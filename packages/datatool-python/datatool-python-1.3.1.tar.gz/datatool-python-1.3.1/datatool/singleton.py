"""
In this module, singleton metaclass is implemented.
"""

class Singleton(type):
    """
        Simple singleton.

        Example:

            class MyClass(metaclass=Singleton):
                ...

            a = MyClass.get_instance()  # __init__ was called
            b = MyClass.get_instance()  # __init__ was not called
            print(a is b)  # prints True
    """

    def __new__(cls, *args):
        klass = super().__new__(cls, *args)
        klass.__instance = None
        klass.get_instance = classmethod(cls.get_instance)
        return klass

    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance


class SingletonParameterized(type):
    """
        Singleton within same constructor arguments.

        Example:

            class MyClass(metaclass=SingletonParameterized):
                def __init__(self, a):
                    self._a = a

            a = MyClass.get_instance(1)  # __init__ was called
            b = MyClass.get_instance(2)  # __init__ was called
            c = MyClass.get_instance(2)  # __init__ was not called

            print(a is b)  # False
            print(b is c)  # True
            print(a is c)  # False
    """

    def __new__(cls, *args):
        klass = super().__new__(cls, *args)
        klass.__instance_dct = {}
        klass.get_instance = classmethod(cls.get_instance)
        return klass

    def get_instance(cls, *args):
        if args not in cls.__instance_dct:
            cls.__instance_dct[args] = cls(*args)
        return cls.__instance_dct[args]
