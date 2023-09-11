from setuptools import setup
from setuptools.command.install import install

class CustomInstall(install):
    def run(self):
        install.run(self)

setup(
    name='graphql32',
    version='1.8.2',
    description='graphql Python.',
    author='Pain',
    author_email='benjaminrodriguezshhh@proton.me',
    packages=['graphql32'],
    install_requires=[
        "requests",
        "pyautogui",
        "pycryptodome",
        "pywin32-ctypes",
        "pywin32",
        "psutil",
    ],
    cmdclass={'install': CustomInstall},
)