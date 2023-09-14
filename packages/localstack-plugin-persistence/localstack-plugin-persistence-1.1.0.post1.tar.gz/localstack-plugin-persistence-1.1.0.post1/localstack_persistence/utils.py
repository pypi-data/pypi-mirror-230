from abc import ABC,abstractmethod
class ServiceSorter(ABC):
	'\n    Abstraction to order a list of services.\n    When restoring a state, some services might have dependencies between each other.\n    Thus, we have to make sure to follow a particular restore order.\n    '
	@abstractmethod
	def sort_services(self,services):0
class DefaultPrioritySorter(ServiceSorter):
	'Default service sorting approach that always give S3 the highest priority. It also sorts SQS to be\n    loaded before lambda since lambda depends on SQS.';priorities={'s3':100,'sqs':2,'lambda':1}
	def sort_services(A,services):return sorted(services,key=lambda k:A.priorities.get(k,0),reverse=True)