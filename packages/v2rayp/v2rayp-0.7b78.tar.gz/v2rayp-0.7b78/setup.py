import os

from setuptools import find_packages, setup

from v2rayp.__version__ import __version__


def package_files(directory):
    paths = []
    for path, directories, filenames in os.walk(directory):
        for filename in filenames:
            if ".pyc" in filename:
                continue
            paths.append(os.path.join("..", path, filename))
    return paths


extra_files = package_files("v2rayp")


setup(
    name="v2rayp",  # How you named your package folder (MyLib)
    packages=find_packages(exclude=[".pyc"]),  # Chose the same as "name"
    package_data={"": extra_files},
    version=__version__,  # Start with a small number and increase it with every change you make
    license="MIT",  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description="An efficient and versatile multiplatform project, serving as a v2rayn substitute for Windows, while seamlessly functioning on Mac and Linux, featuring fragmentation support and multi-threaded capabilities.",  # Give a short description about your library
    author="iBlockchain",  # Type in your name
    author_email="iman.minstry@gmail.com",  # Type in your E-Mail
    url="https://github.com/iblockchaincyberchain/v2rayp",  # Provide either the link to your github or to your website
    # download_url="https://github.com/iblockchaincyberchain/V2rayP/releases/download/untagged-56f596c21486f79c4a17/V2rayP.zip",  # I explain this later on
    keywords=[
        "Fragmentation",
        "V2Ray",
        "multiplatform",
        "VPN",
        "Proxy",
    ],  # Keywords that define your package best
    install_requires=[  # I get to this in a second
        "PySimpleGUI",
        "psgtray",
        "requests",
        "pyperclip",
        "psutil",
        "qrcode",
        "setuptools",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",  # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        "Intended Audience :: Developers",  # Define that your audience are developers
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",  # Again, pick a license
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
