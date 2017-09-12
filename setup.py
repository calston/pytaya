from setuptools import setup, find_packages


setup(
    name="pytaya",
    version='0.1',
    url='https://github.com/calston/pytaya',
    license='MIT',
    description="A Python library for controlling the RedPitaya remotely",
    author='Colin Alston',
    author_email='colin.alston@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Twisted',
        'autobahn',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
)
