import setuptools                                    

with open("README", "r") as fh:
    long_description = fh.read() 

setuptools.setup(
    name="rsmmus", # Replace with your own PyPI username(id)
    version="0.0.1",
    author="Joy",
    author_email="joyhhh@outlook.kr",
    description="RSM MUS Sampling Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/joy-hhh/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
],
python_requires='>=3.9',
)       

