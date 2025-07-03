from setuptools import setup, find_packages

setup(
    name="satellite-chatbot",
    version="0.1.0",
    packages=find_packages(include=['src', 'src.*']),
    install_requires=[
        "streamlit",
        "langgraph",
        "pandas",
        "python-dotenv",
        "pydantic",
        "langchain",
        "langchain-community",
        "langchain-google-genai",
    ],
    author="Sai Pragnaan",
    author_email="pragnaan97@gmail.com",
    description="A chatbot for satellite data extraction and analysis",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    package_dir={"": "."},
    include_package_data=True,
) 