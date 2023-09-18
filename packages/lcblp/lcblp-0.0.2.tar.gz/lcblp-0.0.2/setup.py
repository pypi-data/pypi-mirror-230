import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lcblp", ## 소문자 영단어
    version="0.0.2", ##
    author="Lee Changbok", ## ex) Sunkyeong Lee
    author_email="lcvrjqnr@gmail.com", ##
    description="LAON PEOPLE", ##
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/halfTaim/lcblp.git", ##
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)