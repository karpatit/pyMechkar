
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyMechkar-tomask", # Replace with your own username
    version="0.1.3",
    author="Tomas Karpati",
    author_email="karpati@it4biotech.com",
    description="Useful Tools for Scientific Research",
    long_description="Utilities that help researchers in various phases of their research work. This package offer a function that automate the exploratory data analysis, a function for the generation of Table 1 (required on many epidemiological papers) which can be exported to excel. There is also a function for generation of a forestplot with a table and relative risks or odds ratios that can be used for publication. Additionally, there is a function that generates train/test random partitions used for model evaluation that checks for the balance of the partitions.",
    long_description_content_type="text/markdown",
    url="https://github.com/karpatit/pyMechkar",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)