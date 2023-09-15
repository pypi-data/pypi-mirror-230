from setuptools import setup

setup(
    name="RMSPYlib",
    version="1.3",
    description="Derivada para uso em conversões de python para o RMS",
    author="CGI",
    author_email="andre.ershov@cgi.com",
    packages=["RMSPYlib"],
    install_requires=[
        'pandas',
        'datetime',
        'numpy',
        'requests'
    ],
)
