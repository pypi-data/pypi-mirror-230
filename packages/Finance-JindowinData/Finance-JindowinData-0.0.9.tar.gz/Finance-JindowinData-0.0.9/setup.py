# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages
from distutils.cmd import Command
from distutils.extension import Extension
import os, sys, io, subprocess, platform
from jdwdata import __version__

PACKAGE = "jdwdata"
NAME = "Finance-JindowinData"
VERSION = __version__
DESCRIPTION = "JindowinData" + VERSION
AUTHOR = "flaght"
AUTHOR_EMAIL = "flaght@gmail.com"
URL = 'https://github.com/flaght'


def git_version():
    from subprocess import Popen, PIPE
    gitproc = Popen(['git', 'rev-parse', 'HEAD'], stdout=PIPE)
    (stdout, _) = gitproc.communicate()
    return stdout.strip()

if "--line_trace" in sys.argv:
    line_trace = True
    print("Build with line trace enabled ...")
    sys.argv.remove("--line_trace")
else:
    line_trace = False

class version_build(Command):

    description = "test the distribution prior to install"

    user_options = [
        ('test-dir=', None, "directory that contains the test definitions"),
    ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        git_ver = git_version()[:10]
        configFile = 'jdwdata/__init__.py'

        file_handle = open(configFile, 'r')
        lines = file_handle.readlines()
        newFiles = []
        for line in lines:
            if line.startswith('__version__'):
                line = line.split('+')[0].rstrip()
                line = line + " + \"-" + git_ver + "\"\n"
            newFiles.append(line)
        file_handle.close()
        os.remove(configFile)
        file_handle = open(configFile, 'w')
        file_handle.writelines(newFiles)
        file_handle.close()


requirements = "requirements/py3.txt"

if platform.system() != "Windows":
    import multiprocessing
    n_cpu = multiprocessing.cpu_count()
else:
    n_cpu = 0


setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      packages=find_packages(),
      include_package_data=False,
      install_requires=io.open(requirements, encoding='utf8').read(),
      classifiers=[])
