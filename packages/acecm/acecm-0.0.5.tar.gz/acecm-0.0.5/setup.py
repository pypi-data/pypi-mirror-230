import setuptools
import pathlib

component_name = "acecm"

# See https://docs.streamlit.io/library/components/publish
# rm -rf dist/;python3 setup.py sdist bdist_wheel;twine upload dist/*
setuptools.setup(
    name=component_name,
    version="0.0.5",
    author="Cem Bakar",
    author_email="cembakar@gmail.com",
    description="Streamlit component that allows you to do work with cookies",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/cbakar/acecm",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.9",
    install_requires=[
        "streamlit",
    ],
    extras_require={
        "devel": [
            "wheel",
            "pytest==7.4.0",
            "playwright==1.36.0",
            "requests==2.31.0",
            "pytest-playwright-snapshot==1.0",
            "pytest-rerunfailures==12.0",
        ]
    },
    keywords=["Python", "Streamlit", "JavaScript", "Cookies"],
)