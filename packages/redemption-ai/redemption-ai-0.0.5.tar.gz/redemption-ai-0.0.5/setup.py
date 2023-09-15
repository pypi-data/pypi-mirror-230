from setuptools import setup, find_packages

setup(name="redemption-ai",
      version="0.0.5",
      description="AI-powered (OpenAI API) tools for chat-like interactions and personal AI assistance.",
      packages=find_packages(include=["RAI", "RAI.*"]),
      author="Ausar686",
      author_email='glebyushkov@mail.ru',
      install_requires=[
        "numpy==1.25.2",
        "requests==2.31.0",
      ])