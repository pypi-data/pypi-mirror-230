import json
import sys
import os
from importlib import import_module
from typing import Any
from datetime import datetime
from pytz import timezone, UnknownTimeZoneError
from tzlocal import get_localzone
from enum import Enum

class ExitType(Enum):
    NORMAL_EXIT = 0
    ABNORMAL_EXIT = -1
    STAY_RUNNING = 1

def local_dt_str(iso_str:any):
    from . import configure        
    try:
        if isinstance(iso_str, datetime):
            dt = iso_str
        else:
            dt = datetime.fromisoformat(iso_str)
        local_dt = timezone(configure.get('TIMEZONE')).localize(dt)
        local_dt_str = local_dt.isoformat()        
    except ValueError:
        return iso_str
    except UnknownTimeZoneError:
        return iso_str

    return local_dt_str

def now():
    from . import configure    
    try:
        now = datetime.now(timezone(configure.get('TIMEZONE')))
    except UnknownTimeZoneError:
        now = datetime.now(get_localzone())
    return now

def intersect(list_1st:list, list_2nd:list):

    if not isinstance(list_1st, list):
       list_1st = [list_1st]

    if not isinstance(list_2nd, list):
       list_2nd = [list_2nd]

    return list(set(list_1st) & set(list_2nd))

def is_valid_return(rtn:Any)-> bool:
    
    if isinstance(rtn, tuple) \
        and len(rtn)==2 \
        and isinstance(rtn[0], int) \
        and isinstance(rtn[1], dict):
       return True
    else:
       return False

def split_class_path(class_path: str) -> tuple[str, str]:

    package_name = '.'.join(class_path.split('.')[:-1])
    class_name = class_path.split('.')[-1]

    return package_name, class_name

def jsonFile2Dict(jsonFile: str) -> tuple[int, dict]:

    try:
        f = open(jsonFile)
        data = json.load(f)
    except FileNotFoundError as e:
        return -1, dict(error="JsonFile is not found : {}".format(jsonFile))
    except json.decoder.JSONDecodeError as e:
        return -2, dict(error="JSONDecodeError occured : {}".format(sys.exc_info()[1]))
    
    return 1, data

def get_callable_object(class_path: str) -> object:
        
    package_name, class_name = split_class_path(class_path)

    if package_name is None:
        raise RuntimeError("There is no package name in [{}].",format(class_path))

    try:
      package_module = sys.modules[package_name]\
                    if package_name in sys.modules else import_module(package_name)

    except ImportError:
        raise RuntimeError("Package [{}] of class [{}] isn't able to be imported."\
                        .format(package_name, class_path))

    if not hasattr(package_module, class_name):
        raise RuntimeError("Package [{}] has no attribute [{}]."\
                        .format(package_name, class_name))

    class_obj = getattr(package_module, class_name)

    return class_obj

class SingletonInstane:
  __instance = None

  @classmethod
  def __getInstance(cls):
    return cls.__instance

  @classmethod
  def instance(cls, *args, **kargs):
    cls.__instance = cls(*args, **kargs)
    cls.instance = cls.__getInstance
    return cls.__instance
