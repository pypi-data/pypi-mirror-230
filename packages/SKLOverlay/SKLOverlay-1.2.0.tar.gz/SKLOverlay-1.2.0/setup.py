from setuptools import setup, find_packages

with open("ReadMe.md", "r") as f:
    long_des = f.read()

setup(
    name="SKLOverlay",
    version="1.2.0",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    description="SKLearn Classification Interface",
    long_description=long_des,
    long_description_content_type="text/markdown",
    url="https://github.com/laoluadewoye/SKLOverlay",
    author="Laolu Ade",
    author_email="laoluadewoye@gmail.com",
    license="GPLv3",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Information Technology",
        "Natural Language :: English",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    install_requires=[
        "scikit-learn >= 1.3.0",
        "numpy >= 1.24.3",
        "matplotlib >= 3.7.1",
        "pandas >= 1.5.3",
        "openpyxl >= 3.0.10"
    ],
    python_requires=">=3.11",
)

