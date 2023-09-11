import setuptools

with open("README.md", "r", encoding='utf8') as f:
    long_description = f.read()

setuptools.setup(
    name="bida",
    version="0.9.2",
    author="Pengfei Zhou",
    author_email="pfzhou@gmail.com",
    description="bida， 简单、易用、稳定、高效，便于扩展和集成的，大语言模型工程化开发框架",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pfzhou/bida",
    keywords="llm chat completion embedding ai aigc",
    packages=setuptools.find_packages(include=["bida","bida.*"],  exclude=["test","test.*"]),
    package_data={
        "":["*.json"], 
    },
    install_requires=[
        "duckdb==0.8.1",
        "pydantic==1.10.8",
        "python-dotenv==1.0.0",
        "Requests==2.28.1",
        "openai==0.27.7",
        "tiktoken==0.4.0",
        "dashscope==1.3.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    )
