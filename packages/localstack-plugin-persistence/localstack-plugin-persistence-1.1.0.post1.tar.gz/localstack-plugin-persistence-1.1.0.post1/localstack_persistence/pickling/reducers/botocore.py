import io
from botocore.response import StreamingBody
from localstack.state import pickle
@pickle.register(StreamingBody)
def pickle_botocore_streaming_body(pickler,obj):A=obj;B=io.BytesIO(A.read());pickler.save_reduce(A.__class__,(B,A._content_length),obj=A)