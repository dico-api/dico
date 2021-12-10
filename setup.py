import setuptools

with open("README.md", "r", encoding="UTF-8") as f:
    long_description = f.read()

setuptools.setup(
    name="dico-api",
    version="0.0.27",
    author="eunwoo1104",
    author_email="sions04@naver.com",
    description="Yet another Discord API wrapper for Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dico-api/dico",
    packages=setuptools.find_packages(),
    python_requires='>=3.7',
    install_requires=["aiohttp", "requests"],
    classifiers=[
        "Programming Language :: Python :: 3"
    ]
)
