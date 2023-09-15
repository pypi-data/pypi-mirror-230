# from cyberfametools import __version__
__version__ = "2023.09.14"
import setuptools


setuptools.setup(
    name="cyberfame-tools",
    version=__version__,
    description="Answering interesting cybersecurity questions with graph theory.",
    long_description=open("README.md").read().strip(),
    author="Cyberfame Team",
    author_email="contact@morphysm.com",
    # TODO: Open-source
    # url="https://github.com/kittyandrew/telethon-tgcrypto",
    url=None,
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["aiohttp"],
    # TODO: Open-source
    # license="MIT License",
    license=None,
    keywords="cyberfame tools",
    classifiers=[
        "Development Status :: 4 - Beta",
        # TODO: Open-source
        # "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
)

