from setuptools import setup, find_packages

setup(name="redemption-ai",
      version="0.0.6",
      description="AI-powered (OpenAI API) tools for chat-like interactions and personal AI assistance.",
      packages=find_packages(include=["RAI", "RAI.*"]),
      author="Ausar686",
      author_email='glebyushkov@mail.ru',
      install_requires=[
        "numpy==1.25.2",
        "pandas==2.1.0",
        "requests==2.31.0",
        "urllib3==2.0.4"
      ])