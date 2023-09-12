from setuptools import setup, find_packages


info = {
    "name": "xsera",
    "version": "1.1.2",
    "github_page": "https://github.com/xXxCLOTIxXx/xsera",
    "download_link": "https://github.com/xXxCLOTIxXx/amino.api/archive/refs/heads/main.zip",
    "license": "MIT",
    "author": "Xsarz",
    "author_email": "xsarzy@gmail.com",
    "description": "A library to simplify color manipulation, name generation, and more.",
    "long_description": None,
    "long_description_file": "README.md",
    "long_description_content_type": "text/markdown",
    "keywords": [
        "tools",
        "avatars",
        "nicknames",
        "pymino",
        "colors"
        "python",
        "python3",
        "python3.x",
        "xsarz",
        "official",
        "xsera",
        "xsera.py"
    ],

    "install_requires": [
        "numpy",
        "aiohttp",
        "requests",
    ]

}



if info.get("long_description"):
    long_description=info.get("long_description")
else:
    with open(info.get("long_description_file"), "r") as file:
        long_description = file.read()

setup(
    name = info.get("name"),
    version = info.get("version"),
    url = info.get("github_page"),
    download_url = info.get("download_link"),
    license = info.get("license"),
    author = info.get("author"),
    author_email = info.get("author_email"),
    description = info.get("description"),
    long_description = long_description,
    long_description_content_type = info.get("long_description_content_type"),
    keywords = info.get("keywords"),
    install_requires = info.get("install_requires"),
    packages = find_packages(),
)
