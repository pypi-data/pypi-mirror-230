from setuptools import find_packages, setup


setup(
    name="yjb",
    version="3.4",
    description="Scrape a user's VSCO profile data",
    author="yJb",
    packages=find_packages(),
    install_requires=[
        "tqdm",
        "requests",
        "beautifulsoup4",
    ],
    entry_points="""
        [console_scripts]
        vsco-scraper=vscoscrape:main
    """,
)
