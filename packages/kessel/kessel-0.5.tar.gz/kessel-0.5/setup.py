import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requirements = [
    "cffi==1.15.1",
    "cryptography==41.0.3",
    "gunicorn==21.2.0",
    "Jinja2==3.1.2",
    "MarkupSafe==2.1.3",
    "packaging==23.1",
    "pkg_resources==0.0.0",
    "pycparser==2.21",
    "PyJWT==2.8.0",
]

setuptools.setup(
    name="kessel",
    version="0.5",
    author="mkirc",
    author_email="m.p.kirchner@gmx.de",
    description="a minimal wsgi framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Source Files": "https://github.com/mkirc/kessel"
    },
    install_requires=requirements,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
)

