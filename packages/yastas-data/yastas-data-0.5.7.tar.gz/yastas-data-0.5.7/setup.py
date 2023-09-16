from setuptools import setup, find_packages

def load_requirements():
    with open('requirements.txt') as file:
        return file.read().splitlines()
    
readme = open("./README.md", "r")

setup(
    name='yastas-data',
    version='0.5.7',
    author='Data - Aaron',
    author_email="e-ajuareza@minsait.com",
    description='Paquete distribuible en repositorio de funciones locales Data',
    long_description=readme.read(),
    packages=find_packages(),
    url="https://bitbucket.org/gentera-insumos/data-code",
    keywords=['data', 'big_data', 'data_analytics', 'data_engineer', 'data_science'],
    install_requires=None,
    license="MIT",
    include_package_data=True
)