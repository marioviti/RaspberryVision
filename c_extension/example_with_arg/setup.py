from distutils.core import setup, Extension

module = Extension('myModule', sources = ['myModule.c'])

setup(name = 'PackageName',
    version = '1.0',
    description = 'This is a package fot myModule',
    ext_modules = [module])
