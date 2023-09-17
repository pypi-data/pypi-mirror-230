from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 1 - Planning',
    'Intended Audience :: Developers',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.10'
]

setup(
    name='alexeygameframework',
    version='0.0.14',
    description='A simple game framework designed with pygame',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='Alexey Kazinich',
    author_email='',
    license='MIT',
    classifiers=classifiers,
    keywords='game',
    packages=find_packages(),
    install_requires=['pygame'],
    
)