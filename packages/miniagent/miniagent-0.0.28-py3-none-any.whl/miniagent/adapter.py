import abc
from importlib import import_module
from datetime import datetime
from .common import split_class_path, get_callable_object

class AdapterFactory:

    @staticmethod
    def create_adapter(class_path: str):

        class_obj = get_callable_object(class_path)

        if not issubclass(class_obj, Adapter):
            raise RuntimeError("Class [{}] must be a subclass of"
                               " miniagent.adapter.Adapter"\
                            .format(class_obj.__name__))

        class_instance = class_obj()

        class_instance.set_adapter_name(class_path)

        return class_instance

class Adapter(metaclass=abc.ABCMeta):
    
    def __init__(self):
        self._adaptee = None
        self.adapter_name = ""
        self.adaptee_name = ""

    def set_adapter_name(self, adapter_name: str):
        self.adapter_name = adapter_name

    def get_adapter_name(self):
        return self.adapter_name

    def get_adaptee_name(self):
        return self.adaptee_name

    def set_adaptee(self, class_path: str):
        return self._create_adaptee(class_path)
    
    def get_adaptee(self):
        if self._adaptee is None:
            raise RuntimeError("Adapter [{}] has no adaptee."\
                               .format(self.adapter_name))
        else:
            return self._adaptee

    def _create_adaptee(self, class_path: str):

        if not class_path:
            self.adaptee_name = ""
            self._adaptee = None
            return 1, "No Adaptee"
        
        class_obj = get_callable_object(class_path)

        self._adaptee = class_obj()
        self.adaptee_name = class_path

        return 1, "OK"

    @abc.abstractmethod
    def get_status(self) -> int:
        raise NotImplementedError