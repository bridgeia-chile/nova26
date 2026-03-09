from setuptools import setup, find_packages

setup(
    name='nova26',
    version='1.0.0',
    packages=find_packages(),
    py_modules=['main'],
    install_requires=[
        'fastapi',
        'uvicorn',
        'websockets',
        'psutil',
        'python-dotenv',
        'aiohttp',
        'pyyaml'
    ],
    entry_points={
        'console_scripts': [
            'nova26=main:run_cli',
            'nova26-configure=main:run_cli_configure',
        ],
    },
    description='Nova26 Autónomo IA',
    author='BridgeIA',
)
