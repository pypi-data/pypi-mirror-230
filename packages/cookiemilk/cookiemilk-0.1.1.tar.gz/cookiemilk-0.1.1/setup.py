import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="cookiemilk",
    version="0.1.1",
    author="Ziqian Wei",
    author_email="weiziqianpsych@outlook.com",
    description="An easy-to-use Python package to process knowledge structure data automatically",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/weiziqianpsych/cookiemilk",
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=['numpy', 'pywebview', 'networkx'],
    packages=setuptools.find_packages(include=['d3v3', 'cookiemilk'])
)
