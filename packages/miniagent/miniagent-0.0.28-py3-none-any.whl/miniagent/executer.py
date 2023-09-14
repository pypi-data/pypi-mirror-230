import sys
import logging
import inspect
import types
import abc
from typing import Callable
from importlib import import_module
from typing import TypeVar
from .common import SingletonInstane, get_callable_object, is_valid_return
from .adapter import AdapterFactory

class ExecuterInterface(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'execute_command') and 
                callable(subclass.execute_command) or 
                NotImplemented)

    @abc.abstractmethod
    def execute_command(self, 
                        command_code: str, 
                        initial_param: dict, 
                        *args, 
                        **kwargs) -> tuple[int, dict]:
        """Execute biz logic with handles of calless and paramters"""
        raise NotImplementedError

class ExecuterFactory:

    @staticmethod
    def create_executer(class_path: str):

        class_obj = get_callable_object(class_path)

        if not issubclass(class_obj, ExecuterInterface):
            raise RuntimeError("Class [{}] must be a subclass of"
                               " miniagent.executer.ExecuterInterface"\
                            .format(class_obj.__name__))

        return class_obj()

class ExecuterCaller(SingletonInstane):
  
    def __init__(self, configure=None):
        if configure and configure.get('DEFAULT_ADAPTEES'):
            self.default_adaptees = configure['DEFAULT_ADAPTEES']
        else:
            self.default_adaptees = {}

    def _create_adapter(self, adapter_name: str, adaptee_name: str) -> TypeVar('T'):

        padapter = AdapterFactory.create_adapter(adapter_name)
        rtn, msg = padapter.set_adaptee(adaptee_name)

        if not rtn:
            return None
        else:    
            return padapter

    def execute_command(self, message: dict, message_converter: Callable[[dict], dict]=None) -> dict:
        """
        sample message :
        {
            "initial_param":{
                "product_code":"00011",
                "payment_amount":50000,
            },
            "executer":"addin.executer.purchase_card.PurchaseCard",
        }
        """
        if message_converter==None:
            initial_params = message['initial_param'] if message.get('initial_param') else {}
            
            if not message.get('executer'):
                raise RuntimeError("message must contain 'executer' item, which is not exists."
                               " message : [{}]"\
                            .format(str(message)))

            executer_path = message['executer']

        else:
            initial_params, executer_path = message_converter(message)

        executer = ExecuterFactory.create_executer(executer_path)

        sig = inspect.signature(executer.execute_command)

        adapters = dict()

        for param in sig.parameters.values():

            if param.name not in ['db', 'initial_param']:
                dadapter = param.annotation.__module__ +'.'+param.annotation.__name__
                dadaptee = self.default_adaptees[dadapter] if self.default_adaptees.get(dadapter) else ""
                
                #if dadaptee == "":
                #    raise RuntimeError("Adapter [{}] doesn't have default adaptee."
                #            " Please check the constant DEFAULT_ADAPTEES in config.py".format(dadapter))
                
                adapter_instance = self._create_adapter(dadapter, dadaptee)
                adapters[param.name] = adapter_instance

        #from . import app

        #with app.app_context():
        #    rtn, message = executer.execute_command(initial_params, **adapters)
        rtn = executer.execute_command(initial_params, **adapters)

        if not is_valid_return(rtn):
            raise RuntimeError("Return value of execute_command method must be tuple[int, dict].\n"
                               " class : [{}] , return value : [{}]"\
                        .format(executer_path, str(rtn)))            

        return rtn