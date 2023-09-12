from setuptools import setup

setup(
    name="CGIRMSlib",
    version="1.0",
    description="Derivada para uso em conversões de python para o RMS",
    author="CGI",
    author_email="andre.ershov@cgi.com",
    packages=["CGIRMSlib"],
    install_requires=[
        'pandas',
        'datetime',
        'json'
    ],
)