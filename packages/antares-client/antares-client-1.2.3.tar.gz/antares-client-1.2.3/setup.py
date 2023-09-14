import setuptools

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as f:
    install_require = f.read().splitlines()

tests_require = ["coverage==7.2.7", "pytest", "pytest-cov"]

setuptools.setup(
    author="Nicholas Wolf",
    author_email="nwolf@noao.edu",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    description="A light-weight client for receiving alerts from ANTARES.",
    entry_points={"console_scripts": ["antares=antares_client.cli:entry_point"]},
    install_requires=install_require,
    include_package_data=True,
    tests_require=tests_require,
    setup_requires=["pytest-runner"],
    long_description=readme,
    long_description_content_type="text/markdown",
    name="antares-client",
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    url="https://gitlab.com/nsf-noirlab/csdc/antares/client/",
    version="1.2.3",
)
