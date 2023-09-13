from setuptools import setup

setup(
    name="cgiteste",
    version="0",
    description="Derivada para uso em conversões de python para o RMS",
    author="CGI",
    author_email="andre.ershov@cgi.com",
    packages=["cgiteste"],
    install_requires=[
        'pandas',
        'datetime',
        'json',
        'numpy'
    ],
)


