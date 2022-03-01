import setuptools

with open("README.md", "r", encoding="UTF-8") as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="UTF-8") as f:
    install_requires = f.read().splitlines()

with open("requirements-dev.txt", "r", encoding="UTF-8") as f:
    dev_requires = f.read().splitlines()

setuptools.setup(
    name="dico-api",
    version="0.0.35",
    author="eunwoo1104",
    author_email="sions04@naver.com",
    description="Yet another Discord API wrapper for Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dico-api/dico",
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=install_requires,
    extras_require={"voice": ["PyNaCl"], "dev": dev_requires},
    classifiers=["Programming Language :: Python :: 3"],
)
