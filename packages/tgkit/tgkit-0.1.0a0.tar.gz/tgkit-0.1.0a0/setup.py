from distutils.core import setup

description = """
Python package to convert Temporal Graphs to Discrete (snapshot-based) or Continuous (event-based) format.
"""

with open("README.md") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

setup(
    name="tgkit",
    version="0.1.0-alpha0",
    description=description.strip(),
    long_description=long_description,
    install_requires=install_requires,
    url="https://github.com/nelsonaloysio/tgkit",
    author="Nelson Aloysio Reis de Almeida Passos",
    long_description_content_type="text/markdown",
    license="MIT",
    keywords=["Network", "Graph", "Dynamic Network", "Temporal Graph"],
    python_requires=">=3.7",
    py_modules=["tgkit"],
    project_urls={
        "Source": "https://github.com/nelsonaloysio/tgkit",
        "Tracker": "https://github.com/nelsonaloysio/tgkit/issues",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
