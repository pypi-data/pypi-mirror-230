from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='DesignForPy',
    version='1.0',
    license='MIT License',
    author='Gustavo Martinez',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='gamezinhoo@outlook.com',
    keywords='design',
    description=u'An amazing Design for Python',
    packages=['DesignForPy'],
    install_requires=['pyfiglet', 'colorama'],)