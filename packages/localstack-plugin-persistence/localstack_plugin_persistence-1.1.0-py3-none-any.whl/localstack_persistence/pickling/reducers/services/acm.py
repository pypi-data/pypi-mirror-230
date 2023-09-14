from localstack.state import pickle
from moto.acm.models import CertBundle
@pickle.register()
class CertBundleReducer(pickle.ObjectStateReducer):
	cls=CertBundle
	def prepare(A,obj,state):state.pop('_cert')
	def restore(D,obj,state):A=state;from cryptography.hazmat.backends import default_backend as B;from cryptography.x509 import load_pem_x509_certificate as C;A['_cert']=C(A['cert'],B())