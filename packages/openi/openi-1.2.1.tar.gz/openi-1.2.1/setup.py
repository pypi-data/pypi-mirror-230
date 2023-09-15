from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="openi",
    version="1.2.1",
    description="A package for openi pypi",
    package_dir={"": "src"},
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://openi.pcl.ac.cn/OpenIOSSG/openi-pypi",
    author="chenzh05",
    author_email="chenzh.ds@outlook.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": ["openi = openi.cli:main"]},
    install_requires=["requests", "tqdm"],
    python_requires=">=3.6",
)
