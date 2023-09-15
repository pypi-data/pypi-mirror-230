from setuptools import setup

setup(
    name='infoFlib',
    version='1.0.1',
    description='Biblioteca para registro de usuários, livros, locação e devolução',
    long_description='Biblioteca para registro de usuários, livros, locação e devolução',
    author='Lursy',
    author_email='matheus.cruz@alunos.ifsuldeminas.edu.br',
    url='https://github.com/Lursy7/infoFlib',
    packages=['infoFlib'],
    install_requires=[
        "pyfiglet==0.8.post1"
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)