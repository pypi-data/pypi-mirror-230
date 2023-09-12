from setuptools import find_packages, setup

DESCIPTION = "library developed on top of aiogram framework that adds bunch of reuseable features"

with open("VERSION", "r") as f:
    VERSION = f.read().strip()

with open("requirements.txt", "r") as requirements_file:
    REQUIREMENTS = requirements_file.readlines()


setup(
    name="axaiogram",
    version=VERSION,
    author="axdjuraev",
    author_email="<axdjuraev@gmail.com>",
    description=DESCIPTION,
    packages=find_packages(),
    install_requires=REQUIREMENTS,
)
