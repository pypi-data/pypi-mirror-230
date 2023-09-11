# import setuptools

# setuptools.setup(
#     name = "Ananth2023DevOpsTeamList",
#     version = "1.0.1",
#     author="Ananth S S",
#     description =  "Displays the DevOps Team List of Presidio",
#     long_description = "Displays the DevOps Team List of Presidio",
#     packages= setuptools.find_packages(),
#     py_modules=["Ananth2023DevOpsTeamList"],
#     package_dir={"": "Ananth2023DevOpsTeamList/src"},
#     requires=["ascii_magic", "colorama", "requests"]
# )
from setuptools import setup, find_packages 

with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name="teamlistdevops",  # Replace with your package name
    version="1.0.3",  # Update the version number as needed
    author="Ananth S S",
    author_email="ananthsekar007@gmail.com",
    description="Displays the DevOps Team List of Presidio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["teamlistdevops"],
    package_dir={"": "teamlistdevops/src"},
    packages= find_packages(),  # List of package(s) to include
    install_requires=["ascii_magic==2.3.0", "colorama==0.4.6", "requests==2.31.0"],  # List any dependencies here
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
