import setuptools
import glob
import os

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="scripro",
    version="0.0.1",
    python_requires=">=3.8",
    keywords="Single-Cell Gene Regulatory Network Inference using ChIP-seq for Multi-omics",
    url="https://github.com/xuyunfan9991/SCRIPro",
    license="GPL-3.0+",
    packages=setuptools.find_packages(where="scripro"),
    package_dir={"": "scripro"},
    py_modules=[
        os.path.splitext(os.path.basename(path))[0] for path in glob.glob("scripro/*.py")
    ],
    install_requires=requirements,
    include_package_data=True,
    data_files=[("", ["requirements.txt"])],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)