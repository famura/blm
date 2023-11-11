import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

setup(
    # This is the name of your project as to be published at PyPI: https://pypi.org/project/sampleproject/
    name="blm",  # https://packaging.python.org/specifications/core-metadata/#name
    version="1.1",  # https://www.python.org/dev/peps/pep-0440/
    description="A simple model to describe the backlash effect in physics simulations",
    long_description=(here / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/famura/blm",
    author="Fabio Muratore",
    author_email="fabio.muratore@famura.net",
    classifiers=[  # list of valid classifiers, see https://pypi.org/classifiers/
        "License :: OSI Approved :: MIT License",
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="backlash, simulation, physics, modeling",
    packages=find_packages(include=["blm"], exclude=["tests"]),
    python_requires=">=3.7, <4",
    # List mandatory groups of dependencies, installed via `pip install -e .[dev]`
    install_requires=[  # https://packaging.python.org/en/latest/requirements.html
        "numpy",
        "tabulate",
        "tqdm",
    ],
    # List additional groups of dependencies, installed via `pip install -e .[dev]`
    extras_require={
        "dev": ["black", "isort", "matplotlib", "pytest", "pytest-cov"],
    },
    project_urls={
        "Source": "https://github.com/famura/blm",
        "Bug Reports": "https://github.com/famura/blm/issues",
        # 'Funding': 'https://donate.pypi.org',
    },
    # Data files outside of the package http://docs.python.org/distutils/setupscript.html#installing-additional-files
    # data_files=[('my_data', ['data/data_file'])],
)
