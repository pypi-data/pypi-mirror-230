from setuptools import setup

files = {
    "long_description": "README.md",
    "requirements": "requirements.txt",
    "version": "VERSION",
}

param = {}

for key in files:
    try:
        with open(files[key], "r", encoding="utf-8") as file:
            param[key] = file.read()
    except(OSError, IOError) as exc:
        param[key] = ""

setup(
    name="p_files",
    version=param["version"],
    description="A Python package for file operations.",
    author="Gael",
    author_email="",
    packages=["p_files"],
    install_requires=param["requirements"].split("\n"),
    long_description=param["long_description"],
    long_description_content_type="text/markdown",    
)
