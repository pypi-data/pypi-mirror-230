import setuptools
import bida

def load_readme():
    with open("README.md", "r", encoding='utf8') as f:
        readme_text = f.read()
    return readme_text

setuptools.setup(
    name="bida",
    version=bida.__version__,
    author="Pengfei Zhou",
    author_email="pfzhou@gmail.com",
    description="bida， 简单、易用、稳定、高效，便于扩展和集成的，大语言模型工程化开发框架",
    long_description=load_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/pfzhou/bida",
    keywords=" ai aigc llm chat completion embedding",
    packages=setuptools.find_packages(include=["bida","bida.*"]),
    package_data={
        "":["*.json", "*.md"], 
    },
    include_package_data=True,
    install_requires=[
        "duckdb==0.8.1",
        "pydantic==1.10.8",
        "python-dotenv==1.0.0",
        "requests==2.28.1",
        "openai==0.27.7",
        "tiktoken==0.4.0",
        "dashscope==1.9.0",
        "zhipuai==1.0.7",
        "sensenova==1.0.5",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    )
