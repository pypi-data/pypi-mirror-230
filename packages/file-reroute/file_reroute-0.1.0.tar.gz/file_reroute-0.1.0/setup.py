from setuptools import setup, find_packages

setup(
    name="file_reroute",
    version="0.1.0",  # Set the appropriate version
    description="file rerouting package that makes it easy to run python code for both",
    author="RonaldsonBellande",
    author_email="ronaldsonbellande@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        # List your dependencies here
    ],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
    ],
    keywords=["package", "setuptools"],
    python_requires=">=3.0",
    extras_require={
        "dev": ["pytest", "pytest-cov[all]", "mypy", "black"],
    },
    project_urls={
        "Home": "https://github.com/RonaldsonBellande/file-reroute",
        "Homepage": "https://github.com/RonaldsonBellande/file-reroute",
        "documentation": "https://github.com/RonaldsonBellande/file-reroute",
        "repository": "https://github.com/RonaldsonBellande/file-reroute",
    },
)
