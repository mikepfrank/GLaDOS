	#|--------------------------------------------------------------------------
	#|	@singleton											   [class decorator]
	#|
	#|		This decorator can be supplied before a class definition to 
	#|		declare that class as a singleton class, which means that all
	#|		calls to the class constructor will return the same instance.
	#|
	#|		This implementation uses class wrappers, and the code is taken
	#|		from https://github.com/Kemaweyan/singleton_decorator (GPLv3).
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
	
class _SingletonWrapper:
    """
    A singleton wrapper class. Its instances would be created
    for each decorated class. 
    """

    def __init__(self, cls):
        self.__wrapped__ = cls
        self._instance = None

    def __call__(self, *args, **kwargs):
        """Returns a single instance of decorated class"""
        if self._instance is None:
            self._instance = self.__wrapped__(*args, **kwargs)
        return self._instance

def singleton(cls):
    """
    A singleton decorator. Returns a wrapper objects. A call on that object
    returns a single instance object of decorated class. Use the __wrapped__
    attribute to access decorated class directly in unit tests
    """
    return _SingletonWrapper(cls)


	#|--------------------------------------------------------------------------
	#|	@classproperty										  [method decorator]
	#|
	#|		This decorator can be supplied before a method definition to 
	#|		declare it as a (read-only) class property.  That is, if 
	#|		<Class> is the lexically current class or any of its subclasses, 
	#|		and <instance> is an instance of <Class>, then either of the 
	#|		expressions
	#|		
	#|			<Class>.<methodName>
	#|			<instance>.<methodName>
	#|
	#|		will evaluate to the return value obtained from dynamically 
	#|		calling the method with <Class> as an argument.  Note that 
	#|		assigning to either of these expressions will simply overwrite 
	#|		the property rather than evaluating a setter method.
	#|
	#|		The below implementation comes from Django (BSD license):
	#|		https://github.com/django/django/blob/master/django/utils/functional.py
	#|
	#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

class classproperty:
    """
    Decorator that converts a method with a single cls argument into a property
    that can be accessed directly from the class.
    """
    def __init__(self, method=None):
        self.fget = method

    def __get__(self, instance, cls=None):
        return self.fget(cls)

    def getter(self, method):
        self.fget = method
        return self
