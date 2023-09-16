import os

from setuptools import setup, find_packages

if os.path.exists("requirements.txt"):
    requires = open("requirements.txt", "r").readlines()
else:
    print(os.listdir(os.getcwd()))
    requires = open("./src/workflow_keeper.egg-info/requires.txt", "r").readlines()
print("#-------------------    ", str(os.listdir("./")))
setup(
    name="workflow-keeper",
    version="0.0.1",
    author="davidliyutong",
    author_email="davidliyutong@sjtu.edu.cn",
    description="Driver for Arizona USB Pressure Sensor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    install_requires=requires,
    test_requires=[
        "requests",
        "tqdm",
    ],
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown"
)
