from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="flash_attention_srf",
    version="0.0.7",
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
    install_requires=[
        "scipy",
        "torch"
    ]
)

