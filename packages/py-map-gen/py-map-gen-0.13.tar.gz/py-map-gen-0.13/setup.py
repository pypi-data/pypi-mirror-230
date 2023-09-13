from setuptools import setup, find_packages


setup(
    name='py-map-gen',
    version='0.13',
    author='Ford2003',
    author_email='tommyford28@gmail.com',
    description='A package for generating data for a world with a seed.',
    long_description='',
    packages=find_packages(where='src', include=['py-map-gen']),
    include_package_data=True,
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=["numpy", "matplotlib"]
)
