#!/usr/bin/env python

"""The setup script."""

import os.path
from setuptools import setup, find_packages
from setuptools.command.install_scripts import install_scripts
from setuptools.command.develop import develop

from pipenv.project import Project
try:
    from pipenv.utils.dependencies import convert_deps_to_pip
except ImportError:
    from pipenv.utils import convert_deps_to_pip


pfile = Project(chdir=False).parsed_pipfile
requirements = convert_deps_to_pip(pfile['packages'], r=False)
test_requirements = convert_deps_to_pip(pfile['dev-packages'], r=False)

hardlink_names = ("clls", "cllls", "cals", "calls", "callls", "csls", "cslls", "csllls", "csals", "csalls", "csallls")


class CustomInstallScriptsCommand(install_scripts):
    """Customized setuptools install_scripts command - installs hard links to 'cls'."""
    def run(self):
        ## print("Hello, developer, how are you? :)")
        ## bs_cmd = self.get_finalized_command('build_scripts')
        inst_cmd = self.get_finalized_command('install_scripts')
        install_scripts.run(self)
        ## print(bs_cmd.__dict__)
        ## print(inst_cmd.__dict__)

        #post-processing code
        for name in hardlink_names:
            target = os.path.join(inst_cmd.install_dir, name)
            ## self.copy_file(os.path.join(bs_cmd.build_dir, "cls"), target)
            self.copy_file(os.path.join(inst_cmd.install_dir, "cls"), target, link='hard')
            self.outfiles.append(target)


class CustomDevelopCommand(develop):
    """Customized setuptools develop command - installs hard links to 'cls'."""
    def run(self):
        ## print("Hello, developer, how are you? :)")
        inst_cmd = self.get_finalized_command('develop')
        develop.run(self)
        ## print(inst_cmd.__dict__)

        #post-processing code
        for name in hardlink_names:
            target = os.path.join(inst_cmd.script_dir, name)
            self.copy_file(os.path.join(inst_cmd.script_dir, "cls"), target, link='hard')
            ## self.outfiles.append(target)


# *** MAINLINE ***
with open('README.md') as readme_file:
    readme = readme_file.read()

setup_requirements = ['bumpversion']

setup(
    author="Alastair Irvine",
    author_email='alastair@plug.org.au',
    python_requires='>=3.4',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Environment :: Console',
        'Topic :: Utilities',
        'Operating System :: POSIX :: Linux',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Unix Shell',
    ],
    description="c*ls commands that use colour and pipe output to less, with a sensible prompt",
    install_requires=requirements,
    license="GNU General Public License v2",
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='cls, ls, less, colour, color',
    name='colorls',
    packages=find_packages(include=['colorls', 'colorls.*']),
    entry_points={
        'console_scripts': [
            'colorls-cli=colorls.cli:wrapper',
        ],
    },
    scripts=['bin/cls'],
    cmdclass={
        'install_scripts': CustomInstallScriptsCommand,
        'develop': CustomDevelopCommand,
    },
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/unixnut/cls',
    version='1.3.0',
    zip_safe=False,
)
