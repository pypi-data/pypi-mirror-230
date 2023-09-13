from setuptools import setup, find_packages

setup(
    name='estatbr',
    version='0.1.1',
    description="Uma biblioteca para Mudar sua experiencia em estatistica no python",
    author='Samuel Bidjory',
    author_email='bidjorys@gmail.com',
    url='https://github.com/Anybosoft',
    packages=find_packages(),  # Isso incluirá automaticamente todos os pacotes do seu projeto
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib",
        "sympy",
        "mpmath",
        # Lista de dependências, por exemplo: 'numpy>=1.0'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
