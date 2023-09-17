import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cleverminer",
    version="1.0.8",
    author="(C) Copyright 2020 - 2023 Little Big Company, s.r.o.",
    author_email="code@cleverminer.org",
    description="Beyond apriori. Cleverminer is explainable AI (XAI) package for enhanced association rule mining (eARM). It implements the GUHA procedures that generalises apriori and association rules in many ways. Rules are based on categorical data that can be easily visualized and interpreted. Their if-then with probability allows easy deployment by human realized processes. Trully explainable knowledge mining.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://cleverminer.org",
    project_urls={
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Development Status :: 5 - Production/Stable",
	"License :: Free for non-commercial use",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=['progressbar2'],
    python_requires=">=3.8"
)