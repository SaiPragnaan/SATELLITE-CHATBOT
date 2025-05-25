from setuptools import setup, find_packages

setup(
    name="satellite-chatbot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit==1.31.1",
        "langgraph==0.0.19",
        "beautifulsoup4==4.12.3",
        "requests==2.31.0",
        "pandas==2.1.4",
        "python-dotenv==1.0.0",
        "pydantic==2.6.1",
        "aiohttp==3.9.3",
        "lxml==5.1.0",
    ],
    author="Sai Pragnaan",
    author_email="pragnaan97@gmail.com",
    description="A chatbot for satellite data extraction and analysis",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
) 