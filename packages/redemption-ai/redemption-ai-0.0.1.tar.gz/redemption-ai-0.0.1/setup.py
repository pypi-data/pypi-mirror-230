from setuptools import setup, find_packages

with open("RAI/requirements.txt", "r", encoding="utf-8") as file:
	requirements = file.readlines()
	requirements = [elem.strip() for elem in requirements]

setup(name="redemption-ai",
      version="0.0.1",
      description="AI-powered (OpenAI API) tools for chat-like interactions and personal AI assistance.",
      packages=find_packages(include=["RAI", "RAI.*"]),
      author="Ausar686",
      author_email='glebyushkov@mail.ru',
      install_requires=requirements)