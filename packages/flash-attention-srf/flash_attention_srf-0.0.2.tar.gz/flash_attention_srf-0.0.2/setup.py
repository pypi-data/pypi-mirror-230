import subprocess
import sys

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Install packages using pip to leverage --extra-index-url
def install_with_extra_index():
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", 
         "--extra-index-url", 
         "https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/Triton-Nightly/pypi/simple/",
         "triton-nightly", "scipy", "torch"]
    )

install_with_extra_index()

setup(
    name="flash_attention_srf",
    version="0.0.2",
    author="Alexander Levenston",
    author_email="alexlevenston2021@gmail.com",
    description="Softmax-less Flash Attention w/ SRFs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexjlevenston/flash-attention-srf",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

