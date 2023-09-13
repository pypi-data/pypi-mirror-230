from setuptools import setup, find_packages


setup(
    name='py-map-gen',
    version='0.8',
    author='Ford2003',
    author_email='tommyford28@gmail.com',
    description='A package for generating data for a world with a seed.',
    long_description='',
    packages=find_packages(),
    package_dir={'py-map-gen': 'src'},
    py_modules=['py-map-gen.funcs', 'py-map-gen.mersenne', 'py-map-gen.render'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
