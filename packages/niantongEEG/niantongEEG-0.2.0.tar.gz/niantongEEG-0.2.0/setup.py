from setuptools import setup, find_packages

setup(
    name="niantongEEG",
    version="0.2.0",
    packages=find_packages(),
    package_data={
        "niantongEEG": [
            "py36/eCon.pyd",
            "py37/eCon.pyd",
            "py38/eCon.pyd",
            "py39/eCon.pyd",
            "py310/eCon.pyd",
            "py311/eCon.pyd"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11"
    ],
)
