from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 3 - Alpha',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Intended Audience :: Developers',
]

setup(
    name='tdstyles',
    version='0.0.8',
    description='A python package which helps in customizing a jupyter notebook with very less effort.',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='https://sprakshith.pythonanywhere.com/',
    author='SP RAKSHITH',
    author_email='rakshith0908@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='matplotlib pyplot seaborn plt sns',
    packages=find_packages(),
    install_requires=['matplotlib', 'IPython', 'seaborn']
)
