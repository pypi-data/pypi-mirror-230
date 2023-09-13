from setuptools import setup

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setup(name="d4train",
      version="0.0.2.2",
      description="prepare your dataset for finetuning LLMs",
      author="Shuvam Mandal",
      author_email="shuvammandal121@gmail.com",
      packages=["d4train"],
      long_description= long_description,
      long_description_content_type = "text/markdown",
      install_requires = ['datasets','transformers','pandas'],
      
      )