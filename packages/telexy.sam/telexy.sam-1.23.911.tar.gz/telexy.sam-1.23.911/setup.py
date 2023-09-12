#To build/publish, use following commands
#python3 -m build - for build
#python3 -m twine upload dist/* - for publish
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="telexy.sam",                     # This is the name of the package
    version="1.23.911",                        # The initial release version
    author="Telexy",                     # Full name of the author
    author_email="support@telexy.com", # Full email of author
    description="SAM Inference service",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.10',                # Minimum version requirement of the package
    py_modules=["sam"],             # Name of the python package
    install_requires=['telexy.mars', "opencv-python", 'torch', 'torchvision', 'numpy', 'pycocotools'],                     # Install other dependencies if any
)





