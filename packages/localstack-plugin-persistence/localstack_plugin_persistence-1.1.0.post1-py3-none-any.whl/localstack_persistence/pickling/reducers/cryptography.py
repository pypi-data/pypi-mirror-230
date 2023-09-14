'\nCustom reducers for serializing openssl cryptography concepts.\n'
from cryptography.hazmat.backends.openssl.backend import Backend
from cryptography.hazmat.backends.openssl.ec import _EllipticCurvePrivateKey
from cryptography.hazmat.backends.openssl.rsa import _RSAPrivateKey
from cryptography.hazmat.primitives.asymmetric import ec
from localstack.state import pickle
@pickle.register(Backend)
def pickle_openssl_backend(pickler,obj):
	A=obj
	if not A==_get_openssl_backend():raise TypeError('cannot pickle backend %s, differs from global backend %s'%(A,_get_openssl_backend()))
	pickler.save_reduce(_get_openssl_backend,(),obj=A)
def _get_openssl_backend():from cryptography.hazmat.backends import default_backend as A;return A()
@pickle.register(_EllipticCurvePrivateKey)
def pickle_elliptic_curve_key(pickler,obj):'Fixes pickling of _cffi_backend.__CDataGCP';pickler.save_reduce(_generate_elliptic_curve_private_key,(obj.curve,),obj=obj)
def _generate_elliptic_curve_private_key(curve):from cryptography.hazmat.backends.openssl import backend as A;return A.generate_elliptic_curve_private_key(curve)
@pickle.register(_RSAPrivateKey,subclasses=True)
def pickle_private_key(pickler,obj):A=obj;B=A._backend;C=A._key_size;D=B._ffi.buffer(A._rsa_cdata,C);E=D[:];pickler.save_reduce(_create_rsa_private_key,(B,E),obj=A)
def _create_rsa_private_key(backend,rsa_cdata_buffer):A=backend;B=A._ffi.from_buffer(rsa_cdata_buffer);return _RSAPrivateKey(A,B,A._rsa_cdata_to_evp_pkey(B),unsafe_skip_rsa_key_validation=True)