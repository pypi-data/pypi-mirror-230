import setuptools
 
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
 
setuptools.setup(
    name="KPTE",
    version="1.0.0",
    author="Kaixin",
    include_package_data = True,
    entry_points = {'console_scripts': [
        'KPTE = KPTE.KPTE:KPTE',
    ]},
    author_email="kaixin168KX@163.com",
    description="Used to package the py file as an exe file.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
