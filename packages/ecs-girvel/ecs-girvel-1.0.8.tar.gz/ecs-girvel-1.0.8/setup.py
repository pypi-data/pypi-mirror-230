from pathlib import Path

import setuptools

setuptools.setup(
  name="ecs-girvel",
  version="1.0.8",
  author="Nikita Girvel Dobrynin",
  author_email="widauka@ya.ru",
  description="Annotation-based asynchronous ECS library",
  url="https://github.com/girvel/ecs",
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  package_dir={"": "."},
  packages=["ecs"],
  python_requires=">=3.6",
  long_description=(Path(__file__).parent / "README.md").read_text(),
  long_description_content_type='text/markdown',
)
