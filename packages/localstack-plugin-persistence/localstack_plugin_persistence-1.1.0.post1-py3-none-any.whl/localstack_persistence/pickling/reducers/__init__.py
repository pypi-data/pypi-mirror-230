import importlib
from pkgutil import iter_modules
from localstack.utils.objects import singleton_factory
from setuptools import find_packages
def _find_modules(path):
	A=set()
	for B in find_packages(path):
		A.add(B);D=path+'/'+B.replace('.','/')
		for C in iter_modules([D]):
			if not C.ispkg:A.add(B+'.'+C.name)
	return A
@singleton_factory
def register():
	import localstack_persistence.pickling as A
	for B in _find_modules(A.__path__[0]):
		if not B.startswith('reducers.'):continue
		importlib.import_module(A.__name__+'.'+B)