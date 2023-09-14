from pathlib import Path
from setuptools import setup, find_namespace_packages  # type: ignore[import]


long_description = Path("README.md").read_text()
reqs = Path("requirements.txt").read_text().strip().splitlines()

pkg = "browserexport"
setup(
    name=pkg,
    version="0.4.1",
    url="https://github.com/seanbreckenridge/browserexport",
    author="Sean Breckenridge",
    author_email="seanbrecke@gmail.com",
    description=(
        """save and merge browser history and metadata from different browsers"""
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_namespace_packages(include=[f"{pkg}*"]),
    package_data={pkg: ["py.typed"]},
    python_requires=">=3.8",
    install_requires=reqs,
    extras_require={
        "testing": [
            "pytest",
            "mypy",
            "flake8",
        ],
    },
    keywords="firefox history backup data",
    entry_points={"console_scripts": ["browserexport = browserexport.__main__:cli"]},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
