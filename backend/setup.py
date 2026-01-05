from setuptools import setup, find_packages

setup(
    name="ai-teaching-assistant",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-multipart",
        "python-dotenv",
        "google-generativeai",
        "pydantic-settings",
        "pypdf2",
        "python-docx"
    ],
)