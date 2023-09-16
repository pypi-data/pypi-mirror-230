from setuptools import setup, find_packages

setup(
    name='sequelframe',  
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'sqlite3', 
    ],
    author='Sina Mirshahi',
    author_email='sina7th@gmail.com',
    description='SQL interface for CSV and Excel data using SQLite.',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
