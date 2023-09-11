from pathlib import Path
from setuptools import setup, find_packages

long_description = Path("README.md").read_text()
reqs = Path("requirements.txt").read_text().strip().splitlines()

pkg = "scramble_history"
setup(
    name=pkg,
    version="0.1.15",
    url="https://github.com/seanbreckenridge/scramble-history",
    author="Sean Breckenridge",
    author_email="seanbrecke@gmail.com",
    description=("""parses scramble history from cstimer.net and other sources"""),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(include=[pkg]),
    install_requires=reqs,
    package_data={pkg: ["py.typed"]},
    zip_safe=False,
    keywords="cubing data",
    python_requires=">=3.8",
    entry_points={
        "console_scripts": ["scramble_history = scramble_history.__main__:main"]
    },
    extras_require={
        "optional": ["orjson", "seaborn"],
        "testing": [
            "pytest",
            "mypy",
            "flake8",
        ],
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
