from mars import *
import cherrypy
import os
import cv2
from datetime import datetime
import threading
from Telexy.DS import VirtualFileAccessor
import torch
import numpy as np
from segment_anything import sam_model_registry, SamPredictor
from pycocotools import mask as mask_utils
import math



@cherrypy.tools.allow(methods=['POST'])
@cherrypy.tools.json_out()
class SamPlugin(MarsPluginBase):

    #sam model uid
    samModelUid = 'FBF5D932-4A68-4998-B1DF-48069A470B4E'
    samModelId = 0

    # keeps track of cached images
    imageCacheDictionary = {}
    imageCacheDictionaryLock = threading.Lock()
    # keeps track of tracked image predictors
    predictorCacheDictionary = {}
    predictorCacheDictionaryLock = threading.Lock()

    device = "cpu"
    sam = None

    def __init__(self):
        """default constructor"""
        super().__init__("sam")
        if torch.cuda.is_available():
            device = "cuda"

        # verify existance of any model and check for updated models
        self.modelSyncThread = Thread(target=self.syncModels)
        self.modelSyncThread.start()
        self.populateImagesFromDisk()
   
    def syncModels(self):
        """Synchronize models"""
        # retrieve metadata file (if exists) and read out latest model version id
        ds = ModelApi()
        # sam model active id 
        activeVersionId = int(ds.activeVersion(self.samModelUid)['Id'])

        try:
            # check if there is a file starting with sam model uid
            # if there are and they are not of the version we want, delete them
            localVersion = self.samModelId
            for f in os.listdir(self.getHomeDirectory()):
                if f.startswith(self.samModelUid):
                    localVersion = int(f.split('_')[1])
                    if(localVersion != activeVersionId):
                        self.deleteFile(self.getModelPath(f))
                    else:
                        self.samModelId = localVersion
                    

            # if the active version is not the same as the one we have on disk
            if(activeVersionId != self.samModelId):
                # download file
                v = ds.getModelFile(activeVersionId)
                self.samModelId = activeVersionId
                f = open(self.getModelPath(self.samModelFileName()) , "wb")
                f.write(v)
                f.close()

            self.sam = sam_model_registry["vit_h"](self.getModelPath(self.samModelFileName()))
            self.sam.to(device = self.device)
        except:
            print("Error occurred")

    def populateImagesFromDisk(self):
        """populates images into cache from disk"""
        files = os.listdir(self.getImagesFolder())
        now = datetime.utcnow()
        self.imageCacheDictionaryLock.acquire()
        for f in files:
            self.imageCacheDictionary[f] = now

        self.imageCacheDictionaryLock.release()
        # start the timer to manage files
        tenMins = 60 * 10
        self.cacheThread = marsthreading.RecursiveTimer(tenMins, self.cleanupImages)
        self.cacheThread.start()

    def cleanupImages(self):
        """Cleans up images on a timer"""
        self.imageCacheDictionaryLock.acquire()
        
        fiveMins = 60*5
        now = datetime.utcnow()
        toDelete = []
        for k in self.imageCacheDictionary.keys():
            diff = (now - self.imageCacheDictionary[k]).total_seconds()
            if(diff > fiveMins):
                # delete file and delete record
                self.deleteFile(self.getImagePath(k))
                toDelete.append(k)

        self.predictorCacheDictionaryLock.acquire()        
        for k in toDelete:
            self.imageCacheDictionary.pop(k)
            if self.predictorCacheDictionary.get(k) != None:
                self.predictorCacheDictionary.pop(k)
        self.predictorCacheDictionaryLock.release()
        self.imageCacheDictionaryLock.release()

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def predict(self):
        self.modelSyncThread.join()
        inferenceData = cherrypy.request.json

        predictor = self.getImagePredictor(inferenceData['Key'])
        masks, scores, logits = predictor.predict(point_coords=np.array([[inferenceData['Coordinate']['x'], inferenceData['Coordinate']['y']]]),
                                                  point_labels=np.array([1]), 
                                                  multimask_output=False)


       
        rv = []
        for mask in masks:
            if isinstance(mask, np.ndarray) and mask.dtype == bool:
                mask = mask_utils.decode(mask_utils.encode(np.asfortranarray(mask)))

            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            contours = [np.squeeze(contour) for contour in contours]
            contours = [np.atleast_2d(contour) for contour in contours]


            # find largest contour where the point lies
            contour = None
            area = 0
            maxSide = 0
            for object in contours:
                minX = min(f[0] for f in object)
                minY = min(f[1] for f in object)
                maxY = max(f[1] for f in object)
                maxX = max(f[0] for f in object)
                a2 = (maxX - minX) * (maxY - minY)
                if area < a2 and minX <= inferenceData['Coordinate']['x'] <= maxX and minY <= inferenceData['Coordinate']['y'] <= maxY:
                    contour = object
                    area = a2
                    maxSide = max(maxX - minX, maxY - minY)

            # format masks and make them a coordinate system
            for c in contour:
                rv.append({'x' : int(c[0]), 'y': int(c[1])})

            rv = self.removeClosePoints(self.removeSameSlopePoints(rv), maxSide * 0.15)
        return rv


    def calculateSlope(self, p1, p2):
        """Calculates line slope"""
        if p2['x'] - p1['x'] == 0:
            return float('inf')
        return (p2['y'] - p1['y'])/ (p2['x'] - p1['x'])

    def removeSameSlopePoints(self, points):
        """Remove middle points on the same slope"""
        if len(points)  <= 2:
            return points
        
        result = [points[0]]
        prevSlope = None
        for i in range(1, len(points) - 1):
            currSlope = self.calculateSlope(points[i - 1], points[i+1])
            if currSlope != prevSlope:
                result.append(points[i])
                prevSlope = currSlope

        result.append(points[-1])
        return result
    
    def calculateDistsance(self, p1, p2):
        """calculate distance between points"""
        return math.sqrt((p2['x'] - p1['x']) ** 2 + (p2['y'] - p1['y'])**2)

    def removeClosePoints(self, points, threshold):
        """Remove points that are too close by"""
        if len(points) <= 1:
            return points
        
        existingPoint = points[0]
        result = [existingPoint]

        for i in range(1, len(points)):
            isFarAway = self.calculateDistsance(existingPoint, points[i]) >= threshold
            if isFarAway:
                result.append(points[i])
                existingPoint = points[i]

        return result

    def getImagePredictor(self, key):
        """retrieves image predictor"""
        self.predictorCacheDictionaryLock.acquire()
        predictorWrapper = self.predictorCacheDictionary.get(key)
        # start an async thread to create the predictor
        if(predictorWrapper == None):
            predictorWrapper = {}
            t = Thread(target=self.createImagePredictor, args=(key, predictorWrapper))
            t.start()
            predictorWrapper['Thread']=t
            self.predictorCacheDictionary[key] = predictorWrapper
        self.predictorCacheDictionaryLock.release()

        predictorWrapper['Thread'].join()

        #re - read the actual predictor value
        self.predictorCacheDictionaryLock.acquire()
        predictorWrapper = self.predictorCacheDictionary.get(key)
        self.predictorCacheDictionaryLock.release()
        return predictorWrapper['Predictor']

    def createImagePredictor(self, key, dict):
        """Create image predictor"""
        predictor = SamPredictor(self.sam)
        predictor.set_image(self.getImage(key))
        dict['Predictor'] = predictor

    def getImage(self, key):
        """Retrieves image"""
        imgPath = self.getImagePath(key) 
        if(self.imageExists(key) == False):
            faApi = VirtualFileAccessor.VirtualFileAccessApi()
            file = faApi.getFile(key)
            f = open(imgPath, "wb")
            f.write(file)
            f.close()

        # update or create cache record
        self.imageCacheDictionaryLock.acquire()
        self.imageCacheDictionary[key] = datetime.utcnow()
        self.imageCacheDictionaryLock.release()

        return cv2.cvtColor(cv2.imread(imgPath), cv2.COLOR_BGR2RGB)


    def getImagesFolder(self):
        """retrieves images folder"""
        imagesFolder = self.getHomeDirectory() + "/images"
        if(os.path.exists(imagesFolder) == False):
            os.makedirs(imagesFolder)
        return imagesFolder

    def getImagePath(self, key):
        """Gets image path"""
        return self.getImagesFolder() + "/" + key

    def imageExists(self, key):
        """reeturns if image exists"""
        return self.fileExists(self.getImagePath(key))
    
    def getModelPath(self, key):
        """gets file path"""
        return self.getHomeDirectory() + "/" + key

    def samModelFileName(self):
        """Gets sam model file name"""
        return self.samModelUid + "_" + str(self.samModelId)

    def getFile(self, path):
        """retrieves file via key"""
        return open(path)

    def fileExists(self, path):
        return os.path.exists(path)

    def deleteFile(self, path):
        #deletes file with given key
        if self.fileExists(path):
            os.remove(path)

    def close(self):
        """close threads when application is killed"""
        super().close()
        if self.cacheThread != None:
            self.cacheThread.cancel()

    def configuration(self):
        return {
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json')]
        }