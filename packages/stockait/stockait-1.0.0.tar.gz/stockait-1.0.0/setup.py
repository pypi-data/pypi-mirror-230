import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="stockait", # Replace with your own username
    version="1.0.0",
    author="Eunsu Kim, Sieun Kim, Eunji Cha, Yujin Cha",
    author_email="stockai2023@gmail.com",
    description="Make your stock investment smarter, join StockAit!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stockAI-py/stockait",
    install_requires=['numpy', 'pandas', 'tqdm', 'yfinance', 'xgboost', 'lightgbm', 'ta', 'matplotlib', 'sklearn', 'seaborn', 'boto3', 'sqlalchemy', 'pymysql'],
    packages=setuptools.find_packages(include=["stockait", "stockait.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
