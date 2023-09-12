import setuptools

setuptools.setup(
  name="ecs-girvel",
  version="1.0.6",
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
)
