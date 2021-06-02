from setuptools import setup, find_packages

requirements = ["casbin==1.0.4", "redis"]

setup(
    name="casbin-redis-watcher",
    version="0.0.1",
    author="Captt-g",
    author_email="1061250120@qq.com",
    description="Casbin role watcher to be used for monitoring updates to policies for PyCasbin",
    url="https://github.com/pycasbin/redis-watcher",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
    ],
)