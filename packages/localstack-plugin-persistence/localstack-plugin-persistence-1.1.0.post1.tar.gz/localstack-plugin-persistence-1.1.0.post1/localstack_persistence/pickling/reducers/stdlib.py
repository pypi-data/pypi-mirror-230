'\nCustom reducers for standard lib objects.\n'
import contextvars,queue,threading
from collections import defaultdict
from typing import Any,Callable,Type
from localstack.state import pickle
RLOCK_TYPE=type(threading.RLock())
LOCK_TYPE=type(threading.Lock())
def _create_priority_queue(queue_type,maxsize,queue):A=queue_type(maxsize);A.queue=queue;return A
@pickle.reducer(queue.PriorityQueue,_create_priority_queue,subclasses=True)
def pickle_priority_queue(obj):A=obj;return type(A),A.maxsize,A.queue
@pickle.register(RLOCK_TYPE)
def pickle_rlock(pickler,obj):pickler.save_reduce(threading.RLock,(),obj=obj)
@pickle.register(LOCK_TYPE)
def pickle_lock(pickler,obj):pickler.save_reduce(threading.Lock,(),obj=obj)
def _create_defaultdict(cls,default_factory,items,state=None):
	B=state;A=cls.__new__(cls);A.default_factory=default_factory;A.update(items)
	if B:A.__dict__.update(B)
	return A
@pickle.reducer(defaultdict,_create_defaultdict,subclasses=True)
def pickle_defaultdict(obj):
	A=obj
	if type(A)==defaultdict:return defaultdict,A.default_factory,dict(A),None
	return type(A),A.default_factory,dict(A),A.__dict__
def _create_context(name_to_value):
	A=contextvars.copy_context()
	for(B,D)in A.items():
		if(C:=name_to_value.get(B.name)):A.run(B.set,C)
	return A
@pickle.register(contextvars.Context)
def pickle_contextvars_context(pickler,obj):A={A.name:B for(A,B)in list(obj.items())};return pickler.save_reduce(_create_context,(A,),obj=obj)
def _create_context_vars(name,value):A=contextvars.ContextVar(name);A.set(value);return A
@pickle.register(contextvars.ContextVar)
def pickle_contextvars_contextvars(pickler,obj):A=obj;return pickler.save_reduce(_create_context_vars,(A.name,A.get()),obj=A)