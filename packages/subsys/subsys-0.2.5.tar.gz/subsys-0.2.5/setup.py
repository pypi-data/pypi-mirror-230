from setuptools import setup, find_packages

setup(
    name="subsys",
    version="0.2.5",
    author = "Patrick Mushimiye",
    author_email= "patrick.mushimiye@amalitech.org",
    description='cli for assignment submission',
    py_modules=["main", "calc_hash"],
    packages= find_packages(),
    install_requires=[
        "Click",
    ],
    entry_points={
        "console_scripts": [
            "subsys = main:app",
        ],
    },
)
