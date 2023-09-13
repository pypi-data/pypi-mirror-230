import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyalltools",
    version="2.1.0",
    author="Anupam Kanoongo",
    author_email="programmer.tiak@gmail.com",
    description="Library containing various tools that are required by programmers frequently",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://techinfoak.wixsite.com/tech-info",
    project_urls={
        "Our Website": "https://techinfoak.wixsite.com/tech-info",
        "Our YT Handle": "https://youtube.com/@techinfoak"
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    py_modules=["pyalltools"],
    python_requires=">=3.6"
)
