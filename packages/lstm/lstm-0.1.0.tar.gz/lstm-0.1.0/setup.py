import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


reqs = []

extras_require = {
    "test": ["pytest~=7.0", "pytest-cov~=3.0", "coverage-badge~=1.0"],
    "hook": ["pre-commit~=3.0"],
    "lint": ["black~=23.1", "ruff~=0.0.272"],
    "docs": ["mkdocs-material~=9.0", "mkdocstrings[python]~=0.18", "mike~=1.1"],
}
extras_require["all"] = sum(extras_require.values(), [])
extras_require["dev"] = (
    extras_require["test"] + extras_require["hook"] + extras_require["lint"] + extras_require["docs"]
)

setuptools.setup(
    name="lstm",
    version="0.1.0",
    author="Nicolas REMOND",
    author_email="remondnicola@gmail.com",
    description="Pytorch implementation of LSTM variants",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/astariul/lstm",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=reqs,
    extras_require=extras_require,
)
