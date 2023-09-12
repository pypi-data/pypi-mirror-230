import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="FluViewer",
    version="0.1.9",
    author="Kevin Kuchinski",
    author_email="kevin.kuchinski@bccdc.ca",
    description="An automated, host and subtype agnostic tool for generating influenza A virus genome sequences from FASTQ data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KevinKuchinski/FluViewer",
    project_urls={
        "Bug Tracker": "https://github.com/KevinKuchinski/FluViewer/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8.5",
    entry_points={
    'console_scripts': [
        'FluViewer = FluViewer.FluViewer_v_0_1_9:main',
    ],
    }
)
