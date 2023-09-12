import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="WorldBrowser",
    version="2023.9.1",
    author="anzechannel",
    author_email="348834851@qq.com",
    description="A Browser that can browse the global interesting movies、pictures、news and so on。",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anzechannel/WorldBrowser",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
