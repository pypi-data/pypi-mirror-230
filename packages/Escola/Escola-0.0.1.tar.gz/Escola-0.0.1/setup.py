from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='Escola',
    version='0.0.1',
    license='MIT License',
    author='Larissa de Jesus Vieira',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='lalasarandi@gmail.com',
    keywords='escola',
    description=u'Projeto OO',
    packages=['my_library'],
    install_requires=['requests'],)