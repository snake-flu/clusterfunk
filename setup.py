from setuptools import setup, find_packages

setup(
        name="clusterfunk",
        version="0.0.2",
        packages=find_packages(),
        url="https://github.com/cov-ert/clusterfunk",
        license="MIT",
        entry_points={"console_scripts": ["clusterfunk = clusterfunk.__main__:main"]},
        test_suite="nose.collector",
        tests_require=["nose >= 1.3"],
        install_requires=[
                "biopython>=1.70",
                "dendropy>=4.4.0",
                "chardet>=3.0.4",
                "scipy>=1.4.1"
        ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
    ],
)
