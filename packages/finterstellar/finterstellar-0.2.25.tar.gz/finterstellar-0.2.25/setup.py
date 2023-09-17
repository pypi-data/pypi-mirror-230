import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="finterstellar",
    version="0.2.25",
    author="finterstellar",
    author_email="finterstellar@naver.com",
    description="Quantitative analysis tools for investment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/finterstellar/library",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'lxml>=4.2.6',
        'numpy>=1.19.3',
        'pandas>=1.1.4',
        'requests>=2.23.0',
    ],
    python_requires='>=3.5',
)