import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kessel",
    version="0.4",
    author="mkirc",
    author_email="m.p.kirchner@gmx.de",
    description="a minimal wsgi framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Source Files": "https://github.com/mkirc/kessel"
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
)

