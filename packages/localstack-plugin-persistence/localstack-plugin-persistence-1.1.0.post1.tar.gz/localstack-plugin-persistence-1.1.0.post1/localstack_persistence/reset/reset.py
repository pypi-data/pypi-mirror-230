import inspect,logging
from functools import singledispatchmethod
from typing import Any
from localstack.services.plugins import Service,ServiceManager
from localstack.services.stores import AccountRegionBundle
from localstack.state import AssetDirectory,StateVisitor
from localstack.utils import files
from localstack.utils.functions import call_safe
from moto.core import BackendDict
LOG=logging.getLogger(__name__)
def reset_state(service):
	A=service;B=ResetStateVisitor();call_safe(A.lifecycle_hook.on_before_state_reset)
	try:A.accept_state_visitor(B)
	except Exception:LOG.exception('Resetting state into service %s',A.name());return
	call_safe(A.lifecycle_hook.on_after_state_reset)
def reset_all(service_manager):
	for A in service_manager.values():reset_state(A)
class ResetStateVisitor(StateVisitor):
	'This visitor resets the container state for a given service'
	@singledispatchmethod
	def visit(self,state_container):LOG.warning('Cannot reset state container of type %s',type(state_container))
	@visit.register(AccountRegionBundle)
	def _(self,state_container):state_container.reset()
	@visit.register(BackendDict)
	def _(self,state_container):
		A=state_container
		for(E,B)in A.items():
			for C in B.keys():
				try:self._reset_moto_backend_state(B,C)
				except Exception as D:
					if LOG.isEnabledFor(logging.DEBUG):LOG.exception('failed to reset the state for BackendDict %s',A)
					else:LOG.error('failed to reset the state for BackendDict %s: %s',A,D)
	@visit.register(AssetDirectory)
	def _(self,state_container):
		B='error resetting asset directory %s';A=state_container.path
		if A.strip()in['','/','/root','/tmp','/home']:LOG.warning('preventing the deletion of protected directory %s',A);return
		try:files.rm_rf(A)
		except Exception:
			if LOG.isEnabledFor(logging.DEBUG):LOG.exception(B,A)
			else:LOG.error(B,A)
	def _reset_moto_backend_state(J,state_container,region_key):
		D=state_container;B=region_key;A=D.get(B);E=getattr(A,'reset',None)
		if E and callable(E):E();return A
		from moto.applicationautoscaling.models import ApplicationAutoscalingBackend as G;from moto.autoscaling.models import AutoScalingBackend as H;from moto.redshift.models import RedshiftBackend as I;F=type(A);C=[B]if len(inspect.signature(F.__init__).parameters)>1 else[]
		if isinstance(A,G):C.append(A.ecs_backend)
		elif isinstance(A,I):C.insert(0,A.ec2_backend)
		elif isinstance(A,H):C=[A.ec2_backend,A.elb_backend,A.elbv2_backend]
		D[B]=F(*C);return D[B]