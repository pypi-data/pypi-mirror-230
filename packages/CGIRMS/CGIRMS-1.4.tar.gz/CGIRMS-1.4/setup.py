from setuptools import setup

setup(
    name="CGIRMS",
    version="1.4",
    description="Derivada para uso em conversões de python para o RMS",
    author="CGI",
    author_email="andre.ershov@cgi.com",
    packages=["CGIRMS"],
    install_requires=[
        'pandas',
        'datetime',
        'numpy'
    ],
)

