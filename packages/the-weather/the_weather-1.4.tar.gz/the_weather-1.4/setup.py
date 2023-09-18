import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="the_weather",
    version="1.4",
    author="Michael Mondoro",
    author_email="michaelmondoro@gmail.com",
    description="Package for getting weather data based on a zipcode",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/michaelMondoro/the_weather",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[],
    python_requires='>=3.7',
)
