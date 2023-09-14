from setuptools import setup

setup(
    name="onlinecheckwriter-quickpay",
    version="1.03",
    description="A Python package for handling online check payments",
    author="Onlinecheckwriter",
    author_email="developer@zilmoney.com",
    packages=["onlinecheckwriter-quickpay"],
    install_requires=["requests"],  # Add any dependencies here
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
