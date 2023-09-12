from setuptools import setup, find_packages

setup(
    name='plack',      
    version='1.0.0',          
    packages=find_packages(),
    install_requires=[
        'click',              # List any dependencies here
        # Add other dependencies if needed
    ],
    entry_points={
        'console_scripts': [
            'plack = plack:Plack.start',  # Replace with your module and CLI function
        ],
    },
)
