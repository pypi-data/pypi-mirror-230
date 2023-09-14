from setuptools import setup

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setup(name="yDataPrep",
      version="0.0.1.0",
      description="prepare your dataset for finetuning LLMs",
      author="Shuvam Mandal",
      author_email="shuvammandal121@gmail.com",
      packages=["yDataPrep"],
      long_description= long_description,
      long_description_content_type = "text/markdown",
      install_requires = ['datasets','transformers','pandas','tensorflow'],
      
      )