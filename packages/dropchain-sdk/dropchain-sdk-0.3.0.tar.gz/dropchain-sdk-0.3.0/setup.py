import setuptools
  
with open("README.md", "r") as fh:
    description = fh.read()
  
setuptools.setup(
    name="dropchain-sdk",
    version="0.3.0",
    author="DropChain Inc",
    author_email="carter@dropchain.network",
    packages=["dropchain_sdk"],
    description="Build robust web3 applications seamlessly using Python with existing frameworks.",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/cRazink/py_dropchain_sdk",
    license='MIT',
    python_requires='>=3.8',
    install_requires=["requests"]
)