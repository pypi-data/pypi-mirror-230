from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="smartschool3",
    version="1.0.7",
    description="A third-party API for Smartschool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="bimsie20",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7, <4",
    install_requires=["requests", "beautifulsoup4"]
)