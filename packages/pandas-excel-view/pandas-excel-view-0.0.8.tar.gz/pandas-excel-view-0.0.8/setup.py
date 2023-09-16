import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", 'r') as fh:
    requirements = fh.read().split('\n')

setuptools.setup(
    name="pandas-excel-view",
    version="0.0.8",
    author="Wilian Silva",
    author_email="wilianzilv@gmail.com",
    description="Visualize Pandas DataFrames in Excel",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wilianzilv/pandas_excel_view",
    packages=setuptools.find_packages(),
    python_requires='>=3.5.2',
    install_requires=requirements
)
