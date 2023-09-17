from setuptools import setup

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setup(name="yInference",
      version="0.0.1.1",
      description="Inference your Fine tuned LLM",
      author="Shuvam Mandal",
      author_email="shuvammandal121@gmail.com",
      packages=["yInference"],
      long_description= long_description,
      long_description_content_type = "text/markdown",
      install_requires = ['transformers','pandas','tensorflow'],
      
      )