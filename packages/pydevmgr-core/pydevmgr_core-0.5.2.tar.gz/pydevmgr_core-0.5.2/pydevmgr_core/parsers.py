from .base.class_recorder import record_class 
from .base.parser_engine import BaseParser, parser
from .misc.math_parser import ExpEval

from enum import Enum, auto
import math
from typing import Any, Optional , Type
try:
    from pydantic.v1 import validator
except ModuleNotFoundError:
    from pydantic import validator

__all__ = [
"BadValue", 
"BaseParser", 
"parser", 
"Int", "Float", "Complex", "Bool", "Str", "Tuple", "Set", "List", 
"Clipped", "Bounded", "Loockup", 
"Enumerated", "Rounded", "ToString", "Capitalized", "Lowered", 
"Uppered", "Stripped", "LStripped", "RStripped", "Formula", 
]


class ParseErrors(Enum):
    
    OUT_OF_BOUND = auto()
    NOT_IN_LOOCKUP = auto()


class BadValue(ValueError):
    """ Value Error bringing a meaningfull error code """
    def __init__(self, error_code, message):
        self.error_code = error_code
        self.message = message
        super().__init__(message)


def _make_global_parsers(names):
    """ Build automaticaly some parser from python types """
    for tpe in names:        
        Tpe = tpe.__name__.capitalize()
        def fparse(value, config, tpe=tpe):
            return tpe(value)
        class Config(BaseParser.Config):
            type: str = Tpe 
        cls = type( Tpe , (BaseParser,), {'fparse':staticmethod(fparse), 'Config':Config} )    
        record_class(cls)
        record_class(cls, type=tpe.__name__)
        globals()[ Tpe ] = cls
_make_global_parsers([int, float, complex, bool, str, tuple, set, list])




@record_class  
class Clipped(BaseParser):
    class Config(BaseParser.Config):
        type: str = "Clipped"        
        min: float = -math.inf
        max: float = math.inf
    
    @staticmethod
    def fparse(value, config):
        return min(config.max,max(config.min, value))

           
@record_class
class Bounded(BaseParser):
    class Config(BaseParser.Config): 
        type: str = "Bounded" 
        min: float = -math.inf
        max: float = math.inf
    
    @staticmethod
    def fparse(value, config):        
        if value<config.min :
            raise BadValue(ParseErrors.OUT_OF_BOUND, f'{value} is lower than {config.min}')
        if value>config.max :
            raise BadValue(ParseErrors.OUT_OF_BOUND, f'{value} is higher than {config.max}')
        return value


class _Empty_:
    pass

@record_class
class Loockup(BaseParser):
    class Config(BaseParser.Config):
        type: str = "Loockup"     
        loockup : list = []
        loockup_default : Optional[Any] = _Empty_
    
    @staticmethod
    def fparse(value, config):
        if value not in config.loockup:
            try:
                if config.loockup_default is not _Empty_:
                    return config.loockup_default
                else:
                    raise BadValue(ParseErrors.NOT_IN_LOOCKUP, f'must be one of {config.loockup} got {value}')
            except KeyError:            
                raise BadValue(ParseErrors.NOT_IN_LOOCKUP, f'must be one of {config.loockup} got {value}')
        return value    


class _BaseEnum(Enum):
    pass
    
@record_class
class Enumerated(BaseParser):    
    class Config(BaseParser.Config):
        type = "Enumerated"
        enumname: str = "" # name of the Enum class if enumarator is a dictionary 
        enumerator: Type = _BaseEnum 
        
        @validator("enumerator", pre=True, check_fields=False)
        def _enum_validator(cls, value, values):
            if isinstance( value, list):
                value = dict(value)
            if isinstance(value, dict):
                return Enum( values['enumname'] or "TmpEnumerator", value)
            return value 
            
    @staticmethod
    def fparse(value, config):
        try:
            return config.enumerator(value)    
        except ValueError as err:
            raise BadValue( ParseErrors.NOT_IN_LOOCKUP, str(err))


@record_class
class Rounded(BaseParser):
    class Config(BaseParser.Config):
        type: str = "Rounded"      
        ndigits: Optional[int] = 0 
        
    @staticmethod      
    def fparse(value, config):
        return round(value, config.ndigits)          

@record_class
class ToString(BaseParser):
    class Config(BaseParser.Config):
        type: str = "ToString"      
        format : str = "%s"
        
    @staticmethod    
    def fparse(value, config):
        return config.format%(value,)

@record_class
class Capitalized(BaseParser):
    class Config(BaseParser.Config):
        type: str = "Capitalized" 
    @staticmethod
    def fparse(value, config):
        return value.capitalize()

@record_class(type="Lower")
@record_class
class Lowered(BaseParser):
    class Config(BaseParser.Config):
        type: str = "Lowered"
    @staticmethod
    def fparse(value, config):
        return value.lower()

@record_class(type="Upper")
@record_class
class Uppered(BaseParser):
    class Config(BaseParser.Config):
        type: str = "Uppered"
    @staticmethod
    def fparse(value, config):
        return value.upper()

@record_class
class Stripped(BaseParser):
    class Config(BaseParser.Config):
        type: str = "Stripped"
        strip: Optional[str] = None
    @staticmethod
    def fparse(value, config):
        return value.strip(config.strip)

@record_class
class LStripped(BaseParser):
    class Config(BaseParser.Config):
        type: str = "LStripped"
        lstrip: Optional[str] = None
    @staticmethod
    def fparse(value, config):
        return value.lstrip(config.lstrip)

@record_class
class RStripped(BaseParser):
    class Config(BaseParser.Config):
        type: str = "RStripped"
        rstrip: Optional[str] = None
    @staticmethod
    def fparse(value, config):
        return value.rstrip(config.rstrip)

@record_class
class Formula(BaseParser):
    class Config(BaseParser.Config):
        type: str = "Formula"
        formula: str = 'x'
        varname: str = 'x'
    
    @staticmethod
    def fparse(value, config):
        # Cash the Eval expression inside the condig.__dict__
        
        # exp = config.__dict__.setdefault( "__:"+config.formula, ExpEval(config.formula ))
        exp = ExpEval(config.formula )
        return exp.eval( {config.varname:value} ) 

