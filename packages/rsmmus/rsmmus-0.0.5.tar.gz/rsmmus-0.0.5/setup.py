import setuptools

with open("README", "r") as fh:
    long_description = fh.read() 

setuptools.setup(
    name="rsmmus",
    version="0.0.5",
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
	install_requires=[
		"numpy",
		"pandas",
		"xlsxwriter",
		"openpyxl",
	],
python_requires='>=3.8',
)

