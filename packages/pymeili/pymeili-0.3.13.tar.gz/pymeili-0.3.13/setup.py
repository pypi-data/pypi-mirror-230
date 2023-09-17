from setuptools import setup, find_packages, Extension

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

with open("README.md", "r",encoding="utf-8") as fh:
    README_description = fh.read()

with open("CHANGELOG.md", "r",encoding="utf-8") as fh:
    CHANGELOG_description = fh.read()

with open("USAGE.md", "r",encoding="utf-8") as fh:
    USAGE_description = fh.read()

setup(
    name='pymeili',
    version='0.3.13',
    description='a module to beautify your python plot or terminal text.',
    long_description=README_description + '\n\n' + USAGE_description + '\n\n' + CHANGELOG_description,
    long_description_content_type='text/markdown',
    url='',
    author='VVVictorZhou',
    author_email='vichouro@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='beautify',
    packages=find_packages(),
    install_requires=['matplotlib','numpy','seaborn','metpy']
)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# print the message to remind the user to install the module and make sure using the python version >= 3.7
print(bcolors.OKGREEN + "Congratulations! You have successfully installed the pymeili module!" + bcolors.ENDC)
print(bcolors.BOLD + "Please make sure you are using the python version >= 3.7!" + bcolors.ENDC)
print(bcolors.BOLD + "Please make sure you have installed the matplotlib, numpy, seaborn, pathlib, pathlib2 and metpy module!" + bcolors.ENDC)
print(bcolors.BOLD + "\nVisit our website for more information:" + bcolors.OKBLUE + "https://pypi.org/project/pymeili/" + bcolors.ENDC)
