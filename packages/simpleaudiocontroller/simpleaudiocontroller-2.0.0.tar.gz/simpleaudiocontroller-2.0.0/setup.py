from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()
setup(
    name="simpleaudiocontroller",
    version="2.0.0",
    description="Simple interface for controlling audio devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Anderson Araújo",
    author_email="andersondev.ssh@gmail.com",
    url="https://github.com/andersonssh/simpleaudiocontroller",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
    python_requires=">=3.7",
    install_requires=["setuptools>=61.0"],
    extras_require={
        "dev": [
            "pytest>=6.2.5",
            "black",
            "isort"
        ]
    },
    packages=["simpleaudiocontroller"],
    # entry_points={
    #     "console_scripts": [
    #         "simpleaudiocontroller = simpleaudiocontroller.main:main"
    #     ]
    # },
)
