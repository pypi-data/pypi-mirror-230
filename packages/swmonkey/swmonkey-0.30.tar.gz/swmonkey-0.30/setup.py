from setuptools import setup, find_packages
import io

with open('swmonkey/main.py', encoding='utf-8') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip("'")
            break

print('version: ', version)
setup(
    name='swmonkey',
    version=version,
    packages=find_packages(),
    author='Li Saifei',
    author_email='waltermitty121906@gmail.com',
    description='A tool for monkey test on Linux GUI',
    entry_points={
        'console_scripts': [
            'swmonkey = swmonkey.main:swmonkey',
            'swmonkey_runner = swmonkey.runner:main'
        ]
    },
    install_requires=[
        'pyautogui',
        'psutil',
    ]
)
