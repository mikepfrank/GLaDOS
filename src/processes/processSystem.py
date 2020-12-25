# processSystem.py

from infrastructure.decorators import singleton

class SubProcess:
	#---------------------------------------------------------------------------
	"""
		SubProcess										   [module public class]
		
			An instance of this class, also called a 'subprocess' or 
			'GLaDOS process,' conceptually represents a sub-process of
			GLaDOS, in the sense of a subsidiary process running within 
			the *single* (OS-level) system process that's running the 
			entire GLaDOS server (within a Python runtime environment).
			
			Presently, subprocesses are implemented using Python threads.
			(This could conceivably change in the future, however.)
					
	"""	#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
	def __init__(self, *args):
		pass

@singleton
class TheProcessSystem: 
	super(
	pass
