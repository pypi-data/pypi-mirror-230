from setuptools import setup, find_packages

setup(name="redemption-ai",
      version="0.0.3",
      description="AI-powered (OpenAI API) tools for chat-like interactions and personal AI assistance.",
      packages=find_packages(include=["RAI", "RAI.*"]),
      author="Ausar686",
      author_email='glebyushkov@mail.ru',
      install_requires=[
        "numpy==1.25.2",
        "orjson==3.9.7",
        "pandas==2.1.0",
        "pydantic==2.3.0",
        "requests==2.31.0",
        "tiktoken==0.5.0"
      ])