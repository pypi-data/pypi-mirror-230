import logging,os,zipfile
from functools import singledispatchmethod
from typing import Any
from localstack import config
from localstack.services.stores import AccountRegionBundle
from localstack.state import AssetDirectory,Encoder,StateVisitor,pickle
from moto.core import BackendDict
from localstack_persistence import constants
LOG=logging.getLogger(__name__)
class CreatePodVisitor(StateVisitor):
	zip:0
	def __init__(A,zip_file,encoder=None):A.zip=zip_file;A.encoder=encoder or pickle.PickleEncoder()
	@singledispatchmethod
	def visit(self,state_container):LOG.warning('cannot save state container of type %s',type(state_container))
	@visit.register(AccountRegionBundle)
	def _(self,state_container):
		A=state_container;B=A.service_name
		for(C,D)in A.items():
			for(E,F)in D.items():
				G=os.path.join(constants.API_STATES_DIRECTORY,C,B,E,constants.LOCALSTACK_STORE_STATE_FILE)
				with self.zip.open(G,'w')as H:self.encoder.encode(F,H)
	@visit.register(BackendDict)
	def _(self,state_container):
		A=state_container;B=A.service_name
		for(C,D)in A.items():
			for(E,F)in D.items():
				G=os.path.join(constants.API_STATES_DIRECTORY,C,B,E,constants.MOTO_BACKEND_STATE_FILE)
				with self.zip.open(G,'w')as H:self.encoder.encode(F,H)
	@visit.register(AssetDirectory)
	def _(self,state_container):
		A=config.dirs.data;A=A.rstrip('/')
		for(C,H,F)in os.walk(state_container.path):
			B=os.path.relpath(C,A).lstrip('/');B=os.path.join(constants.ASSETS_DIRECTORY,B);self.zip.writestr(zipfile.ZipInfo.from_file(A,B),'')
			for D in F:
				E=os.path.join(C,D)
				if os.path.exists(E):G=os.path.join(B,D);self.zip.write(E,G)