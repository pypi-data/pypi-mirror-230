# Header
if(True):
  __doc__          = "This module contains unit tests. Passed 0.0.1"
  __version__      = "0.0.1"
  __reverse_path__ = "../"
  
  # Python Standard Imports
  import sys, os
  
  # Python Math Imports
  if(True):
    import math,cmath,random
    from decimal import *
    from numbers import Number
  
  # Logging Functions
  if(True):
    import logging, types
    
    global log
    log = logging.getLogger()
    
    def log_func(func,context,name=None):
      # Simplify Variables
      name = name if(name!=None) else func.__name__
      # Context: Extend for Non-Nested, Replace for Nested
      if(log.name == "root"): context = context  + "." + name
      else:                   context = log.name + "." + name
      context = ".".join([_.strip("_") for _ in context.split(".")])
      # Wrappers to Update Context
      def log_wrapper(*args, **kwargs):
        # Log with Context
        global log
        log = logging.getLogger(context)
        out = func(*args, **kwargs)
        log = logging.getLogger()
        return out 
      # Return Wrapped Function
      return log_wrapper
    def log_class(cls,context):
      # Add Context
      context = context + "." + cls.__name__
      # Iterate over class dict
      for name, obj in vars(cls).items():
        is_function = callable(obj) and not isinstance(obj,type)
        is_class    = callable(obj) and     isinstance(obj,type)
        if(is_function): setattr( cls, name, log_func( obj,context,name=name) )
        if(is_class):    setattr( cls, name, log_class(obj,context) )
      return cls
    def log_this(obj,context=None):
      # Initial Context
      if(context==None):context = __name__
      # Sort
      is_function = callable(obj) and not isinstance(obj,type)
      is_class    = callable(obj) and     isinstance(obj,type)
      # Return
      if(is_function): return log_func( obj,context)
      if(is_class):    return log_class(obj,context)
  
  # Repo-Script for Repo-Imports
  if(True):
    # Define Repo-Library Path.
    _file_dir_     = os.path.dirname(__file__)
    _repo_dir_     = os.path.join(_file_dir_, __reverse_path__)
    _repo_lib_dir_ = os.path.join(_repo_dir_, "src/")
    _repo_lib_dir_ = os.path.normpath(_repo_lib_dir_)
    # Add Repo-Library to Path.
    if(_repo_lib_dir_ not in sys.path): sys.path.insert(0, _repo_lib_dir_)
  
  # Additional Imports
  import pytest
  from unitment import AmbiguousUnitException,IncompatibleUnitException,UnitException,Unit,Measure
  import unitment as measure

class TestMeasureInit:
  # Initialization & Conversion
  # Note: Failures in init can be caused by failures in parser.
  def test_init(self):
    
    # Implicit Value, Implicit Unit, Implicit Error
    if(True):
      # Str Unit
      if(True): 
        # Str Value, Str Unit
        if(True):
          # Unit First
          assert Measure("cm","2").value   == Decimal("2")
          assert Measure("cm","2").error   == Decimal("0.5")
          assert Measure("cm","2").implied == True
          assert Measure("cm","2").units.symbols   == Unit("cm").symbols
          assert Measure("cm","2").units.magnitude == Unit("cm").magnitude
          # Unit Last
          assert Measure("2","cm").value   == Decimal("2")
          assert Measure("2","cm").error   == Decimal("0.5")
          assert Measure("2","cm").implied == True
          assert Measure("2","cm").units.symbols   == Unit("cm").symbols
          assert Measure("2","cm").units.magnitude == Unit("cm").magnitude
        # Decimal Value, Str Unit
        if(True):
          # Tens Place 
          if(True):
            # Unit First
            assert Measure("M^2", Decimal("10")).value   == Decimal("10")
            assert Measure("M^2", Decimal("10")).error   == Decimal("5")
            assert Measure("M^2", Decimal("10")).implied == True
            assert Measure("M^2", Decimal("10")).units.symbols   == Unit("M^2").symbols
            assert Measure("M^2", Decimal("10")).units.magnitude == Unit("M^2").magnitude
            # Unit Last
            assert Measure(Decimal("10"), "M^2").value   == Decimal("10")
            assert Measure(Decimal("10"), "M^2").error   == Decimal("5")
            assert Measure(Decimal("10"), "M^2").implied == True
            assert Measure(Decimal("10"), "M^2").units.symbols   == Unit("M^2").symbols
            assert Measure(Decimal("10"), "M^2").units.magnitude == Unit("M^2").magnitude
          # Tenths Place 
          if(True):
            # Unit First
            assert Measure("M^2", Decimal("10.1")).value   == Decimal("10.1")
            assert Measure("M^2", Decimal("10.1")).error   == Decimal("0.05")
            assert Measure("M^2", Decimal("10.1")).implied == True
            assert Measure("M^2", Decimal("10.1")).units.symbols   == Unit("M^2").symbols
            assert Measure("M^2", Decimal("10.1")).units.magnitude == Unit("M^2").magnitude
            # Unit Last
            assert Measure(Decimal("10.1"), "M^2").value   == Decimal("10.1")
            assert Measure(Decimal("10.1"), "M^2").error   == Decimal("0.05")
            assert Measure(Decimal("10.1"), "M^2").implied == True
            assert Measure(Decimal("10.1"), "M^2").units.symbols   == Unit("M^2").symbols
            assert Measure(Decimal("10.1"), "M^2").units.magnitude == Unit("M^2").magnitude
        # int Value, Str Unit
        if(True):
          # Unit First
          assert Measure("$",2).value   == Decimal(2)
          assert Measure("$",2).error   == Decimal("0.5")
          assert Measure("$",2).implied == True
          assert Measure("$",2).units.symbols   == Unit("$").symbols
          assert Measure("$",2).units.magnitude == Unit("$").magnitude
          # Unit Last
          assert Measure(2,"$").value   == Decimal(2)
          assert Measure(2,"$").error   == Decimal("0.5")
          assert Measure(2,"$").implied == True
          assert Measure(2,"$").units.symbols   == Unit("$").symbols
          assert Measure(2,"$").units.magnitude == Unit("$").magnitude
        # float Value, Str Unit
        if(True):
          # Unit First
          assert Measure("5 m^2", 10.0).value   == 10.0
          assert Measure("5 m^2", 10.0).error   == 0.05
          assert Measure("5 m^2", 10.0).implied == True
          assert Measure("5 m^2", 10.0).units.symbols    == Unit("5 m^2").symbols 
          assert Measure("5 m^2", 10.0).units.magnitude  == Unit("5 m^2").magnitude 
          # Unit Last
          assert Measure(10.0, "5 m^2").value   == 10.0
          assert Measure(10.0, "5 m^2").error   == 0.05
          assert Measure(10.0, "5 m^2").implied == True
          assert Measure(10.0, "5 m^2").units.symbols   == Unit("5 m^2").symbols
          assert Measure(10.0, "5 m^2").units.magnitude == Unit("5 m^2").magnitude
          # Note: Without context-awareness, there's no way to solve this:
          # assert Measure(float(10), Unit("M^2")).error   == 5.0
      # Unit Unit
      if(True): 
        # Str Value, Str Unit
        if(True):
          # Unit First
          assert Measure(Unit("cm"),"2").value   == Decimal("2")
          assert Measure(Unit("cm"),"2").error   == Decimal("0.5")
          assert Measure(Unit("cm"),"2").implied == True
          assert Measure(Unit("cm"),"2").units.symbols   == Unit("cm").symbols
          assert Measure(Unit("cm"),"2").units.magnitude == Unit("cm").magnitude
          # Unit Last
          assert Measure("2",Unit("cm")).value   == Decimal("2")
          assert Measure("2",Unit("cm")).error   == Decimal("0.5")
          assert Measure("2",Unit("cm")).implied == True
          assert Measure("2",Unit("cm")).units.symbols   == Unit("cm").symbols
          assert Measure("2",Unit("cm")).units.magnitude == Unit("cm").magnitude
        # Decimal Value, Str Unit
        if(True):
          # Tens Place 
          if(True):
            # Unit First
            assert Measure(Unit("M^2"), Decimal("10")).value   == Decimal("10")
            assert Measure(Unit("M^2"), Decimal("10")).error   == Decimal("5")
            assert Measure(Unit("M^2"), Decimal("10")).implied == True
            assert Measure(Unit("M^2"), Decimal("10")).units.symbols   == Unit("M^2").symbols
            assert Measure(Unit("M^2"), Decimal("10")).units.magnitude == Unit("M^2").magnitude
            # Unit Last
            assert Measure(Decimal("10"), Unit("M^2")).value   == Decimal("10")
            assert Measure(Decimal("10"), Unit("M^2")).error   == Decimal("5")
            assert Measure(Decimal("10"), Unit("M^2")).implied == True
            assert Measure(Decimal("10"), Unit("M^2")).units.symbols   == Unit("M^2").symbols
            assert Measure(Decimal("10"), Unit("M^2")).units.magnitude == Unit("M^2").magnitude
          # Tenths Place 
          if(True):
            # Unit First
            assert Measure(Unit("M^2"), Decimal("10.1")).value   == Decimal("10.1")
            assert Measure(Unit("M^2"), Decimal("10.1")).error   == Decimal("0.05")
            assert Measure(Unit("M^2"), Decimal("10.1")).implied == True
            assert Measure(Unit("M^2"), Decimal("10.1")).units.symbols   == Unit("M^2").symbols
            assert Measure(Unit("M^2"), Decimal("10.1")).units.magnitude == Unit("M^2").magnitude
            # Unit Last
            assert Measure(Decimal("10.1"), Unit("M^2")).value   == Decimal("10.1")
            assert Measure(Decimal("10.1"), Unit("M^2")).error   == Decimal("0.05")
            assert Measure(Decimal("10.1"), Unit("M^2")).implied == True
            assert Measure(Decimal("10.1"), Unit("M^2")).units.symbols   == Unit("M^2").symbols
            assert Measure(Decimal("10.1"), Unit("M^2")).units.magnitude == Unit("M^2").magnitude
        # int Value, Str Unit
        if(True):
          # Unit First
          assert Measure(Unit("$"),2).value   == Decimal(2)
          assert Measure(Unit("$"),2).error   == Decimal("0.5")
          assert Measure(Unit("$"),2).implied == True
          assert Measure(Unit("$"),2).units.symbols   == Unit("$").symbols
          assert Measure(Unit("$"),2).units.magnitude == Unit("$").magnitude
          # Unit Last
          assert Measure(2,Unit("$")).value   == Decimal(2)
          assert Measure(2,Unit("$")).error   == Decimal("0.5")
          assert Measure(2,Unit("$")).implied == True
          assert Measure(2,Unit("$")).units.symbols   == Unit("$").symbols
          assert Measure(2,Unit("$")).units.magnitude == Unit("$").magnitude
        # float Value, Str Unit
        if(True):
          # Unit First
          assert Measure(Unit("5 m^2"), 10.0).value   == 10.0
          assert Measure(Unit("5 m^2"), 10.0).error   == 0.05
          assert Measure(Unit("5 m^2"), 10.0).implied == True
          assert Measure(Unit("5 m^2"), 10.0).units.symbols   == Unit("5 m^2").symbols
          assert Measure(Unit("5 m^2"), 10.0).units.magnitude == Unit("5 m^2").magnitude
          # Unit Last
          assert Measure(10.0, Unit("5 m^2")).value   == 10.0
          assert Measure(10.0, Unit("5 m^2")).error   == 0.05
          assert Measure(10.0, Unit("5 m^2")).implied == True
          assert Measure(10.0, Unit("5 m^2")).units.symbols   == Unit("5 m^2").symbols
          assert Measure(10.0, Unit("5 m^2")).units.magnitude == Unit("5 m^2").magnitude
          # Note: Without context-awareness, there's no way to solve this:
          # assert Measure(float(10), Unit("M^2")).error   == 5.0
    
    # Implicit Value, Explicit Unit, Implicit Error
    if(True):
      # Str Unit
      if(True):
        # Str Value, Str Unit
        if(True):
          assert Measure("2",units="cm").value   == Decimal("2")
          assert Measure("2",units="cm").error   == Decimal("0.5")
          assert Measure("2",units="cm").implied == True 
          assert Measure("2",units="cm").units.symbols   == Unit("cm").symbols
          assert Measure("2",units="cm").units.magnitude == Unit("cm").magnitude
        # Decimal Value, Str Unit
        if(True):
          # Tens Place 
          if(True):
            assert Measure(Decimal("10"), unit="M^2").value   == Decimal("10")
            assert Measure(Decimal("10"), unit="M^2").error   == Decimal("5")
            assert Measure(Decimal("10"), unit="M^2").implied == True
            assert Measure(Decimal("10"), unit="M^2").units.symbols   == Unit("M^2").symbols
            assert Measure(Decimal("10"), unit="M^2").units.magnitude == Unit("M^2").magnitude
          # Tenths Place 
          if(True):
            assert Measure(Decimal("10.1"), unit="M^2").value   == Decimal("10.1")
            assert Measure(Decimal("10.1"), unit="M^2").error   == Decimal("0.05")
            assert Measure(Decimal("10.1"), unit="M^2").implied == True
            assert Measure(Decimal("10.1"), unit="M^2").units.symbols   == Unit("M^2").symbols
            assert Measure(Decimal("10.1"), unit="M^2").units.magnitude == Unit("M^2").magnitude
        # int Value, Str Unit
        if(True):
          assert Measure(2,units="$").value   == 2
          assert Measure(2,units="$").error   == 0.5
          assert Measure(2,units="$").implied == True 
          assert Measure(2,units="$").units.symbols   == Unit("$").symbols
          assert Measure(2,units="$").units.magnitude == Unit("$").magnitude
        # float Value, Str Unit
        if(True):
          assert Measure(2.0,units="5 m^2").value   == 2.0
          assert Measure(2.0,units="5 m^2").error   == 0.05
          assert Measure(2.0,units="5 m^2").implied == True 
          assert Measure(2.0,units="5 m^2").units.symbols   == Unit("5 m^2").symbols
          assert Measure(2.0,units="5 m^2").units.magnitude == Unit("5 m^2").magnitude
      # Unit Unit
      if(True):
        # Str Value, Str Unit
        if(True):
          assert Measure("2",units=Unit("cm")).value   == Decimal("2")
          assert Measure("2",units=Unit("cm")).error   == Decimal("0.5")
          assert Measure("2",units=Unit("cm")).implied == True 
          assert Measure("2",units=Unit("cm")).units.symbols   == Unit("cm").symbols
          assert Measure("2",units=Unit("cm")).units.magnitude == Unit("cm").magnitude
        # Decimal Value, Str Unit
        if(True):
          # Tens Place 
          if(True):
            assert Measure(Decimal("10"), unit=Unit("M^2")).value   == Decimal("10")
            assert Measure(Decimal("10"), unit=Unit("M^2")).error   == Decimal("5")
            assert Measure(Decimal("10"), unit=Unit("M^2")).implied == True
            assert Measure(Decimal("10"), unit=Unit("M^2")).units.symbols   == Unit("M^2").symbols
            assert Measure(Decimal("10"), unit=Unit("M^2")).units.magnitude == Unit("M^2").magnitude
          # Tenths Place 
          if(True):
            assert Measure(Decimal("10.1"), unit=Unit("M^2")).value   == Decimal("10.1")
            assert Measure(Decimal("10.1"), unit=Unit("M^2")).error   == Decimal("0.05")
            assert Measure(Decimal("10.1"), unit=Unit("M^2")).implied == True
            assert Measure(Decimal("10.1"), unit=Unit("M^2")).units.symbols   == Unit("M^2").symbols
            assert Measure(Decimal("10.1"), unit=Unit("M^2")).units.magnitude == Unit("M^2").magnitude
        # int Value, Str Unit
        if(True):
          assert Measure(2,units=Unit("$")).value   == 2
          assert Measure(2,units=Unit("$")).error   == 0.5
          assert Measure(2,units=Unit("$")).implied == True 
          assert Measure(2,units=Unit("$")).units.symbols   == Unit("$").symbols
          assert Measure(2,units=Unit("$")).units.magnitude == Unit("$").magnitude
        # float Value, Str Unit
        if(True):
          assert Measure(2.0,units=Unit("5 m^2")).value   == 2.0
          assert Measure(2.0,units=Unit("5 m^2")).error   == 0.05
          assert Measure(2.0,units=Unit("5 m^2")).implied == True 
          assert Measure(2.0,units=Unit("5 m^2")).units.symbols   == Unit("5 m^2").symbols
          assert Measure(2.0,units=Unit("5 m^2")).units.magnitude == Unit("5 m^2").magnitude
      
    # Explicit Value, Implicit Unit, Implicit Error
    if(True):
      # Str Unit
      if(True): 
        # Str Value, Str Unit
        if(True):
          assert Measure("cm",value="2").value   == Decimal("2")
          assert Measure("cm",value="2").error   == Decimal("0.5")
          assert Measure("cm",value="2").implied == True
          assert Measure("cm",value="2").units.symbols   == Unit("cm").symbols
          assert Measure("cm",value="2").units.magnitude == Unit("cm").magnitude
        # Decimal Value, Str Unit
        if(True):
          # Tens Place 
          if(True):
            assert Measure("M^2", value=Decimal("10")).value   == Decimal("10")
            assert Measure("M^2", value=Decimal("10")).error   == Decimal("5")
            assert Measure("M^2", value=Decimal("10")).implied == True
            assert Measure("M^2", value=Decimal("10")).units.symbols   == Unit("M^2").symbols
            assert Measure("M^2", value=Decimal("10")).units.magnitude == Unit("M^2").magnitude
          # Tenths Place 
          if(True):
            assert Measure("M^2", value=Decimal("10.1")).value   == Decimal("10.1")
            assert Measure("M^2", value=Decimal("10.1")).error   == Decimal("0.05")
            assert Measure("M^2", value=Decimal("10.1")).implied == True
            assert Measure("M^2", value=Decimal("10.1")).units.symbols   == Unit("M^2").symbols
            assert Measure("M^2", value=Decimal("10.1")).units.magnitude == Unit("M^2").magnitude
        # int Value, Str Unit
        if(True):
          assert Measure("$",value=2).value   == Decimal(2)
          assert Measure("$",value=2).error   == Decimal("0.5")
          assert Measure("$",value=2).implied == True
          assert Measure("$",value=2).units.symbols   == Unit("$").symbols
          assert Measure("$",value=2).units.magnitude == Unit("$").magnitude
        # float Value, Str Unit
        if(True):
          assert Measure("5 m^2", value=10.0).value   == 10.0
          assert Measure("5 m^2", value=10.0).error   == 0.05
          assert Measure("5 m^2", value=10.0).implied == True
          assert Measure("5 m^2", value=10.0).units.symbols   == Unit("5 m^2").symbols
          assert Measure("5 m^2", value=10.0).units.magnitude == Unit("5 m^2").magnitude
      # Unit Unit
      if(True): 
        # Str Value, Str Unit
        if(True):
          assert Measure(Unit("cm"),value="2").value == Decimal("2")
          assert Measure(Unit("cm"),value="2").error == Decimal("0.5")
          assert Measure(Unit("cm"),value="2").implied  == True
          assert Measure(Unit("cm"),value="2").units.symbols   == Unit("cm").symbols
          assert Measure(Unit("cm"),value="2").units.magnitude == Unit("cm").magnitude
        # Decimal Value, Str Unit
        if(True):
          # Tens Place 
          if(True):
            assert Measure(Unit("M^2"), value=Decimal("10")).value   == Decimal("10")
            assert Measure(Unit("M^2"), value=Decimal("10")).error   == Decimal("5")
            assert Measure(Unit("M^2"), value=Decimal("10")).implied == True
            assert Measure(Unit("M^2"), value=Decimal("10")).units.symbols   == Unit("M^2").symbols
            assert Measure(Unit("M^2"), value=Decimal("10")).units.magnitude == Unit("M^2").magnitude
          # Tenths Place 
          if(True):
            assert Measure(Unit("M^2"), value=Decimal("10.1")).value   == Decimal("10.1")
            assert Measure(Unit("M^2"), value=Decimal("10.1")).error   == Decimal("0.05")
            assert Measure(Unit("M^2"), value=Decimal("10.1")).implied == True
            assert Measure(Unit("M^2"), value=Decimal("10.1")).units.symbols   == Unit("M^2").symbols
            assert Measure(Unit("M^2"), value=Decimal("10.1")).units.magnitude == Unit("M^2").magnitude
        # int Value, Str Unit
        if(True):
          assert Measure(Unit("$"),value=2).value   == Decimal(2)
          assert Measure(Unit("$"),value=2).error   == Decimal("0.5")
          assert Measure(Unit("$"),value=2).implied == True
          assert Measure(Unit("$"),value=2).units.symbols   == Unit("$").symbols
          assert Measure(Unit("$"),value=2).units.magnitude == Unit("$").magnitude
        # float Value, Str Unit
        if(True):
          assert Measure(Unit("5 m^2"), value=10.0).value   == 10.0
          assert Measure(Unit("5 m^2"), value=10.0).error   == 0.05
          assert Measure(Unit("5 m^2"), value=10.0).implied == True
          assert Measure(Unit("5 m^2"), value=10.0).units.symbols   == Unit("5 m^2").symbols
          assert Measure(Unit("5 m^2"), value=10.0).units.magnitude == Unit("5 m^2").magnitude
    
    # Explicit Value, Explicit Unit, Implicit Error
    if(True):
      # Str Unit
      if(True): 
        # Str Value, Str Unit
        if(True):
          assert Measure(unit="cm",value="2").value   == Decimal("2")
          assert Measure(unit="cm",value="2").error   == Decimal("0.5")
          assert Measure(unit="cm",value="2").implied == True
          assert Measure(unit="cm",value="2").units.symbols   == Unit("cm").symbols
          assert Measure(unit="cm",value="2").units.magnitude == Unit("cm").magnitude
        # Decimal Value, Str Unit
        if(True):
          # Tens Place 
          if(True):
            assert Measure(unit="M^2", value=Decimal("10")).value   == Decimal("10")
            assert Measure(unit="M^2", value=Decimal("10")).error   == Decimal("5")
            assert Measure(unit="M^2", value=Decimal("10")).implied == True
            assert Measure(unit="M^2", value=Decimal("10")).units.symbols   == Unit("M^2").symbols
            assert Measure(unit="M^2", value=Decimal("10")).units.magnitude == Unit("M^2").magnitude
          # Tenths Place 
          if(True):
            assert Measure(unit="M^2", value=Decimal("10.1")).value   == Decimal("10.1")
            assert Measure(unit="M^2", value=Decimal("10.1")).error   == Decimal("0.05")
            assert Measure(unit="M^2", value=Decimal("10.1")).implied == True
            assert Measure(unit="M^2", value=Decimal("10.1")).units.symbols   == Unit("M^2").symbols
            assert Measure(unit="M^2", value=Decimal("10.1")).units.magnitude == Unit("M^2").magnitude
        # int Value, Str Unit
        if(True):
          assert Measure(unit="$",value=2).value   == Decimal(2)
          assert Measure(unit="$",value=2).error   == Decimal("0.5")
          assert Measure(unit="$",value=2).implied == True
          assert Measure(unit="$",value=2).units.symbols   == Unit("$").symbols
          assert Measure(unit="$",value=2).units.magnitude == Unit("$").magnitude
        # float Value, Str Unit
        if(True):
          assert Measure(unit="5 m^2", value=10.0).value   == 10.0
          assert Measure(unit="5 m^2", value=10.0).error   == 0.05
          assert Measure(unit="5 m^2", value=10.0).implied == True
          assert Measure(unit="5 m^2", value=10.0).units.symbols   == Unit("5 m^2").symbols
          assert Measure(unit="5 m^2", value=10.0).units.magnitude == Unit("5 m^2").magnitude
      # Unit Unit
      if(True): 
        # Str Value, Str Unit
        if(True):
          assert Measure(unit=Unit("cm"),value="2").value   == Decimal("2")
          assert Measure(unit=Unit("cm"),value="2").error   == Decimal("0.5")
          assert Measure(unit=Unit("cm"),value="2").implied == True
          assert Measure(unit=Unit("cm"),value="2").units.symbols   == Unit("cm").symbols
          assert Measure(unit=Unit("cm"),value="2").units.magnitude == Unit("cm").magnitude
        # Decimal Value, Str Unit
        if(True):
          # Tens Place 
          if(True):
            assert Measure(unit=Unit("M^2"), value=Decimal("10")).value   == Decimal("10")
            assert Measure(unit=Unit("M^2"), value=Decimal("10")).error   == Decimal("5")
            assert Measure(unit=Unit("M^2"), value=Decimal("10")).implied == True
            assert Measure(unit=Unit("M^2"), value=Decimal("10")).units.symbols   == Unit("M^2").symbols
            assert Measure(unit=Unit("M^2"), value=Decimal("10")).units.magnitude == Unit("M^2").magnitude
          # Tenths Place 
          if(True):
            assert Measure(unit=Unit("M^2"), value=Decimal("10.1")).value   == Decimal("10.1")
            assert Measure(unit=Unit("M^2"), value=Decimal("10.1")).error   == Decimal("0.05")
            assert Measure(unit=Unit("M^2"), value=Decimal("10.1")).implied == True
            assert Measure(unit=Unit("M^2"), value=Decimal("10.1")).units.symbols   == Unit("M^2").symbols
            assert Measure(unit=Unit("M^2"), value=Decimal("10.1")).units.magnitude == Unit("M^2").magnitude
        # int Value, Str Unit
        if(True):
          assert Measure(unit=Unit("$"),value=2).value   == Decimal(2)
          assert Measure(unit=Unit("$"),value=2).error   == Decimal("0.5")
          assert Measure(unit=Unit("$"),value=2).implied == True
          assert Measure(unit=Unit("$"),value=2).units.symbols   == Unit("$").symbols
          assert Measure(unit=Unit("$"),value=2).units.magnitude == Unit("$").magnitude
        # float Value, Str Unit
        if(True):
          assert Measure(unit=Unit("5 m^2"), value=10.0).value   == 10.0
          assert Measure(unit=Unit("5 m^2"), value=10.0).error   == 0.05
          assert Measure(unit=Unit("5 m^2"), value=10.0).implied == True
          assert Measure(unit=Unit("5 m^2"), value=10.0).units.symbols   == Unit("5 m^2").symbols
          assert Measure(unit=Unit("5 m^2"), value=10.0).units.magnitude == Unit("5 m^2").magnitude
    
    # Implicit Value, Implicit Unit, Explicit Error
    if(True):
      # Decimal Err
      if(True):
        # Str Unit
        if(True): 
          # Str Value, Str Unit, Decimal Err
          if(True):
            # Unit First
            assert Measure("cm","2",error=Decimal("0.1")).value   == Decimal("2")
            assert Measure("cm","2",error=Decimal("0.1")).error   == Decimal("0.1")
            assert Measure("cm","2",error=Decimal("0.1")).implied == False
            assert Measure("cm","2",error=Decimal("0.1")).units.symbols   == Unit("cm").symbols
            assert Measure("cm","2",error=Decimal("0.1")).units.magnitude == Unit("cm").magnitude
            # Unit Last
            assert Measure("2","cm",error=Decimal("0.1")).value   == Decimal("2")
            assert Measure("2","cm",error=Decimal("0.1")).error   == Decimal("0.1")
            assert Measure("2","cm",error=Decimal("0.1")).implied == False
            assert Measure("2","cm",error=Decimal("0.1")).units.symbols   == Unit("cm").symbols
            assert Measure("2","cm",error=Decimal("0.1")).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Decimal Err
          if(True):
            # Tens Place 
            if(True):
              assert Measure("M^2", Decimal("10"),error=Decimal("0.1")).value   == Decimal("10")
              assert Measure("M^2", Decimal("10"),error=Decimal("0.1")).error   == Decimal("0.1")
              assert Measure("M^2", Decimal("10"),error=Decimal("0.1")).implied == False
              assert Measure("M^2", Decimal("10"),error=Decimal("0.1")).units.symbols   == Unit("M^2").symbols
              assert Measure("M^2", Decimal("10"),error=Decimal("0.1")).units.magnitude == Unit("M^2").magnitude
              # Unit Last
              assert Measure(Decimal("10"), "M^2",error=Decimal("0.1")).value   == Decimal("10")
              assert Measure(Decimal("10"), "M^2",error=Decimal("0.1")).error   == Decimal("0.1")
              assert Measure(Decimal("10"), "M^2",error=Decimal("0.1")).implied == False
              assert Measure(Decimal("10"), "M^2",error=Decimal("0.1")).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10"), "M^2",error=Decimal("0.1")).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              # Unit First
              assert Measure("M^2", Decimal("10.1"),error=Decimal("0.1")).value   == Decimal("10.1")
              assert Measure("M^2", Decimal("10.1"),error=Decimal("0.1")).error   == Decimal("0.1")
              assert Measure("M^2", Decimal("10.1"),error=Decimal("0.1")).implied == False
              assert Measure("M^2", Decimal("10.1"),error=Decimal("0.1")).units.symbols   == Unit("M^2").symbols
              assert Measure("M^2", Decimal("10.1"),error=Decimal("0.1")).units.magnitude == Unit("M^2").magnitude
              # Unit Last
              assert Measure(Decimal("10.1"), "M^2",error=Decimal("0.1")).value   == Decimal("10.1")
              assert Measure(Decimal("10.1"), "M^2",error=Decimal("0.1")).error   == Decimal("0.1")
              assert Measure(Decimal("10.1"), "M^2",error=Decimal("0.1")).implied == False
              assert Measure(Decimal("10.1"), "M^2",error=Decimal("0.1")).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10.1"), "M^2",error=Decimal("0.1")).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Decimal Err
          if(True):
            # Unit First
            assert Measure("$",2,error=Decimal("0.1")).value   == Decimal(2)
            assert Measure("$",2,error=Decimal("0.1")).error   == Decimal("0.1")
            assert Measure("$",2,error=Decimal("0.1")).implied == False
            assert Measure("$",2,error=Decimal("0.1")).units.symbols   == Unit("$").symbols
            assert Measure("$",2,error=Decimal("0.1")).units.magnitude == Unit("$").magnitude
            # Unit Last
            assert Measure(2,"$",error=Decimal("0.1")).value   == Decimal(2)
            assert Measure(2,"$",error=Decimal("0.1")).error   == Decimal("0.1")
            assert Measure(2,"$",error=Decimal("0.1")).implied == False
            assert Measure(2,"$",error=Decimal("0.1")).units.symbols   == Unit("$").symbols
            assert Measure(2,"$",error=Decimal("0.1")).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Decimal Err
          if(True):
            # Unit First
            assert Measure("5 m^2", 10.0,error=Decimal("0.1")).value   == 10.0
            assert Measure("5 m^2", 10.0,error=Decimal("0.1")).error   == 0.1 # Due to Value-Error Type Correction
            assert Measure("5 m^2", 10.0,error=Decimal("0.1")).implied == False
            assert Measure("5 m^2", 10.0,error=Decimal("0.1")).units.symbols   == Unit("5 m^2").symbols
            assert Measure("5 m^2", 10.0,error=Decimal("0.1")).units.magnitude == Unit("5 m^2").magnitude
            # Unit Last
            assert Measure(10.0, "5 m^2",error=Decimal("0.1")).value   == 10.0
            assert Measure(10.0, "5 m^2",error=Decimal("0.1")).error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(10.0, "5 m^2",error=Decimal("0.1")).implied == False
            assert Measure(10.0, "5 m^2",error=Decimal("0.1")).units.symbols   == Unit("5 m^2").symbols
            assert Measure(10.0, "5 m^2",error=Decimal("0.1")).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
        # Unit Unit
        if(True): 
          # Str Value, Str Unit, Decimal Err
          if(True):
            # Unit First
            assert Measure(Unit("cm"),"2",error=Decimal("0.1")).value   == Decimal("2")
            assert Measure(Unit("cm"),"2",error=Decimal("0.1")).error   == Decimal("0.1")
            assert Measure(Unit("cm"),"2",error=Decimal("0.1")).implied == False
            assert Measure(Unit("cm"),"2",error=Decimal("0.1")).units.symbols   == Unit("cm").symbols
            assert Measure(Unit("cm"),"2",error=Decimal("0.1")).units.magnitude == Unit("cm").magnitude
            # Unit Last
            assert Measure("2",Unit("cm"),error=Decimal("0.1")).value   == Decimal("2")
            assert Measure("2",Unit("cm"),error=Decimal("0.1")).error   == Decimal("0.1")
            assert Measure("2",Unit("cm"),error=Decimal("0.1")).implied == False
            assert Measure("2",Unit("cm"),error=Decimal("0.1")).units.symbols   == Unit("cm").symbols
            assert Measure("2",Unit("cm"),error=Decimal("0.1")).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Decimal Err
          if(True):
            # Tens Place 
            if(True):
              # Unit First
              assert Measure(Unit("M^2"), Decimal("10"),error=Decimal("0.1")).value   == Decimal("10")
              assert Measure(Unit("M^2"), Decimal("10"),error=Decimal("0.1")).error   == Decimal("0.1")
              assert Measure(Unit("M^2"), Decimal("10"),error=Decimal("0.1")).implied == False
              assert Measure(Unit("M^2"), Decimal("10"),error=Decimal("0.1")).units.symbols   == Unit("M^2").symbols
              assert Measure(Unit("M^2"), Decimal("10"),error=Decimal("0.1")).units.magnitude == Unit("M^2").magnitude
              # Unit Last
              assert Measure(Decimal("10"), Unit("M^2"),error=Decimal("0.1")).value   == Decimal("10")
              assert Measure(Decimal("10"), Unit("M^2"),error=Decimal("0.1")).error   == Decimal("0.1")
              assert Measure(Decimal("10"), Unit("M^2"),error=Decimal("0.1")).implied == False
              assert Measure(Decimal("10"), Unit("M^2"),error=Decimal("0.1")).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10"), Unit("M^2"),error=Decimal("0.1")).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              # Unit First
              assert Measure(Unit("M^2"), Decimal("10.1"),error=Decimal("0.1")).value   == Decimal("10.1")
              assert Measure(Unit("M^2"), Decimal("10.1"),error=Decimal("0.1")).error   == Decimal("0.1")
              assert Measure(Unit("M^2"), Decimal("10.1"),error=Decimal("0.1")).implied == False
              assert Measure(Unit("M^2"), Decimal("10.1"),error=Decimal("0.1")).units.symbols   == Unit("M^2").symbols
              assert Measure(Unit("M^2"), Decimal("10.1"),error=Decimal("0.1")).units.magnitude == Unit("M^2").magnitude
              # Unit Last
              assert Measure(Decimal("10.1"), Unit("M^2"),error=Decimal("0.1")).value   == Decimal("10.1")
              assert Measure(Decimal("10.1"), Unit("M^2"),error=Decimal("0.1")).error   == Decimal("0.1")
              assert Measure(Decimal("10.1"), Unit("M^2"),error=Decimal("0.1")).implied == False
              assert Measure(Decimal("10.1"), Unit("M^2"),error=Decimal("0.1")).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10.1"), Unit("M^2"),error=Decimal("0.1")).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Decimal Err
          if(True):
            # Unit First
            assert Measure(Unit("$"),2,error=Decimal("0.1")).value   == Decimal(2)
            assert Measure(Unit("$"),2,error=Decimal("0.1")).error   == Decimal("0.1")
            assert Measure(Unit("$"),2,error=Decimal("0.1")).implied == False
            assert Measure(Unit("$"),2,error=Decimal("0.1")).units.symbols   == Unit("$").symbols
            assert Measure(Unit("$"),2,error=Decimal("0.1")).units.magnitude == Unit("$").magnitude
            # Unit Last
            assert Measure(2,Unit("$"),error=Decimal("0.1")).value   == Decimal(2)
            assert Measure(2,Unit("$"),error=Decimal("0.1")).error   == Decimal("0.1")
            assert Measure(2,Unit("$"),error=Decimal("0.1")).implied == False
            assert Measure(2,Unit("$"),error=Decimal("0.1")).units.symbols   == Unit("$").symbols
            assert Measure(2,Unit("$"),error=Decimal("0.1")).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Decimal Err
          if(True):
            # Unit First
            assert Measure(Unit("5 m^2"), 10.0,error=Decimal("0.1")).value   == 10.0
            assert Measure(Unit("5 m^2"), 10.0,error=Decimal("0.1")).error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(Unit("5 m^2"), 10.0,error=Decimal("0.1")).implied == False
            assert Measure(Unit("5 m^2"), 10.0,error=Decimal("0.1")).units.symbols   == Unit("5 m^2").symbols
            assert Measure(Unit("5 m^2"), 10.0,error=Decimal("0.1")).units.magnitude == Unit("5 m^2").magnitude
            # Unit Last
            assert Measure(10.0, Unit("5 m^2"),error=Decimal("0.1")).value   == 10.0
            assert Measure(10.0, Unit("5 m^2"),error=Decimal("0.1")).error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(10.0, Unit("5 m^2"),error=Decimal("0.1")).implied == False
            assert Measure(10.0, Unit("5 m^2"),error=Decimal("0.1")).units.symbols   == Unit("5 m^2").symbols
            assert Measure(10.0, Unit("5 m^2"),error=Decimal("0.1")).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
      # int Err
      if(True):
        # Str Unit
        if(True): 
          # Str Value, Str Unit, Int Err
          if(True):
            # Unit First
            assert Measure("cm","2",error=1).value   == Decimal("2")
            assert Measure("cm","2",error=1).error   == 1
            assert Measure("cm","2",error=1).implied == False
            assert Measure("cm","2",error=1).units.symbols   == Unit("cm").symbols
            assert Measure("cm","2",error=1).units.magnitude == Unit("cm").magnitude
            # Unit Last
            assert Measure("2","cm",error=1).value   == Decimal("2")
            assert Measure("2","cm",error=1).error   == 1
            assert Measure("2","cm",error=1).implied == False
            assert Measure("2","cm",error=1).units.symbols   == Unit("cm").symbols
            assert Measure("2","cm",error=1).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Int Err
          if(True):
            # Tens Place 
            if(True):
              assert Measure("M^2", Decimal("10"),error=1).value   == Decimal("10")
              assert Measure("M^2", Decimal("10"),error=1).error   == 1
              assert Measure("M^2", Decimal("10"),error=1).implied == False
              assert Measure("M^2", Decimal("10"),error=1).units.symbols   == Unit("M^2").symbols
              assert Measure("M^2", Decimal("10"),error=1).units.magnitude == Unit("M^2").magnitude
              # Unit Last
              assert Measure(Decimal("10"), "M^2",error=1).value   == Decimal("10")
              assert Measure(Decimal("10"), "M^2",error=1).error   == 1
              assert Measure(Decimal("10"), "M^2",error=1).implied == False
              assert Measure(Decimal("10"), "M^2",error=1).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10"), "M^2",error=1).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              # Unit First
              assert Measure("M^2", Decimal("10.1"),error=1).value   == Decimal("10.1")
              assert Measure("M^2", Decimal("10.1"),error=1).error   == 1
              assert Measure("M^2", Decimal("10.1"),error=1).implied == False
              assert Measure("M^2", Decimal("10.1"),error=1).units.symbols   == Unit("M^2").symbols
              assert Measure("M^2", Decimal("10.1"),error=1).units.magnitude == Unit("M^2").magnitude
              # Unit Last
              assert Measure(Decimal("10.1"), "M^2",error=1).value   == Decimal("10.1")
              assert Measure(Decimal("10.1"), "M^2",error=1).error   == 1
              assert Measure(Decimal("10.1"), "M^2",error=1).implied == False
              assert Measure(Decimal("10.1"), "M^2",error=1).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10.1"), "M^2",error=1).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Int Err
          if(True):
            # Unit First
            assert Measure("$",2,error=1).value   == Decimal(2)
            assert Measure("$",2,error=1).error   == 1
            assert Measure("$",2,error=1).implied == False
            assert Measure("$",2,error=1).units.symbols   == Unit("$").symbols
            assert Measure("$",2,error=1).units.magnitude == Unit("$").magnitude
            # Unit Last
            assert Measure(2,"$",error=1).value   == Decimal(2)
            assert Measure(2,"$",error=1).error   == 1
            assert Measure(2,"$",error=1).implied == False
            assert Measure(2,"$",error=1).units.symbols   == Unit("$").symbols
            assert Measure(2,"$",error=1).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Int Err
          if(True):
            # Unit First
            assert Measure("5 m^2", 10.0,error=1).value   == 10.0
            assert Measure("5 m^2", 10.0,error=1).error   == 1.0 # Due to Value-Error Type Correction
            assert Measure("5 m^2", 10.0,error=1).implied == False
            assert Measure("5 m^2", 10.0,error=1).units.symbols   == Unit("5 m^2").symbols
            assert Measure("5 m^2", 10.0,error=1).units.magnitude == Unit("5 m^2").magnitude
            # Unit Last
            assert Measure(10.0, "5 m^2",error=1).value   == 10.0
            assert Measure(10.0, "5 m^2",error=1).error   == 1.0 # Due to Value-Error Type Correction
            assert Measure(10.0, "5 m^2",error=1).implied == False
            assert Measure(10.0, "5 m^2",error=1).units.symbols   == Unit("5 m^2").symbols
            assert Measure(10.0, "5 m^2",error=1).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
        # Unit Unit
        if(True): 
          # Str Value, Str Unit, Int Err
          if(True):
            # Unit First
            assert Measure(Unit("cm"),"2",error=1).value   == Decimal("2")
            assert Measure(Unit("cm"),"2",error=1).error   == 1
            assert Measure(Unit("cm"),"2",error=1).implied == False
            assert Measure(Unit("cm"),"2",error=1).units.symbols   == Unit("cm").symbols
            assert Measure(Unit("cm"),"2",error=1).units.magnitude == Unit("cm").magnitude
            # Unit Last
            assert Measure("2",Unit("cm"),error=1).value   == Decimal("2")
            assert Measure("2",Unit("cm"),error=1).error   == 1
            assert Measure("2",Unit("cm"),error=1).implied == False
            assert Measure("2",Unit("cm"),error=1).units.symbols   == Unit("cm").symbols
            assert Measure("2",Unit("cm"),error=1).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Int Err
          if(True):
            # Tens Place 
            if(True):
              # Unit First
              assert Measure(Unit("M^2"), Decimal("10"),error=1).value   == Decimal("10")
              assert Measure(Unit("M^2"), Decimal("10"),error=1).error   == 1
              assert Measure(Unit("M^2"), Decimal("10"),error=1).implied == False
              assert Measure(Unit("M^2"), Decimal("10"),error=1).units.symbols   == Unit("M^2").symbols
              assert Measure(Unit("M^2"), Decimal("10"),error=1).units.magnitude == Unit("M^2").magnitude
              # Unit Last
              assert Measure(Decimal("10"), Unit("M^2"),error=1).value   == Decimal("10")
              assert Measure(Decimal("10"), Unit("M^2"),error=1).error   == 1
              assert Measure(Decimal("10"), Unit("M^2"),error=1).implied == False
              assert Measure(Decimal("10"), Unit("M^2"),error=1).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10"), Unit("M^2"),error=1).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              # Unit First
              assert Measure(Unit("M^2"), Decimal("10.1"),error=1).value   == Decimal("10.1")
              assert Measure(Unit("M^2"), Decimal("10.1"),error=1).error   == 1
              assert Measure(Unit("M^2"), Decimal("10.1"),error=1).implied == False
              assert Measure(Unit("M^2"), Decimal("10.1"),error=1).units.symbols   == Unit("M^2").symbols
              assert Measure(Unit("M^2"), Decimal("10.1"),error=1).units.magnitude == Unit("M^2").magnitude
              # Unit Last
              assert Measure(Decimal("10.1"), Unit("M^2"),error=1).value   == Decimal("10.1")
              assert Measure(Decimal("10.1"), Unit("M^2"),error=1).error   == 1
              assert Measure(Decimal("10.1"), Unit("M^2"),error=1).implied == False
              assert Measure(Decimal("10.1"), Unit("M^2"),error=1).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10.1"), Unit("M^2"),error=1).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Int Err
          if(True):
            # Unit First
            assert Measure(Unit("$"),2,error=1).value   == Decimal(2)
            assert Measure(Unit("$"),2,error=1).error   == 1
            assert Measure(Unit("$"),2,error=1).implied == False
            assert Measure(Unit("$"),2,error=1).units.symbols   == Unit("$").symbols
            assert Measure(Unit("$"),2,error=1).units.magnitude == Unit("$").magnitude
            # Unit Last
            assert Measure(2,Unit("$"),error=1).value   == Decimal(2)
            assert Measure(2,Unit("$"),error=1).error   == 1
            assert Measure(2,Unit("$"),error=1).implied == False
            assert Measure(2,Unit("$"),error=1).units.symbols   == Unit("$").symbols
            assert Measure(2,Unit("$"),error=1).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Int Err
          if(True):
            # Unit First
            assert Measure(Unit("5 m^2"), 10.0,error=1).value   == 10.0
            assert Measure(Unit("5 m^2"), 10.0,error=1).error   == 1.0 # Due to Value-Error Type Correction
            assert Measure(Unit("5 m^2"), 10.0,error=1).implied == False
            assert Measure(Unit("5 m^2"), 10.0,error=1).units.symbols   == Unit("5 m^2").symbols
            assert Measure(Unit("5 m^2"), 10.0,error=1).units.magnitude == Unit("5 m^2").magnitude
            # Unit Last
            assert Measure(10.0, Unit("5 m^2"),error=1).value   == 10.0
            assert Measure(10.0, Unit("5 m^2"),error=1).error   == 1.0 # Due to Value-Error Type Correction
            assert Measure(10.0, Unit("5 m^2"),error=1).implied == False
            assert Measure(10.0, Unit("5 m^2"),error=1).units.symbols   == Unit("5 m^2").symbols
            assert Measure(10.0, Unit("5 m^2"),error=1).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
      # float Err
      if(True):
        # Str Unit
        if(True): 
          # Str Value, Str Unit, Float Err
          if(True):
            # Unit First
            assert Measure("cm","2",error=0.1).value   == 2.0
            assert Measure("cm","2",error=0.1).error   == 0.1
            assert Measure("cm","2",error=0.1).implied == False
            assert Measure("cm","2",error=0.1).units.symbols   == Unit("cm").symbols
            assert Measure("cm","2",error=0.1).units.magnitude == Unit("cm").magnitude
            # Unit Last
            assert Measure("2","cm",error=0.1).value   == 2.0
            assert Measure("2","cm",error=0.1).error   == 0.1
            assert Measure("2","cm",error=0.1).implied == False
            assert Measure("2","cm",error=0.1).units.symbols   == Unit("cm").symbols
            assert Measure("2","cm",error=0.1).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Float Err
          if(True):
            # Tens Place 
            if(True):
              # Unit First
              assert Measure("M^2", Decimal("10"),error=0.1).value   == 10.0
              assert Measure("M^2", Decimal("10"),error=0.1).error   == 0.1
              assert Measure("M^2", Decimal("10"),error=0.1).implied == False
              assert Measure("M^2", Decimal("10"),error=0.1).units.symbols   == Unit("M^2").symbols
              assert Measure("M^2", Decimal("10"),error=0.1).units.magnitude == Unit("M^2").magnitude
              # Unit Last
              assert Measure(Decimal("10"), "M^2",error=0.1).value   == 10.0
              assert Measure(Decimal("10"), "M^2",error=0.1).error   == 0.1
              assert Measure(Decimal("10"), "M^2",error=0.1).implied == False
              assert Measure(Decimal("10"), "M^2",error=0.1).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10"), "M^2",error=0.1).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              # Unit First
              assert Measure("M^2", Decimal("10.1"),error=0.1).value   == 10.1
              assert Measure("M^2", Decimal("10.1"),error=0.1).error   == 0.1
              assert Measure("M^2", Decimal("10.1"),error=0.1).implied == False
              assert Measure("M^2", Decimal("10.1"),error=0.1).units.symbols   == Unit("M^2").symbols
              assert Measure("M^2", Decimal("10.1"),error=0.1).units.magnitude == Unit("M^2").magnitude
              # Unit Last
              assert Measure(Decimal("10.1"), "M^2",error=0.1).value   == 10.1
              assert Measure(Decimal("10.1"), "M^2",error=0.1).error   == 0.1
              assert Measure(Decimal("10.1"), "M^2",error=0.1).implied == False
              assert Measure(Decimal("10.1"), "M^2",error=0.1).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10.1"), "M^2",error=0.1).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Float Err
          if(True):
            # Unit First
            assert Measure("$",2,error=0.1).value   == 2.0
            assert Measure("$",2,error=0.1).error   == 0.1
            assert Measure("$",2,error=0.1).implied == False
            assert Measure("$",2,error=0.1).units.symbols   == Unit("$").symbols
            assert Measure("$",2,error=0.1).units.magnitude == Unit("$").magnitude
            # Unit Last
            assert Measure(2,"$",error=0.1).value   == 2.0
            assert Measure(2,"$",error=0.1).error   == 0.1
            assert Measure(2,"$",error=0.1).implied == False
            assert Measure(2,"$",error=0.1).units.symbols   == Unit("$").symbols
            assert Measure(2,"$",error=0.1).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Float Err
          if(True):
            # Unit First
            assert Measure("5 m^2", 10.0,error=0.1).value   == 10.0
            assert Measure("5 m^2", 10.0,error=0.1).error   == 0.1 # Due to Value-Error Type Correction
            assert Measure("5 m^2", 10.0,error=0.1).implied == False
            assert Measure("5 m^2", 10.0,error=0.1).units.symbols   == Unit("5 m^2").symbols
            assert Measure("5 m^2", 10.0,error=0.1).units.magnitude == Unit("5 m^2").magnitude
            # Unit Last
            assert Measure(10.0, "5 m^2",error=0.1).value   == 10.0
            assert Measure(10.0, "5 m^2",error=0.1).error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(10.0, "5 m^2",error=0.1).implied == False
            assert Measure(10.0, "5 m^2",error=0.1).units.symbols   == Unit("5 m^2").symbols
            assert Measure(10.0, "5 m^2",error=0.1).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
        # Unit Unit
        if(True): 
          # Str Value, Str Unit, Float Err
          if(True):
            # Unit First
            assert Measure(Unit("cm"),"2",error=0.1).value   == 2.0
            assert Measure(Unit("cm"),"2",error=0.1).error   == 0.1
            assert Measure(Unit("cm"),"2",error=0.1).implied == False
            assert Measure(Unit("cm"),"2",error=0.1).units.symbols   == Unit("cm").symbols
            assert Measure(Unit("cm"),"2",error=0.1).units.magnitude == Unit("cm").magnitude
            # Unit Last
            assert Measure("2",Unit("cm"),error=0.1).value   == 2.0
            assert Measure("2",Unit("cm"),error=0.1).error   == 0.1
            assert Measure("2",Unit("cm"),error=0.1).implied == False
            assert Measure("2",Unit("cm"),error=0.1).units.symbols   == Unit("cm").symbols
            assert Measure("2",Unit("cm"),error=0.1).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Float Err
          if(True):
            # Tens Place 
            if(True):
              # Unit First
              assert Measure(Unit("M^2"), Decimal("10"),error=0.1).value   == 10.0
              assert Measure(Unit("M^2"), Decimal("10"),error=0.1).error   == 0.1
              assert Measure(Unit("M^2"), Decimal("10"),error=0.1).implied == False
              assert Measure(Unit("M^2"), Decimal("10"),error=0.1).units.symbols   == Unit("M^2").symbols
              assert Measure(Unit("M^2"), Decimal("10"),error=0.1).units.magnitude == Unit("M^2").magnitude
              # Unit Last
              assert Measure(Decimal("10"), Unit("M^2"),error=0.1).value   == 10.0
              assert Measure(Decimal("10"), Unit("M^2"),error=0.1).error   == 0.1
              assert Measure(Decimal("10"), Unit("M^2"),error=0.1).implied == False
              assert Measure(Decimal("10"), Unit("M^2"),error=0.1).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10"), Unit("M^2"),error=0.1).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              # Unit First
              assert Measure(Unit("M^2"), Decimal("10.1"),error=0.1).value   == 10.1
              assert Measure(Unit("M^2"), Decimal("10.1"),error=0.1).error   == 0.1
              assert Measure(Unit("M^2"), Decimal("10.1"),error=0.1).implied == False
              assert Measure(Unit("M^2"), Decimal("10.1"),error=0.1).units.symbols   == Unit("M^2").symbols
              assert Measure(Unit("M^2"), Decimal("10.1"),error=0.1).units.magnitude == Unit("M^2").magnitude
              # Unit Last
              assert Measure(Decimal("10.1"), Unit("M^2"),error=0.1).value   == 10.1
              assert Measure(Decimal("10.1"), Unit("M^2"),error=0.1).error   == 0.1
              assert Measure(Decimal("10.1"), Unit("M^2"),error=0.1).implied == False
              assert Measure(Decimal("10.1"), Unit("M^2"),error=0.1).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10.1"), Unit("M^2"),error=0.1).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Float Err
          if(True):
            # Unit First
            assert Measure(Unit("$"),2,error=0.1).value   == 2.0
            assert Measure(Unit("$"),2,error=0.1).error   == 0.1
            assert Measure(Unit("$"),2,error=0.1).implied == False
            assert Measure(Unit("$"),2,error=0.1).units.symbols   == Unit("$").symbols
            assert Measure(Unit("$"),2,error=0.1).units.magnitude == Unit("$").magnitude
            # Unit Last
            assert Measure(2,Unit("$"),error=0.1).value   == 2.0
            assert Measure(2,Unit("$"),error=0.1).error   == 0.1
            assert Measure(2,Unit("$"),error=0.1).implied == False
            assert Measure(2,Unit("$"),error=0.1).units.symbols   == Unit("$").symbols
            assert Measure(2,Unit("$"),error=0.1).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Float Err
          if(True):
            # Unit First
            assert Measure(Unit("5 m^2"), 10.0,error=0.1).value   == 10.0
            assert Measure(Unit("5 m^2"), 10.0,error=0.1).error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(Unit("5 m^2"), 10.0,error=0.1).implied == False
            assert Measure(Unit("5 m^2"), 10.0,error=0.1).units.symbols   == Unit("5 m^2").symbols
            assert Measure(Unit("5 m^2"), 10.0,error=0.1).units.magnitude == Unit("5 m^2").magnitude
            # Unit Last
            assert Measure(10.0, Unit("5 m^2"),error=0.1).value   == 10.0
            assert Measure(10.0, Unit("5 m^2"),error=0.1).error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(10.0, Unit("5 m^2"),error=0.1).implied == False
            assert Measure(10.0, Unit("5 m^2"),error=0.1).units.symbols   == Unit("5 m^2").symbols
            assert Measure(10.0, Unit("5 m^2"),error=0.1).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
      # Str Err
      if(True):
        # Str Unit
        if(True): 
          # Str Value, Str Unit, Str Err
          if(True):
            # Unit First
            assert Measure("cm","2",error="0.1").value   == Decimal("2")
            assert Measure("cm","2",error="0.1").error   == Decimal("0.1")
            assert Measure("cm","2",error="0.1").implied == False
            assert Measure("cm","2",error="0.1").units.symbols   == Unit("cm").symbols
            assert Measure("cm","2",error="0.1").units.magnitude == Unit("cm").magnitude
            # Unit Last
            assert Measure("2","cm",error="0.1").value   == Decimal("2")
            assert Measure("2","cm",error="0.1").error   == Decimal("0.1")
            assert Measure("2","cm",error="0.1").implied == False
            assert Measure("2","cm",error="0.1").units.symbols   == Unit("cm").symbols
            assert Measure("2","cm",error="0.1").units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Str Err
          if(True):
            # Tens Place 
            if(True):
              # Unit First
              assert Measure("M^2", Decimal("10"),error="0.1").value   == Decimal("10")
              assert Measure("M^2", Decimal("10"),error="0.1").error   == Decimal("0.1")
              assert Measure("M^2", Decimal("10"),error="0.1").implied == False
              assert Measure("M^2", Decimal("10"),error="0.1").units.symbols   == Unit("M^2").symbols
              assert Measure("M^2", Decimal("10"),error="0.1").units.magnitude == Unit("M^2").magnitude
              # Unit Last
              assert Measure(Decimal("10"), "M^2",error="0.1").value   == Decimal("10")
              assert Measure(Decimal("10"), "M^2",error="0.1").error   == Decimal("0.1")
              assert Measure(Decimal("10"), "M^2",error="0.1").implied == False
              assert Measure(Decimal("10"), "M^2",error="0.1").units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10"), "M^2",error="0.1").units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              # Unit First
              assert Measure("M^2", Decimal("10.1"),error="0.1").value   == Decimal("10.1")
              assert Measure("M^2", Decimal("10.1"),error="0.1").error   == Decimal("0.1")
              assert Measure("M^2", Decimal("10.1"),error="0.1").implied == False
              assert Measure("M^2", Decimal("10.1"),error="0.1").units.symbols   == Unit("M^2").symbols
              assert Measure("M^2", Decimal("10.1"),error="0.1").units.magnitude == Unit("M^2").magnitude
              # Unit Last
              assert Measure(Decimal("10.1"), "M^2",error="0.1").value   == Decimal("10.1")
              assert Measure(Decimal("10.1"), "M^2",error="0.1").error   == Decimal("0.1")
              assert Measure(Decimal("10.1"), "M^2",error="0.1").implied == False
              assert Measure(Decimal("10.1"), "M^2",error="0.1").units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10.1"), "M^2",error="0.1").units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Str Err
          if(True):
            # Unit First
            assert Measure("$",2,error="0.1").value   == Decimal(2)
            assert Measure("$",2,error="0.1").error   == Decimal("0.1")
            assert Measure("$",2,error="0.1").implied == False
            assert Measure("$",2,error="0.1").units.symbols   == Unit("$").symbols
            assert Measure("$",2,error="0.1").units.magnitude == Unit("$").magnitude
            # Unit Last
            assert Measure(2,"$",error="0.1").value   == Decimal(2)
            assert Measure(2,"$",error="0.1").error   == Decimal("0.1")
            assert Measure(2,"$",error="0.1").implied == False
            assert Measure(2,"$",error="0.1").units.symbols   == Unit("$").symbols
            assert Measure(2,"$",error="0.1").units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Str Err
          if(True):
            # Unit First
            assert Measure("5 m^2", 10.0,error="0.1").value   == 10.0
            assert Measure("5 m^2", 10.0,error="0.1").error   == 0.1 # Due to Value-Error Type Correction
            assert Measure("5 m^2", 10.0,error="0.1").implied == False
            assert Measure("5 m^2", 10.0,error="0.1").units.symbols   == Unit("5 m^2").symbols
            assert Measure("5 m^2", 10.0,error="0.1").units.magnitude == Unit("5 m^2").magnitude
            # Unit Last
            assert Measure(10.0, "5 m^2",error="0.1").value   == 10.0
            assert Measure(10.0, "5 m^2",error="0.1").error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(10.0, "5 m^2",error="0.1").implied == False
            assert Measure(10.0, "5 m^2",error="0.1").units.symbols   == Unit("5 m^2").symbols
            assert Measure(10.0, "5 m^2",error="0.1").units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
        # Unit Unit
        if(True): 
          # Str Value, Str Unit, Str Err
          if(True):
            # Unit First
            assert Measure(Unit("cm"),"2",error="0.1").value   == Decimal("2")
            assert Measure(Unit("cm"),"2",error="0.1").error   == Decimal("0.1")
            assert Measure(Unit("cm"),"2",error="0.1").implied == False
            assert Measure(Unit("cm"),"2",error="0.1").units.symbols   == Unit("cm").symbols
            assert Measure(Unit("cm"),"2",error="0.1").units.magnitude == Unit("cm").magnitude
            # Unit Last
            assert Measure("2",Unit("cm"),error="0.1").value   == Decimal("2")
            assert Measure("2",Unit("cm"),error="0.1").error   == Decimal("0.1")
            assert Measure("2",Unit("cm"),error="0.1").implied == False
            assert Measure("2",Unit("cm"),error="0.1").units.symbols   == Unit("cm").symbols
            assert Measure("2",Unit("cm"),error="0.1").units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Str Err
          if(True):
            # Tens Place 
            if(True):
              # Unit First
              assert Measure(Unit("M^2"), Decimal("10"),error="0.1").value   == Decimal("10")
              assert Measure(Unit("M^2"), Decimal("10"),error="0.1").error   == Decimal("0.1")
              assert Measure(Unit("M^2"), Decimal("10"),error="0.1").implied == False
              assert Measure(Unit("M^2"), Decimal("10"),error="0.1").units.symbols   == Unit("M^2").symbols
              assert Measure(Unit("M^2"), Decimal("10"),error="0.1").units.magnitude == Unit("M^2").magnitude
              # Unit Last
              assert Measure(Decimal("10"), Unit("M^2"),error="0.1").value   == Decimal("10")
              assert Measure(Decimal("10"), Unit("M^2"),error="0.1").error   == Decimal("0.1")
              assert Measure(Decimal("10"), Unit("M^2"),error="0.1").implied == False
              assert Measure(Decimal("10"), Unit("M^2"),error="0.1").units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10"), Unit("M^2"),error="0.1").units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              # Unit First
              assert Measure(Unit("M^2"), Decimal("10.1"),error="0.1").value   == Decimal("10.1")
              assert Measure(Unit("M^2"), Decimal("10.1"),error="0.1").error   == Decimal("0.1")
              assert Measure(Unit("M^2"), Decimal("10.1"),error="0.1").implied == False
              assert Measure(Unit("M^2"), Decimal("10.1"),error="0.1").units.symbols   == Unit("M^2").symbols
              assert Measure(Unit("M^2"), Decimal("10.1"),error="0.1").units.magnitude == Unit("M^2").magnitude
              # Unit Last
              assert Measure(Decimal("10.1"), Unit("M^2"),error="0.1").value   == Decimal("10.1")
              assert Measure(Decimal("10.1"), Unit("M^2"),error="0.1").error   == Decimal("0.1")
              assert Measure(Decimal("10.1"), Unit("M^2"),error="0.1").implied == False
              assert Measure(Decimal("10.1"), Unit("M^2"),error="0.1").units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10.1"), Unit("M^2"),error="0.1").units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Str Err
          if(True):
            # Unit First
            assert Measure(Unit("$"),2,error="0.1").value   == Decimal(2)
            assert Measure(Unit("$"),2,error="0.1").error   == Decimal("0.1")
            assert Measure(Unit("$"),2,error="0.1").implied == False
            assert Measure(Unit("$"),2,error="0.1").units.symbols   == Unit("$").symbols
            assert Measure(Unit("$"),2,error="0.1").units.magnitude == Unit("$").magnitude
            # Unit Last
            assert Measure(2,Unit("$"),error="0.1").value   == Decimal(2)
            assert Measure(2,Unit("$"),error="0.1").error   == Decimal("0.1")
            assert Measure(2,Unit("$"),error="0.1").implied == False
            assert Measure(2,Unit("$"),error="0.1").units.symbols   == Unit("$").symbols
            assert Measure(2,Unit("$"),error="0.1").units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Str Err
          if(True):
            # Unit First
            assert Measure(Unit("5 m^2"), 10.0,error="0.1").value   == 10.0
            assert Measure(Unit("5 m^2"), 10.0,error="0.1").error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(Unit("5 m^2"), 10.0,error="0.1").implied == False
            assert Measure(Unit("5 m^2"), 10.0,error="0.1").units.symbols   == Unit("5 m^2").symbols
            assert Measure(Unit("5 m^2"), 10.0,error="0.1").units.magnitude == Unit("5 m^2").magnitude
            # Unit Last
            assert Measure(10.0, Unit("5 m^2"),error="0.1").value   == 10.0
            assert Measure(10.0, Unit("5 m^2"),error="0.1").error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(10.0, Unit("5 m^2"),error="0.1").implied == False
            assert Measure(10.0, Unit("5 m^2"),error="0.1").units.symbols   == Unit("5 m^2").symbols
            assert Measure(10.0, Unit("5 m^2"),error="0.1").units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
    
    # Implicit Value, Explicit Unit, Explicit Error
    if(True):
      # Decimal Err
      if(True):
        # Str Unit
        if(True): 
          # Str Value, Str Unit, Decimal Err
          if(True):
            assert Measure("2",unit="cm",error=Decimal("0.1")).value   == Decimal("2")
            assert Measure("2",unit="cm",error=Decimal("0.1")).error   == Decimal("0.1")
            assert Measure("2",unit="cm",error=Decimal("0.1")).implied == False
            assert Measure("2",unit="cm",error=Decimal("0.1")).units.symbols   == Unit("cm").symbols
            assert Measure("2",unit="cm",error=Decimal("0.1")).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Decimal Err
          if(True):
            # Tens Place 
            if(True):
              assert Measure(Decimal("10"), unit="M^2",error=Decimal("0.1")).value   == Decimal("10")
              assert Measure(Decimal("10"), unit="M^2",error=Decimal("0.1")).error   == Decimal("0.1")
              assert Measure(Decimal("10"), unit="M^2",error=Decimal("0.1")).implied == False
              assert Measure(Decimal("10"), unit="M^2",error=Decimal("0.1")).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10"), unit="M^2",error=Decimal("0.1")).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              assert Measure(Decimal("10.1"), unit="M^2",error=Decimal("0.1")).value   == Decimal("10.1")
              assert Measure(Decimal("10.1"), unit="M^2",error=Decimal("0.1")).error   == Decimal("0.1")
              assert Measure(Decimal("10.1"), unit="M^2",error=Decimal("0.1")).implied == False
              assert Measure(Decimal("10.1"), unit="M^2",error=Decimal("0.1")).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10.1"), unit="M^2",error=Decimal("0.1")).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Decimal Err
          if(True):
            assert Measure(2,unit="$",error=Decimal("0.1")).value   == Decimal(2)
            assert Measure(2,unit="$",error=Decimal("0.1")).error   == Decimal("0.1")
            assert Measure(2,unit="$",error=Decimal("0.1")).implied == False
            assert Measure(2,unit="$",error=Decimal("0.1")).units.symbols   == Unit("$").symbols
            assert Measure(2,unit="$",error=Decimal("0.1")).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Decimal Err
          if(True):
            assert Measure(10.0, unit="5 m^2",error=Decimal("0.1")).value   == 10.0
            assert Measure(10.0, unit="5 m^2",error=Decimal("0.1")).error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(10.0, unit="5 m^2",error=Decimal("0.1")).implied == False
            assert Measure(10.0, unit="5 m^2",error=Decimal("0.1")).units.symbols   == Unit("5 m^2").symbols
            assert Measure(10.0, unit="5 m^2",error=Decimal("0.1")).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
        # Unit Unit
        if(True): 
          # Str Value, Str Unit, Decimal Err
          if(True):
            assert Measure("2",unit=Unit("cm"),error=Decimal("0.1")).value   == Decimal("2")
            assert Measure("2",unit=Unit("cm"),error=Decimal("0.1")).error   == Decimal("0.1")
            assert Measure("2",unit=Unit("cm"),error=Decimal("0.1")).implied == False
            assert Measure("2",unit=Unit("cm"),error=Decimal("0.1")).units.symbols   == Unit("cm").symbols
            assert Measure("2",unit=Unit("cm"),error=Decimal("0.1")).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Decimal Err
          if(True):
            # Tens Place 
            if(True):
              assert Measure(Decimal("10"), unit=Unit("M^2"),error=Decimal("0.1")).value   == Decimal("10")
              assert Measure(Decimal("10"), unit=Unit("M^2"),error=Decimal("0.1")).error   == Decimal("0.1")
              assert Measure(Decimal("10"), unit=Unit("M^2"),error=Decimal("0.1")).implied == False
              assert Measure(Decimal("10"), unit=Unit("M^2"),error=Decimal("0.1")).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10"), unit=Unit("M^2"),error=Decimal("0.1")).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              assert Measure(Decimal("10.1"), unit=Unit("M^2"),error=Decimal("0.1")).value   == Decimal("10.1")
              assert Measure(Decimal("10.1"), unit=Unit("M^2"),error=Decimal("0.1")).error   == Decimal("0.1")
              assert Measure(Decimal("10.1"), unit=Unit("M^2"),error=Decimal("0.1")).implied == False
              assert Measure(Decimal("10.1"), unit=Unit("M^2"),error=Decimal("0.1")).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10.1"), unit=Unit("M^2"),error=Decimal("0.1")).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Decimal Err
          if(True):
            assert Measure(2,unit=Unit("$"),error=Decimal("0.1")).value   == Decimal(2)
            assert Measure(2,unit=Unit("$"),error=Decimal("0.1")).error   == Decimal("0.1")
            assert Measure(2,unit=Unit("$"),error=Decimal("0.1")).implied == False
            assert Measure(2,unit=Unit("$"),error=Decimal("0.1")).units.symbols   == Unit("$").symbols
            assert Measure(2,unit=Unit("$"),error=Decimal("0.1")).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Decimal Err
          if(True):
            assert Measure(10.0, unit=Unit("5 m^2"),error=Decimal("0.1")).value   == 10.0
            assert Measure(10.0, unit=Unit("5 m^2"),error=Decimal("0.1")).error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(10.0, unit=Unit("5 m^2"),error=Decimal("0.1")).implied == False
            assert Measure(10.0, unit=Unit("5 m^2"),error=Decimal("0.1")).units.symbols   == Unit("5 m^2").symbols
            assert Measure(10.0, unit=Unit("5 m^2"),error=Decimal("0.1")).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
      # int Err
      if(True):
        # Str Unit
        if(True): 
          # Str Value, Str Unit, Int Err
          if(True):
            assert Measure("2",unit="cm",error=1).value   == Decimal("2")
            assert Measure("2",unit="cm",error=1).error   == 1
            assert Measure("2",unit="cm",error=1).implied == False
            assert Measure("2",unit="cm",error=1).units.symbols   == Unit("cm").symbols
            assert Measure("2",unit="cm",error=1).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Int Err
          if(True):
            # Tens Place 
            if(True):
              assert Measure(Decimal("10"), unit="M^2",error=1).value   == Decimal("10")
              assert Measure(Decimal("10"), unit="M^2",error=1).error   == 1
              assert Measure(Decimal("10"), unit="M^2",error=1).implied == False
              assert Measure(Decimal("10"), unit="M^2",error=1).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10"), unit="M^2",error=1).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              assert Measure(Decimal("10.1"), unit="M^2",error=1).value   == Decimal("10.1")
              assert Measure(Decimal("10.1"), unit="M^2",error=1).error   == 1
              assert Measure(Decimal("10.1"), unit="M^2",error=1).implied == False
              assert Measure(Decimal("10.1"), unit="M^2",error=1).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10.1"), unit="M^2",error=1).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Int Err
          if(True):
            assert Measure(2,unit="$",error=1).value   == Decimal(2)
            assert Measure(2,unit="$",error=1).error   == 1
            assert Measure(2,unit="$",error=1).implied == False
            assert Measure(2,unit="$",error=1).units.symbols   == Unit("$").symbols
            assert Measure(2,unit="$",error=1).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Int Err
          if(True):
            assert Measure(10.0, unit="5 m^2",error=1).value   == 10.0
            assert Measure(10.0, unit="5 m^2",error=1).error   == 1.0 # Due to Value-Error Type Correction
            assert Measure(10.0, unit="5 m^2",error=1).implied == False
            assert Measure(10.0, unit="5 m^2",error=1).units.symbols   == Unit("5 m^2").symbols
            assert Measure(10.0, unit="5 m^2",error=1).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
        # Unit Unit
        if(True): 
          # Str Value, Str Unit, Int Err
          if(True):
            assert Measure("2",unit=Unit("cm"),error=1).value   == Decimal("2")
            assert Measure("2",unit=Unit("cm"),error=1).error   == 1
            assert Measure("2",unit=Unit("cm"),error=1).implied == False
            assert Measure("2",unit=Unit("cm"),error=1).units.symbols   == Unit("cm").symbols
            assert Measure("2",unit=Unit("cm"),error=1).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Int Err
          if(True):
            # Tens Place 
            if(True):
              assert Measure(Decimal("10"), unit=Unit("M^2"),error=1).value   == Decimal("10")
              assert Measure(Decimal("10"), unit=Unit("M^2"),error=1).error   == 1
              assert Measure(Decimal("10"), unit=Unit("M^2"),error=1).implied == False
              assert Measure(Decimal("10"), unit=Unit("M^2"),error=1).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10"), unit=Unit("M^2"),error=1).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              assert Measure(Decimal("10.1"), unit=Unit("M^2"),error=1).value   == Decimal("10.1")
              assert Measure(Decimal("10.1"), unit=Unit("M^2"),error=1).error   == 1
              assert Measure(Decimal("10.1"), unit=Unit("M^2"),error=1).implied == False
              assert Measure(Decimal("10.1"), unit=Unit("M^2"),error=1).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10.1"), unit=Unit("M^2"),error=1).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Int Err
          if(True):
            assert Measure(2,unit=Unit("$"),error=1).value   == Decimal(2)
            assert Measure(2,unit=Unit("$"),error=1).error   == 1
            assert Measure(2,unit=Unit("$"),error=1).implied == False
            assert Measure(2,unit=Unit("$"),error=1).units.symbols   == Unit("$").symbols
            assert Measure(2,unit=Unit("$"),error=1).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Int Err
          if(True):
            assert Measure(10.0, unit=Unit("5 m^2"),error=1).value   == 10.0
            assert Measure(10.0, unit=Unit("5 m^2"),error=1).error   == 1.0 # Due to Value-Error Type Correction
            assert Measure(10.0, unit=Unit("5 m^2"),error=1).implied == False
            assert Measure(10.0, unit=Unit("5 m^2"),error=1).units.symbols   == Unit("5 m^2").symbols
            assert Measure(10.0, unit=Unit("5 m^2"),error=1).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
      # float Err
      if(True):
        # Str Unit
        if(True): 
          # Str Value, Str Unit, Float Err
          if(True):
            assert Measure("2",unit="cm",error=0.1).value   == 2.0
            assert Measure("2",unit="cm",error=0.1).error   == 0.1
            assert Measure("2",unit="cm",error=0.1).implied == False
            assert Measure("2",unit="cm",error=0.1).units.symbols   == Unit("cm").symbols
            assert Measure("2",unit="cm",error=0.1).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Float Err
          if(True):
            # Tens Place 
            if(True):
              assert Measure(Decimal("10"), unit="M^2",error=0.1).value   == 10.0
              assert Measure(Decimal("10"), unit="M^2",error=0.1).error   == 0.1
              assert Measure(Decimal("10"), unit="M^2",error=0.1).implied == False
              assert Measure(Decimal("10"), unit="M^2",error=0.1).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10"), unit="M^2",error=0.1).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              assert Measure(Decimal("10.1"), unit="M^2",error=0.1).value   == 10.1
              assert Measure(Decimal("10.1"), unit="M^2",error=0.1).error   == 0.1
              assert Measure(Decimal("10.1"), unit="M^2",error=0.1).implied == False
              assert Measure(Decimal("10.1"), unit="M^2",error=0.1).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10.1"), unit="M^2",error=0.1).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Float Err
          if(True):
            assert Measure(2,unit="$",error=0.1).value   == 2.0
            assert Measure(2,unit="$",error=0.1).error   == 0.1
            assert Measure(2,unit="$",error=0.1).implied == False
            assert Measure(2,unit="$",error=0.1).units.symbols   == Unit("$").symbols
            assert Measure(2,unit="$",error=0.1).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Float Err
          if(True):
            assert Measure(10.0, unit="5 m^2",error=0.1).value   == 10.0
            assert Measure(10.0, unit="5 m^2",error=0.1).error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(10.0, unit="5 m^2",error=0.1).implied == False
            assert Measure(10.0, unit="5 m^2",error=0.1).units.symbols   == Unit("5 m^2").symbols
            assert Measure(10.0, unit="5 m^2",error=0.1).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
        # Unit Unit
        if(True): 
          # Str Value, Str Unit, Float Err
          if(True):
            assert Measure("2",unit=Unit("cm"),error=0.1).value == 2.0
            assert Measure("2",unit=Unit("cm"),error=0.1).error == 0.1
            assert Measure("2",unit=Unit("cm"),error=0.1).implied  == False
            assert Measure("2",unit=Unit("cm"),error=0.1).units.symbols   == Unit("cm").symbols
            assert Measure("2",unit=Unit("cm"),error=0.1).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Float Err
          if(True):
            # Tens Place 
            if(True):
              assert Measure(Decimal("10"), unit=Unit("M^2"),error=0.1).value   == 10.0
              assert Measure(Decimal("10"), unit=Unit("M^2"),error=0.1).error   == 0.1
              assert Measure(Decimal("10"), unit=Unit("M^2"),error=0.1).implied == False
              assert Measure(Decimal("10"), unit=Unit("M^2"),error=0.1).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10"), unit=Unit("M^2"),error=0.1).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              assert Measure(Decimal("10.1"), unit=Unit("M^2"),error=0.1).value   == 10.1
              assert Measure(Decimal("10.1"), unit=Unit("M^2"),error=0.1).error   == 0.1
              assert Measure(Decimal("10.1"), unit=Unit("M^2"),error=0.1).implied == False
              assert Measure(Decimal("10.1"), unit=Unit("M^2"),error=0.1).units.symbols   == Unit("M^2").symbols
              assert Measure(Decimal("10.1"), unit=Unit("M^2"),error=0.1).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Float Err
          if(True):
            assert Measure(2,unit=Unit("$"),error=0.1).value   == 2.0
            assert Measure(2,unit=Unit("$"),error=0.1).error   == 0.1
            assert Measure(2,unit=Unit("$"),error=0.1).implied == False
            assert Measure(2,unit=Unit("$"),error=0.1).units.symbols   == Unit("$").symbols
            assert Measure(2,unit=Unit("$"),error=0.1).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Float Err
          if(True):
            assert Measure(10.0, unit=Unit("5 m^2"),error=0.1).value   == 10.0
            assert Measure(10.0, unit=Unit("5 m^2"),error=0.1).error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(10.0, unit=Unit("5 m^2"),error=0.1).implied == False
            assert Measure(10.0, unit=Unit("5 m^2"),error=0.1).units.symbols   == Unit("5 m^2").symbols
            assert Measure(10.0, unit=Unit("5 m^2"),error=0.1).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
      # Str Err
      if(True):
        # Str Unit
        if(True):
          # Str Value, Str Unit, Str Err
          if(True):
            assert Measure("2",units="cm",error="0.1").value   == Decimal("2")
            assert Measure("2",units="cm",error="0.1").error   == Decimal("0.1")
            assert Measure("2",units="cm",error="0.1").implied == False 
            assert Measure("2",units="cm",error="0.1").units.symbols   == Unit("cm").symbols
            assert Measure("2",units="cm",error="0.1").units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Str Err
          if(True):
            assert Measure(Decimal("2"),units="M^2",error="0.1").value   == Decimal("2")
            assert Measure(Decimal("2"),units="M^2",error="0.1").error   == Decimal("0.1")
            assert Measure(Decimal("2"),units="M^2",error="0.1").implied == False 
            assert Measure(Decimal("2"),units="M^2",error="0.1").units.symbols   == Unit("M^2").symbols
            assert Measure(Decimal("2"),units="M^2",error="0.1").units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Str Err
          if(True):
            assert Measure(2,units="$",error="0.1").value   == 2
            assert Measure(2,units="$",error="0.1").error   == Decimal("0.1")
            assert Measure(2,units="$",error="0.1").implied == False 
            assert Measure(2,units="$",error="0.1").units.symbols   == Unit("$").symbols
            assert Measure(2,units="$",error="0.1").units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Str Err
          if(True):
            assert Measure(2.0,units="5 m^2",error="0.1").value == 2.0
            assert Measure(2.0,units="5 m^2",error="0.1").error == 0.1 # Due to Value-Error Type Correction
            assert Measure(2.0,units="5 m^2",error="0.1").implied == False 
            assert Measure(2.0,units="5 m^2",error="0.1").units.symbols   == Unit("5 m^2").symbols
            assert Measure(2.0,units="5 m^2",error="0.1").units.magnitude == Unit("5 m^2").magnitude
        # Unit Unit
        if(True):
          # Str Value, Str Unit, Str Err
          if(True):
            assert Measure("2",units=Unit("cm"),error="0.1").value   == Decimal("2")
            assert Measure("2",units=Unit("cm"),error="0.1").error   == Decimal("0.1")
            assert Measure("2",units=Unit("cm"),error="0.1").implied == False 
            assert Measure("2",units=Unit("cm"),error="0.1").units.symbols   == Unit("cm").symbols
            assert Measure("2",units=Unit("cm"),error="0.1").units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Str Err
          if(True):
            assert Measure(Decimal("2"),units=Unit("M^2"),error="0.1").value   == Decimal("2")
            assert Measure(Decimal("2"),units=Unit("M^2"),error="0.1").error   == Decimal("0.1")
            assert Measure(Decimal("2"),units=Unit("M^2"),error="0.1").implied == False 
            assert Measure(Decimal("2"),units=Unit("M^2"),error="0.1").units.symbols   == Unit("M^2").symbols
            assert Measure(Decimal("2"),units=Unit("M^2"),error="0.1").units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Str Err
          if(True):
            assert Measure(2,units=Unit("$"),error="0.1").value   == 2
            assert Measure(2,units=Unit("$"),error="0.1").error   == Decimal("0.1")
            assert Measure(2,units=Unit("$"),error="0.1").implied == False 
            assert Measure(2,units=Unit("$"),error="0.1").units.symbols   == Unit("$").symbols
            assert Measure(2,units=Unit("$"),error="0.1").units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Str Err
          if(True):
            assert Measure(2.0,units=Unit("5 m^2"),error="0.1").value   == 2.0
            assert Measure(2.0,units=Unit("5 m^2"),error="0.1").error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(2.0,units=Unit("5 m^2"),error="0.1").implied == False 
            assert Measure(2.0,units=Unit("5 m^2"),error="0.1").units.symbols   == Unit("5 m^2").symbols
            assert Measure(2.0,units=Unit("5 m^2"),error="0.1").units.magnitude == Unit("5 m^2").magnitude
    
    # Explicit Value, Implicit Unit, Explicit Error
    if(True):
      # Decimal Err
      if(True):
        # Str Unit
        if(True): 
          # Str Value, Str Unit, Decimal Err
          if(True):
            assert Measure("cm",value="2",error=Decimal("0.1")).value   == Decimal("2")
            assert Measure("cm",value="2",error=Decimal("0.1")).error   == Decimal("0.1")
            assert Measure("cm",value="2",error=Decimal("0.1")).implied == False
            assert Measure("cm",value="2",error=Decimal("0.1")).units.symbols   == Unit("cm").symbols
            assert Measure("cm",value="2",error=Decimal("0.1")).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Decimal Err
          if(True):
            # Tens Place 
            if(True):
              assert Measure("M^2", value=Decimal("10"),error=Decimal("0.1")).value   == Decimal("10")
              assert Measure("M^2", value=Decimal("10"),error=Decimal("0.1")).error   == Decimal("0.1")
              assert Measure("M^2", value=Decimal("10"),error=Decimal("0.1")).implied == False
              assert Measure("M^2", value=Decimal("10"),error=Decimal("0.1")).units.symbols   == Unit("M^2").symbols
              assert Measure("M^2", value=Decimal("10"),error=Decimal("0.1")).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              assert Measure("M^2", value=Decimal("10.1"),error=Decimal("0.1")).value   == Decimal("10.1")
              assert Measure("M^2", value=Decimal("10.1"),error=Decimal("0.1")).error   == Decimal("0.1")
              assert Measure("M^2", value=Decimal("10.1"),error=Decimal("0.1")).implied == False
              assert Measure("M^2", value=Decimal("10.1"),error=Decimal("0.1")).units.symbols   == Unit("M^2").symbols
              assert Measure("M^2", value=Decimal("10.1"),error=Decimal("0.1")).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Decimal Err
          if(True):
            assert Measure("$",value=2,error=Decimal("0.1")).value   == Decimal(2)
            assert Measure("$",value=2,error=Decimal("0.1")).error   == Decimal("0.1")
            assert Measure("$",value=2,error=Decimal("0.1")).implied == False
            assert Measure("$",value=2,error=Decimal("0.1")).units.symbols   == Unit("$").symbols
            assert Measure("$",value=2,error=Decimal("0.1")).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Decimal Err
          if(True):
            assert Measure("5 m^2", value=10.0,error=Decimal("0.1")).value   == 10.0
            assert Measure("5 m^2", value=10.0,error=Decimal("0.1")).error   == 0.1 # Due to Value-Error Type Correction
            assert Measure("5 m^2", value=10.0,error=Decimal("0.1")).implied == False
            assert Measure("5 m^2", value=10.0,error=Decimal("0.1")).units.symbols   == Unit("5 m^2").symbols
            assert Measure("5 m^2", value=10.0,error=Decimal("0.1")).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
        # Unit Unit
        if(True): 
          # Str Value, Str Unit, Decimal Err
          if(True):
            assert Measure(Unit("cm"),value="2",error=Decimal("0.1")).value   == Decimal("2")
            assert Measure(Unit("cm"),value="2",error=Decimal("0.1")).error   == Decimal("0.1")
            assert Measure(Unit("cm"),value="2",error=Decimal("0.1")).implied == False
            assert Measure(Unit("cm"),value="2",error=Decimal("0.1")).units.symbols   == Unit("cm").symbols
            assert Measure(Unit("cm"),value="2",error=Decimal("0.1")).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Decimal Err
          if(True):
            # Tens Place 
            if(True):
              assert Measure(Unit("M^2"), value=Decimal("10"),error=Decimal("0.1")).value   == Decimal("10")
              assert Measure(Unit("M^2"), value=Decimal("10"),error=Decimal("0.1")).error   == Decimal("0.1")
              assert Measure(Unit("M^2"), value=Decimal("10"),error=Decimal("0.1")).implied == False
              assert Measure(Unit("M^2"), value=Decimal("10"),error=Decimal("0.1")).units.symbols   == Unit("M^2").symbols
              assert Measure(Unit("M^2"), value=Decimal("10"),error=Decimal("0.1")).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              assert Measure(Unit("M^2"), value=Decimal("10.1"),error=Decimal("0.1")).value   == Decimal("10.1")
              assert Measure(Unit("M^2"), value=Decimal("10.1"),error=Decimal("0.1")).error   == Decimal("0.1")
              assert Measure(Unit("M^2"), value=Decimal("10.1"),error=Decimal("0.1")).implied == False
              assert Measure(Unit("M^2"), value=Decimal("10.1"),error=Decimal("0.1")).units.symbols   == Unit("M^2").symbols
              assert Measure(Unit("M^2"), value=Decimal("10.1"),error=Decimal("0.1")).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Decimal Err
          if(True):
            assert Measure(Unit("$"),value=2,error=Decimal("0.1")).value   == Decimal(2)
            assert Measure(Unit("$"),value=2,error=Decimal("0.1")).error   == Decimal("0.1")
            assert Measure(Unit("$"),value=2,error=Decimal("0.1")).implied == False
            assert Measure(Unit("$"),value=2,error=Decimal("0.1")).units.symbols   == Unit("$").symbols
            assert Measure(Unit("$"),value=2,error=Decimal("0.1")).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Decimal Err
          if(True):
            assert Measure(Unit("5 m^2"), value=10.0,error=Decimal("0.1")).value   == 10.0
            assert Measure(Unit("5 m^2"), value=10.0,error=Decimal("0.1")).error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(Unit("5 m^2"), value=10.0,error=Decimal("0.1")).implied == False
            assert Measure(Unit("5 m^2"), value=10.0,error=Decimal("0.1")).units.symbols   == Unit("5 m^2").symbols
            assert Measure(Unit("5 m^2"), value=10.0,error=Decimal("0.1")).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
      # int Err
      if(True):
        # Str Unit
        if(True): 
          # Str Value, Str Unit, Int Err
          if(True):
            assert Measure("cm",value="2",error=1).value   == Decimal("2")
            assert Measure("cm",value="2",error=1).error   == 1
            assert Measure("cm",value="2",error=1).implied == False
            assert Measure("cm",value="2",error=1).units.symbols   == Unit("cm").symbols
            assert Measure("cm",value="2",error=1).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Int Err
          if(True):
            # Tens Place 
            if(True):
              assert Measure("M^2", value=Decimal("10"),error=1).value   == Decimal("10")
              assert Measure("M^2", value=Decimal("10"),error=1).error   == 1
              assert Measure("M^2", value=Decimal("10"),error=1).implied == False
              assert Measure("M^2", value=Decimal("10"),error=1).units.symbols   == Unit("M^2").symbols
              assert Measure("M^2", value=Decimal("10"),error=1).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              assert Measure("M^2", value=Decimal("10.1"),error=1).value   == Decimal("10.1")
              assert Measure("M^2", value=Decimal("10.1"),error=1).error   == 1
              assert Measure("M^2", value=Decimal("10.1"),error=1).implied == False
              assert Measure("M^2", value=Decimal("10.1"),error=1).units.symbols   == Unit("M^2").symbols
              assert Measure("M^2", value=Decimal("10.1"),error=1).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Int Err
          if(True):
            assert Measure("$",value=2,error=1).value   == Decimal(2)
            assert Measure("$",value=2,error=1).error   == 1
            assert Measure("$",value=2,error=1).implied == False
            assert Measure("$",value=2,error=1).units.symbols   == Unit("$").symbols
            assert Measure("$",value=2,error=1).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Int Err
          if(True):
            assert Measure("5 m^2", value=10.0,error=1).value   == 10.0
            assert Measure("5 m^2", value=10.0,error=1).error   == 1.0 # Due to Value-Error Type Correction
            assert Measure("5 m^2", value=10.0,error=1).implied == False
            assert Measure("5 m^2", value=10.0,error=1).units.symbols   == Unit("5 m^2").symbols
            assert Measure("5 m^2", value=10.0,error=1).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
        # Unit Unit
        if(True): 
          # Str Value, Str Unit, Int Err
          if(True):
            assert Measure(Unit("cm"),value="2",error=1).value   == Decimal("2")
            assert Measure(Unit("cm"),value="2",error=1).error   == 1
            assert Measure(Unit("cm"),value="2",error=1).implied == False
            assert Measure(Unit("cm"),value="2",error=1).units.symbols   == Unit("cm").symbols
            assert Measure(Unit("cm"),value="2",error=1).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Int Err
          if(True):
            # Tens Place 
            if(True):
              assert Measure(Unit("M^2"), value=Decimal("10"),error=1).value   == Decimal("10")
              assert Measure(Unit("M^2"), value=Decimal("10"),error=1).error   == 1
              assert Measure(Unit("M^2"), value=Decimal("10"),error=1).implied == False
              assert Measure(Unit("M^2"), value=Decimal("10"),error=1).units.symbols   == Unit("M^2").symbols
              assert Measure(Unit("M^2"), value=Decimal("10"),error=1).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              assert Measure(Unit("M^2"), value=Decimal("10.1"),error=1).value   == Decimal("10.1")
              assert Measure(Unit("M^2"), value=Decimal("10.1"),error=1).error   == 1
              assert Measure(Unit("M^2"), value=Decimal("10.1"),error=1).implied == False
              assert Measure(Unit("M^2"), value=Decimal("10.1"),error=1).units.symbols   == Unit("M^2").symbols
              assert Measure(Unit("M^2"), value=Decimal("10.1"),error=1).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Int Err
          if(True):
            assert Measure(Unit("$"),value=2,error=1).value   == Decimal(2)
            assert Measure(Unit("$"),value=2,error=1).error   == 1
            assert Measure(Unit("$"),value=2,error=1).implied == False
            assert Measure(Unit("$"),value=2,error=1).units.symbols   == Unit("$").symbols
            assert Measure(Unit("$"),value=2,error=1).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Int Err
          if(True):
            assert Measure(Unit("5 m^2"), value=10.0,error=1).value   == 10.0
            assert Measure(Unit("5 m^2"), value=10.0,error=1).error   == 1.0 # Due to Value-Error Type Correction
            assert Measure(Unit("5 m^2"), value=10.0,error=1).implied == False
            assert Measure(Unit("5 m^2"), value=10.0,error=1).units.symbols   == Unit("5 m^2").symbols
            assert Measure(Unit("5 m^2"), value=10.0,error=1).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
      # float Err
      if(True):
        # Str Unit
        if(True): 
          # Str Value, Str Unit, Float Err
          if(True):
            assert Measure("cm",value="2",error=0.1).value   == 2.0
            assert Measure("cm",value="2",error=0.1).error   == 0.1
            assert Measure("cm",value="2",error=0.1).implied == False
            assert Measure("cm",value="2",error=0.1).units.symbols   == Unit("cm").symbols
            assert Measure("cm",value="2",error=0.1).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Float Err
          if(True):
            # Tens Place 
            if(True):
              assert Measure("M^2", value=Decimal("10"),error=0.1).value   == 10.0
              assert Measure("M^2", value=Decimal("10"),error=0.1).error   == 0.1
              assert Measure("M^2", value=Decimal("10"),error=0.1).implied == False
              assert Measure("M^2", value=Decimal("10"),error=0.1).units.symbols   == Unit("M^2").symbols
              assert Measure("M^2", value=Decimal("10"),error=0.1).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              assert Measure("M^2", value=Decimal("10.1"),error=0.1).value   == 10.1
              assert Measure("M^2", value=Decimal("10.1"),error=0.1).error   == 0.1
              assert Measure("M^2", value=Decimal("10.1"),error=0.1).implied == False
              assert Measure("M^2", value=Decimal("10.1"),error=0.1).units.symbols   == Unit("M^2").symbols
              assert Measure("M^2", value=Decimal("10.1"),error=0.1).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Float Err
          if(True):
            assert Measure("$",value=2,error=0.1).value   == 2.0
            assert Measure("$",value=2,error=0.1).error   == 0.1
            assert Measure("$",value=2,error=0.1).implied == False
            assert Measure("$",value=2,error=0.1).units.symbols   == Unit("$").symbols
            assert Measure("$",value=2,error=0.1).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Float Err
          if(True):
            assert Measure("5 m^2", value=10.0,error=0.1).value   == 10.0
            assert Measure("5 m^2", value=10.0,error=0.1).error   == 0.1 # Due to Value-Error Type Correction
            assert Measure("5 m^2", value=10.0,error=0.1).implied == False
            assert Measure("5 m^2", value=10.0,error=0.1).units.symbols   == Unit("5 m^2").symbols
            assert Measure("5 m^2", value=10.0,error=0.1).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
        # Unit Unit
        if(True): 
          # Str Value, Str Unit, Float Err
          if(True):
            assert Measure(Unit("cm"),value="2",error=0.1).value   == 2.0
            assert Measure(Unit("cm"),value="2",error=0.1).error   == 0.1
            assert Measure(Unit("cm"),value="2",error=0.1).implied == False
            assert Measure(Unit("cm"),value="2",error=0.1).units.symbols   == Unit("cm").symbols
            assert Measure(Unit("cm"),value="2",error=0.1).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Float Err
          if(True):
            # Tens Place 
            if(True):
              assert Measure(Unit("M^2"), value=Decimal("10"),error=0.1).value   == 10.0
              assert Measure(Unit("M^2"), value=Decimal("10"),error=0.1).error   == 0.1
              assert Measure(Unit("M^2"), value=Decimal("10"),error=0.1).implied == False
              assert Measure(Unit("M^2"), value=Decimal("10"),error=0.1).units.symbols   == Unit("M^2").symbols
              assert Measure(Unit("M^2"), value=Decimal("10"),error=0.1).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              assert Measure(Unit("M^2"), value=Decimal("10.1"),error=0.1).value   == 10.1
              assert Measure(Unit("M^2"), value=Decimal("10.1"),error=0.1).error   == 0.1
              assert Measure(Unit("M^2"), value=Decimal("10.1"),error=0.1).implied == False
              assert Measure(Unit("M^2"), value=Decimal("10.1"),error=0.1).units.symbols   == Unit("M^2").symbols
              assert Measure(Unit("M^2"), value=Decimal("10.1"),error=0.1).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Float Err
          if(True):
            assert Measure(Unit("$"),value=2,error=0.1).value   == 2.0
            assert Measure(Unit("$"),value=2,error=0.1).error   == 0.1
            assert Measure(Unit("$"),value=2,error=0.1).implied == False
            assert Measure(Unit("$"),value=2,error=0.1).units.symbols   == Unit("$").symbols
            assert Measure(Unit("$"),value=2,error=0.1).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Float Err
          if(True):
            assert Measure(Unit("5 m^2"), value=10.0,error=0.1).value   == 10.0
            assert Measure(Unit("5 m^2"), value=10.0,error=0.1).error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(Unit("5 m^2"), value=10.0,error=0.1).implied == False
            assert Measure(Unit("5 m^2"), value=10.0,error=0.1).units.symbols   == Unit("5 m^2").symbols
            assert Measure(Unit("5 m^2"), value=10.0,error=0.1).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
      # Str Err
      if(True):
        # Str Unit
        if(True): 
          # Str Value, Str Unit, Str Err
          if(True):
            assert Measure("cm",value="2",error="0.1").value   == Decimal("2")
            assert Measure("cm",value="2",error="0.1").error   == Decimal("0.1")
            assert Measure("cm",value="2",error="0.1").implied == False
            assert Measure("cm",value="2",error="0.1").units.symbols   == Unit("cm").symbols
            assert Measure("cm",value="2",error="0.1").units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Str Err
          if(True):
            assert Measure("M^2", value=Decimal("10.1"),error="0.1").value   == Decimal("10.1")
            assert Measure("M^2", value=Decimal("10.1"),error="0.1").error   == Decimal("0.1")
            assert Measure("M^2", value=Decimal("10.1"),error="0.1").implied == False
            assert Measure("M^2", value=Decimal("10.1"),error="0.1").units.symbols   == Unit("M^2").symbols
            assert Measure("M^2", value=Decimal("10.1"),error="0.1").units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Str Err
          if(True):
            assert Measure("$",value=2,error="0.1").value   == Decimal(2)
            assert Measure("$",value=2,error="0.1").error   == Decimal("0.1")
            assert Measure("$",value=2,error="0.1").implied == False
            assert Measure("$",value=2,error="0.1").units.symbols   == Unit("$").symbols
            assert Measure("$",value=2,error="0.1").units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Str Err
          if(True):
            assert Measure("5 m^2", value=10.0,error="0.1").value   == 10.0
            assert Measure("5 m^2", value=10.0,error="0.1").error   == 0.1 # Due to Value-Error Type Correction
            assert Measure("5 m^2", value=10.0,error="0.1").implied == False
            assert Measure("5 m^2", value=10.0,error="0.1").units.symbols   == Unit("5 m^2").symbols
            assert Measure("5 m^2", value=10.0,error="0.1").units.magnitude == Unit("5 m^2").magnitude
        # Unit Unit
        if(True): 
          # Str Value, Str Unit, Str Err
          if(True):
            assert Measure(Unit("cm"),value="2",error="0.1").value   == Decimal("2")
            assert Measure(Unit("cm"),value="2",error="0.1").error   == Decimal("0.1")
            assert Measure(Unit("cm"),value="2",error="0.1").implied == False
            assert Measure(Unit("cm"),value="2",error="0.1").units.symbols   == Unit("cm").symbols
            assert Measure(Unit("cm"),value="2",error="0.1").units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Str Err
          if(True):
            assert Measure(Unit("M^2"), value=Decimal("10.1"),error="0.1").value   == Decimal("10.1")
            assert Measure(Unit("M^2"), value=Decimal("10.1"),error="0.1").error   == Decimal("0.1")
            assert Measure(Unit("M^2"), value=Decimal("10.1"),error="0.1").implied == False
            assert Measure(Unit("M^2"), value=Decimal("10.1"),error="0.1").units.symbols   == Unit("M^2").symbols
            assert Measure(Unit("M^2"), value=Decimal("10.1"),error="0.1").units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Str Err
          if(True):
            assert Measure(Unit("$"),value=2,error="0.1").value   == Decimal(2)
            assert Measure(Unit("$"),value=2,error="0.1").error   == Decimal("0.1")
            assert Measure(Unit("$"),value=2,error="0.1").implied == False
            assert Measure(Unit("$"),value=2,error="0.1").units.symbols   == Unit("$").symbols
            assert Measure(Unit("$"),value=2,error="0.1").units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Str Err
          if(True):
            assert Measure(Unit("5 m^2"), value=10.0,error="0.1").value   == 10.0
            assert Measure(Unit("5 m^2"), value=10.0,error="0.1").error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(Unit("5 m^2"), value=10.0,error="0.1").implied == False
            assert Measure(Unit("5 m^2"), value=10.0,error="0.1").units.symbols   == Unit("5 m^2").symbols
            assert Measure(Unit("5 m^2"), value=10.0,error="0.1").units.magnitude == Unit("5 m^2").magnitude
    
    # Explicit Value, Explicit Unit, Explicit Error
    if(True):
      # Decimal Err
      if(True):
        # Str Unit
        if(True): 
          # Str Value, Str Unit, Decimal Err
          if(True):
            assert Measure(unit="cm",value="2",error=Decimal("0.1")).value   == Decimal("2")
            assert Measure(unit="cm",value="2",error=Decimal("0.1")).error   == Decimal("0.1")
            assert Measure(unit="cm",value="2",error=Decimal("0.1")).implied == False
            assert Measure(unit="cm",value="2",error=Decimal("0.1")).units.symbols   == Unit("cm").symbols
            assert Measure(unit="cm",value="2",error=Decimal("0.1")).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Decimal Err
          if(True):
            # Tens Place 
            if(True):
              assert Measure(unit="M^2", value=Decimal("10"),error=Decimal("0.1")).value   == Decimal("10")
              assert Measure(unit="M^2", value=Decimal("10"),error=Decimal("0.1")).error   == Decimal("0.1")
              assert Measure(unit="M^2", value=Decimal("10"),error=Decimal("0.1")).implied == False
              assert Measure(unit="M^2", value=Decimal("10"),error=Decimal("0.1")).units.symbols   == Unit("M^2").symbols
              assert Measure(unit="M^2", value=Decimal("10"),error=Decimal("0.1")).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              assert Measure(unit="M^2", value=Decimal("10.1"),error=Decimal("0.1")).value   == Decimal("10.1")
              assert Measure(unit="M^2", value=Decimal("10.1"),error=Decimal("0.1")).error   == Decimal("0.1")
              assert Measure(unit="M^2", value=Decimal("10.1"),error=Decimal("0.1")).implied == False
              assert Measure(unit="M^2", value=Decimal("10.1"),error=Decimal("0.1")).units.symbols   == Unit("M^2").symbols
              assert Measure(unit="M^2", value=Decimal("10.1"),error=Decimal("0.1")).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Decimal Err
          if(True):
            assert Measure(unit="$",value=2,error=Decimal("0.1")).value   == Decimal(2)
            assert Measure(unit="$",value=2,error=Decimal("0.1")).error   == Decimal("0.1")
            assert Measure(unit="$",value=2,error=Decimal("0.1")).implied == False
            assert Measure(unit="$",value=2,error=Decimal("0.1")).units.symbols   == Unit("$").symbols
            assert Measure(unit="$",value=2,error=Decimal("0.1")).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Decimal Err
          if(True):
            assert Measure(unit="5 m^2", value=10.0,error=Decimal("0.1")).value   == 10.0
            assert Measure(unit="5 m^2", value=10.0,error=Decimal("0.1")).error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(unit="5 m^2", value=10.0,error=Decimal("0.1")).implied == False
            assert Measure(unit="5 m^2", value=10.0,error=Decimal("0.1")).units.symbols   == Unit("5 m^2").symbols
            assert Measure(unit="5 m^2", value=10.0,error=Decimal("0.1")).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
        # Unit Unit
        if(True): 
          # Str Value, Str Unit, Decimal Err
          if(True):
            assert Measure(unit=Unit("cm"),value="2",error=Decimal("0.1")).value   == Decimal("2")
            assert Measure(unit=Unit("cm"),value="2",error=Decimal("0.1")).error   == Decimal("0.1")
            assert Measure(unit=Unit("cm"),value="2",error=Decimal("0.1")).implied == False
            assert Measure(unit=Unit("cm"),value="2",error=Decimal("0.1")).units.symbols   == Unit("cm").symbols
            assert Measure(unit=Unit("cm"),value="2",error=Decimal("0.1")).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Decimal Err
          if(True):
            # Tens Place 
            if(True):
              assert Measure(unit=Unit("M^2"), value=Decimal("10"),error=Decimal("0.1")).value   == Decimal("10")
              assert Measure(unit=Unit("M^2"), value=Decimal("10"),error=Decimal("0.1")).error   == Decimal("0.1")
              assert Measure(unit=Unit("M^2"), value=Decimal("10"),error=Decimal("0.1")).implied == False
              assert Measure(unit=Unit("M^2"), value=Decimal("10"),error=Decimal("0.1")).units.symbols   == Unit("M^2").symbols
              assert Measure(unit=Unit("M^2"), value=Decimal("10"),error=Decimal("0.1")).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              assert Measure(unit=Unit("M^2"), value=Decimal("10.1"),error=Decimal("0.1")).value   == Decimal("10.1")
              assert Measure(unit=Unit("M^2"), value=Decimal("10.1"),error=Decimal("0.1")).error   == Decimal("0.1")
              assert Measure(unit=Unit("M^2"), value=Decimal("10.1"),error=Decimal("0.1")).implied == False
              assert Measure(unit=Unit("M^2"), value=Decimal("10.1"),error=Decimal("0.1")).units.symbols   == Unit("M^2").symbols
              assert Measure(unit=Unit("M^2"), value=Decimal("10.1"),error=Decimal("0.1")).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Decimal Err
          if(True):
            assert Measure(unit=Unit("$"),value=2,error=Decimal("0.1")).value   == Decimal(2)
            assert Measure(unit=Unit("$"),value=2,error=Decimal("0.1")).error   == Decimal("0.1")
            assert Measure(unit=Unit("$"),value=2,error=Decimal("0.1")).implied == False
            assert Measure(unit=Unit("$"),value=2,error=Decimal("0.1")).units.symbols   == Unit("$").symbols
            assert Measure(unit=Unit("$"),value=2,error=Decimal("0.1")).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Decimal Err
          if(True):
            assert Measure(unit=Unit("5 m^2"), value=10.0,error=Decimal("0.1")).value   == 10.0
            assert Measure(unit=Unit("5 m^2"), value=10.0,error=Decimal("0.1")).error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(unit=Unit("5 m^2"), value=10.0,error=Decimal("0.1")).implied == False
            assert Measure(unit=Unit("5 m^2"), value=10.0,error=Decimal("0.1")).units.symbols   == Unit("5 m^2").symbols
            assert Measure(unit=Unit("5 m^2"), value=10.0,error=Decimal("0.1")).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
      # int Err
      if(True):
        # Str Unit
        if(True): 
          # Str Value, Str Unit, Int Err
          if(True):
            assert Measure(unit="cm",value="2",error=1).value   == Decimal("2")
            assert Measure(unit="cm",value="2",error=1).error   == 1
            assert Measure(unit="cm",value="2",error=1).implied == False
            assert Measure(unit="cm",value="2",error=1).units.symbols   == Unit("cm").symbols
            assert Measure(unit="cm",value="2",error=1).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Int Err
          if(True):
            # Tens Place 
            if(True):
              assert Measure(unit="M^2", value=Decimal("10"),error=1).value   == Decimal("10")
              assert Measure(unit="M^2", value=Decimal("10"),error=1).error   == 1
              assert Measure(unit="M^2", value=Decimal("10"),error=1).implied == False
              assert Measure(unit="M^2", value=Decimal("10"),error=1).units.symbols   == Unit("M^2").symbols
              assert Measure(unit="M^2", value=Decimal("10"),error=1).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              assert Measure(unit="M^2", value=Decimal("10.1"),error=1).value   == Decimal("10.1")
              assert Measure(unit="M^2", value=Decimal("10.1"),error=1).error   == 1
              assert Measure(unit="M^2", value=Decimal("10.1"),error=1).implied == False
              assert Measure(unit="M^2", value=Decimal("10.1"),error=1).units.symbols   == Unit("M^2").symbols
              assert Measure(unit="M^2", value=Decimal("10.1"),error=1).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Int Err
          if(True):
            assert Measure(unit="$",value=2,error=1).value   == Decimal(2)
            assert Measure(unit="$",value=2,error=1).error   == 1
            assert Measure(unit="$",value=2,error=1).implied == False
            assert Measure(unit="$",value=2,error=1).units.symbols   == Unit("$").symbols
            assert Measure(unit="$",value=2,error=1).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Int Err
          if(True):
            assert Measure(unit="5 m^2", value=10.0,error=1).value   == 10.0
            assert Measure(unit="5 m^2", value=10.0,error=1).error   == 1.0 # Due to Value-Error Type Correction
            assert Measure(unit="5 m^2", value=10.0,error=1).implied == False
            assert Measure(unit="5 m^2", value=10.0,error=1).units.symbols   == Unit("5 m^2").symbols
            assert Measure(unit="5 m^2", value=10.0,error=1).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
        # Unit Unit
        if(True): 
          # Str Value, Str Unit, Int Err
          if(True):
            assert Measure(unit=Unit("cm"),value="2",error=1).value   == Decimal("2")
            assert Measure(unit=Unit("cm"),value="2",error=1).error   == 1
            assert Measure(unit=Unit("cm"),value="2",error=1).implied == False
            assert Measure(unit=Unit("cm"),value="2",error=1).units.symbols   == Unit("cm").symbols
            assert Measure(unit=Unit("cm"),value="2",error=1).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Int Err
          if(True):
            # Tens Place 
            if(True):
              assert Measure(unit=Unit("M^2"), value=Decimal("10"),error=1).value   == Decimal("10")
              assert Measure(unit=Unit("M^2"), value=Decimal("10"),error=1).error   == 1
              assert Measure(unit=Unit("M^2"), value=Decimal("10"),error=1).implied == False
              assert Measure(unit=Unit("M^2"), value=Decimal("10"),error=1).units.symbols   == Unit("M^2").symbols
              assert Measure(unit=Unit("M^2"), value=Decimal("10"),error=1).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              assert Measure(unit=Unit("M^2"), value=Decimal("10.1"),error=1).value   == Decimal("10.1")
              assert Measure(unit=Unit("M^2"), value=Decimal("10.1"),error=1).error   == 1
              assert Measure(unit=Unit("M^2"), value=Decimal("10.1"),error=1).implied == False
              assert Measure(unit=Unit("M^2"), value=Decimal("10.1"),error=1).units.symbols   == Unit("M^2").symbols
              assert Measure(unit=Unit("M^2"), value=Decimal("10.1"),error=1).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Int Err
          if(True):
            assert Measure(unit=Unit("$"),value=2,error=1).value   == Decimal(2)
            assert Measure(unit=Unit("$"),value=2,error=1).error   == 1
            assert Measure(unit=Unit("$"),value=2,error=1).implied == False
            assert Measure(unit=Unit("$"),value=2,error=1).units.symbols   == Unit("$").symbols
            assert Measure(unit=Unit("$"),value=2,error=1).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Int Err
          if(True):
            assert Measure(unit=Unit("5 m^2"), value=10.0,error=1).value   == 10.0
            assert Measure(unit=Unit("5 m^2"), value=10.0,error=1).error   == 1.0 # Due to Value-Error Type Correction
            assert Measure(unit=Unit("5 m^2"), value=10.0,error=1).implied == False
            assert Measure(unit=Unit("5 m^2"), value=10.0,error=1).units.symbols   == Unit("5 m^2").symbols
            assert Measure(unit=Unit("5 m^2"), value=10.0,error=1).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
      # float Err
      if(True):
        # Str Unit
        if(True): 
          # Str Value, Str Unit, Float Err
          if(True):
            assert Measure(unit="cm",value="2",error=0.1).value   == 2.0
            assert Measure(unit="cm",value="2",error=0.1).error   == 0.1
            assert Measure(unit="cm",value="2",error=0.1).implied == False
            assert Measure(unit="cm",value="2",error=0.1).units.symbols   == Unit("cm").symbols
            assert Measure(unit="cm",value="2",error=0.1).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Float Err
          if(True):
            # Tens Place 
            if(True):
              assert Measure(unit="M^2", value=Decimal("10"),error=0.1).value   == 10.0
              assert Measure(unit="M^2", value=Decimal("10"),error=0.1).error   == 0.1
              assert Measure(unit="M^2", value=Decimal("10"),error=0.1).implied == False
              assert Measure(unit="M^2", value=Decimal("10"),error=0.1).units.symbols   == Unit("M^2").symbols
              assert Measure(unit="M^2", value=Decimal("10"),error=0.1).units.magnitude   == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              assert Measure(unit="M^2", value=Decimal("10.1"),error=0.1).value   == 10.1
              assert Measure(unit="M^2", value=Decimal("10.1"),error=0.1).error   == 0.1
              assert Measure(unit="M^2", value=Decimal("10.1"),error=0.1).implied == False
              assert Measure(unit="M^2", value=Decimal("10.1"),error=0.1).units.symbols   == Unit("M^2").symbols
              assert Measure(unit="M^2", value=Decimal("10.1"),error=0.1).units.magnitude   == Unit("M^2").magnitude
          # int Value, Str Unit, Float Err
          if(True):
            assert Measure(unit="$",value=2,error=0.1).value   == 2.0
            assert Measure(unit="$",value=2,error=0.1).error   == 0.1
            assert Measure(unit="$",value=2,error=0.1).implied == False
            assert Measure(unit="$",value=2,error=0.1).units.symbols   == Unit("$").symbols
            assert Measure(unit="$",value=2,error=0.1).units.magnitude   == Unit("$").magnitude
          # float Value, Str Unit, Float Err
          if(True):
            assert Measure(unit="5 m^2", value=10.0,error=0.1).value   == 10.0
            assert Measure(unit="5 m^2", value=10.0,error=0.1).error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(unit="5 m^2", value=10.0,error=0.1).implied == False
            assert Measure(unit="5 m^2", value=10.0,error=0.1).units.symbols   == Unit("5 m^2").symbols
            assert Measure(unit="5 m^2", value=10.0,error=0.1).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
        # Unit Unit
        if(True): 
          # Str Value, Str Unit, Float Err
          if(True):
            assert Measure(unit=Unit("cm"),value="2",error=0.1).value   == 2.0
            assert Measure(unit=Unit("cm"),value="2",error=0.1).error   == 0.1
            assert Measure(unit=Unit("cm"),value="2",error=0.1).implied == False
            assert Measure(unit=Unit("cm"),value="2",error=0.1).units.symbols   == Unit("cm").symbols
            assert Measure(unit=Unit("cm"),value="2",error=0.1).units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Float Err
          if(True):
            # Tens Place 
            if(True):
              assert Measure(unit=Unit("M^2"), value=Decimal("10"),error=0.1).value   == 10.0
              assert Measure(unit=Unit("M^2"), value=Decimal("10"),error=0.1).error   == 0.1
              assert Measure(unit=Unit("M^2"), value=Decimal("10"),error=0.1).implied == False
              assert Measure(unit=Unit("M^2"), value=Decimal("10"),error=0.1).units.symbols   == Unit("M^2").symbols
              assert Measure(unit=Unit("M^2"), value=Decimal("10"),error=0.1).units.magnitude == Unit("M^2").magnitude
            # Tenths Place 
            if(True):
              assert Measure(unit=Unit("M^2"), value=Decimal("10.1"),error=0.1).value   == 10.1
              assert Measure(unit=Unit("M^2"), value=Decimal("10.1"),error=0.1).error   == 0.1
              assert Measure(unit=Unit("M^2"), value=Decimal("10.1"),error=0.1).implied == False
              assert Measure(unit=Unit("M^2"), value=Decimal("10.1"),error=0.1).units.symbols   == Unit("M^2").symbols
              assert Measure(unit=Unit("M^2"), value=Decimal("10.1"),error=0.1).units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Float Err
          if(True):
            assert Measure(unit=Unit("$"),value=2,error=0.1).value   == 2.0
            assert Measure(unit=Unit("$"),value=2,error=0.1).error   == 0.1
            assert Measure(unit=Unit("$"),value=2,error=0.1).implied == False
            assert Measure(unit=Unit("$"),value=2,error=0.1).units.symbols   == Unit("$").symbols
            assert Measure(unit=Unit("$"),value=2,error=0.1).units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Float Err
          if(True):
            assert Measure(unit=Unit("5 m^2"), value=10.0,error=0.1).value   == 10.0
            assert Measure(unit=Unit("5 m^2"), value=10.0,error=0.1).error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(unit=Unit("5 m^2"), value=10.0,error=0.1).implied == False
            assert Measure(unit=Unit("5 m^2"), value=10.0,error=0.1).units.symbols   == Unit("5 m^2").symbols
            assert Measure(unit=Unit("5 m^2"), value=10.0,error=0.1).units.magnitude == Unit("5 m^2").magnitude
            # Note: Without context-awareness, there's no way to solve this:
            # assert Measure(float(10), Unit("M^2")).error   == 5.0
      # Str Err
      if(True):
        # Str Unit
        if(True): 
          # Str Value, Str Unit, Str Err
          if(True):
            assert Measure(unit="cm",value="2",error="0.1").value   == Decimal("2")
            assert Measure(unit="cm",value="2",error="0.1").error   == Decimal("0.1")
            assert Measure(unit="cm",value="2",error="0.1").implied == False
            assert Measure(unit="cm",value="2",error="0.1").units.symbols   == Unit("cm").symbols
            assert Measure(unit="cm",value="2",error="0.1").units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Str Err
          if(True):
            assert Measure(unit="M^2", value=Decimal("10.1"),error="0.1").value   == Decimal("10.1")
            assert Measure(unit="M^2", value=Decimal("10.1"),error="0.1").error   == Decimal("0.1")
            assert Measure(unit="M^2", value=Decimal("10.1"),error="0.1").implied == False
            assert Measure(unit="M^2", value=Decimal("10.1"),error="0.1").units.symbols   == Unit("M^2").symbols
            assert Measure(unit="M^2", value=Decimal("10.1"),error="0.1").units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Str Err
          if(True):
            assert Measure(unit="$",value=2,error="0.1").value   == Decimal(2)
            assert Measure(unit="$",value=2,error="0.1").error   == Decimal("0.1")
            assert Measure(unit="$",value=2,error="0.1").implied == False
            assert Measure(unit="$",value=2,error="0.1").units.symbols   == Unit("$").symbols
            assert Measure(unit="$",value=2,error="0.1").units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Str Err
          if(True):
            assert Measure(unit="5 m^2", value=10.0,error="0.1").value   == 10.0
            assert Measure(unit="5 m^2", value=10.0,error="0.1").error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(unit="5 m^2", value=10.0,error="0.1").implied == False
            assert Measure(unit="5 m^2", value=10.0,error="0.1").units.symbols   == Unit("5 m^2").symbols
            assert Measure(unit="5 m^2", value=10.0,error="0.1").units.magnitude == Unit("5 m^2").magnitude
        # Unit Unit
        if(True): 
          # Str Value, Str Unit, Str Err
          if(True):
            assert Measure(unit=Unit("cm"),value="2",error="0.1").value   == Decimal("2")
            assert Measure(unit=Unit("cm"),value="2",error="0.1").error   == Decimal("0.1")
            assert Measure(unit=Unit("cm"),value="2",error="0.1").implied == False
            assert Measure(unit=Unit("cm"),value="2",error="0.1").units.symbols   == Unit("cm").symbols
            assert Measure(unit=Unit("cm"),value="2",error="0.1").units.magnitude == Unit("cm").magnitude
          # Decimal Value, Str Unit, Str Err
          if(True):
            assert Measure(unit=Unit("M^2"), value=Decimal("10.1"),error="0.1").value   == Decimal("10.1")
            assert Measure(unit=Unit("M^2"), value=Decimal("10.1"),error="0.1").error   == Decimal("0.1")
            assert Measure(unit=Unit("M^2"), value=Decimal("10.1"),error="0.1").implied == False
            assert Measure(unit=Unit("M^2"), value=Decimal("10.1"),error="0.1").units.symbols   == Unit("M^2").symbols
            assert Measure(unit=Unit("M^2"), value=Decimal("10.1"),error="0.1").units.magnitude == Unit("M^2").magnitude
          # int Value, Str Unit, Str Err
          if(True):
            assert Measure(unit=Unit("$"),value=2,error="0.1").value   == Decimal(2)
            assert Measure(unit=Unit("$"),value=2,error="0.1").error   == Decimal("0.1")
            assert Measure(unit=Unit("$"),value=2,error="0.1").implied == False
            assert Measure(unit=Unit("$"),value=2,error="0.1").units.symbols   == Unit("$").symbols
            assert Measure(unit=Unit("$"),value=2,error="0.1").units.magnitude == Unit("$").magnitude
          # float Value, Str Unit, Str Err
          if(True):
            assert Measure(unit=Unit("5 m^2"), value=10.0,error="0.1").value   == 10.0
            assert Measure(unit=Unit("5 m^2"), value=10.0,error="0.1").error   == 0.1 # Due to Value-Error Type Correction
            assert Measure(unit=Unit("5 m^2"), value=10.0,error="0.1").implied == False
            assert Measure(unit=Unit("5 m^2"), value=10.0,error="0.1").units.symbols   == Unit("5 m^2").symbols
            assert Measure(unit=Unit("5 m^2"), value=10.0,error="0.1").units.magnitude == Unit("5 m^2").magnitude
    
  def test_init_cast(self):
    # Measure Input
    if(True):
      assert Measure(Measure(value=2,units="cm")).value == Decimal(2)
      assert Measure(Measure(value=2,units="cm")).units == Unit("cm")
      assert Measure(Measure(value=2,units="cm")).error == Decimal("0.5")
      assert Measure(Measure(value=2,units="cm")).implied == True
    # Unit as input
    assert Measure("cm/min").value == Decimal("1")
    assert Measure("cm/min").units == Unit("cm/min")
    assert Measure("cm/min").error == Decimal("0.5")
    assert Measure("cm/min").implied == True
  
  def test_init_fail(self):
    # To-Do:
    # Implicit
    # Explicit
    
    
    
    # No Value
    with pytest.raises(Exception):
      Measure()
      Measure(None)
      Measure("")
    # conflicting units input
    with pytest.raises(Exception):
      Measure("5 m^2","2 m^2")
    with pytest.raises(Exception):
      Measure("5 m^2",units="cm")
    with pytest.raises(Exception):
      Measure("5","m^2",units="cm")
    # conflicting value input
    with pytest.raises(Exception):
      Measure("3","cm",value="2")
    with pytest.raises(Exception):
      Measure("2","3","cm")
    with pytest.raises(Exception):
      assert Measure("5",value="2")
    # Bad Keyword
    with pytest.raises(Exception):
      Measure("2 cm",yellow="red")
  
  def test_convert(self):
    # Conversions to Base Units
    if(True):
      # From Prefix Unit with Implied Error
      assert Measure("24cm").convert("m").value == Decimal(".24")
      assert Measure("24cm").convert("m").units == Unit("m")
      assert Measure("24cm").convert("m").error == Decimal(".005")
      assert Measure("24cm").convert("m").implied == True
      # From Prefix Unit with Explicit Error
      assert Measure("24(3)cm").convert("m").value == Decimal(".24")
      assert Measure("24(3)cm").convert("m").error == Decimal(".03")
      assert Measure("24(3)cm").convert("m").units == Unit("m")
      assert Measure("24(3)cm").convert("m").implied == False
      # From Magnitude And Prefix
      assert Measure("24 10^3 cm").convert("m").value == Decimal("240")
      assert Measure("24 10^3 cm").convert("m").units == Unit("m")
      assert Measure("24 10^3 cm").convert("m").error == Decimal("5")
      assert Measure("24 10^3 cm").convert("m").implied == True
    # Conversion to Prefix Unit
    if(True):
      # From Prefix Unit with Implied Error
      assert Measure("24cm").convert("mm").value == Decimal("240")
      assert Measure("24cm").convert("mm").units == Unit("mm")
      assert Measure("24cm").convert("mm").error == Decimal("5")
      assert Measure("24cm").convert("mm").implied == True
      # From Prefix Unit with Explicit Error
      assert Measure("24(3)cm").convert("mm").value == Decimal("240")
      assert Measure("24(3)cm").convert("mm").error == Decimal("30")
      assert Measure("24(3)cm").convert("mm").units == Unit("mm")
      assert Measure("24(3)cm").convert("mm").implied == False
      # From Magnitude And Prefix
      assert Measure("24 10^3 cm").convert("mm").value == Decimal("240000")
      assert Measure("24 10^3 cm").convert("mm").units == Unit("mm")
      assert Measure("24 10^3 cm").convert("mm").error == Decimal("5000")
      assert Measure("24 10^3 cm").convert("mm").implied == True
    # Conversion to Magnitude Units
    if(True):
      # From Prefix Unit with Implied Error
      assert Measure("24cm").convert("10 m").value == Decimal("0.024")
      assert Measure("24cm").convert("10 m").units == Unit("10 m")
      assert Measure("24cm").convert("10 m").error == Decimal("0.0005")
      assert Measure("24cm").convert("10 m").implied == True
      # From Prefix Unit with Explicit Error
      assert Measure("24(3)cm").convert("10 m").value == Decimal("0.024")
      assert Measure("24(3)cm").convert("10 m").error == Decimal("0.003")
      assert Measure("24(3)cm").convert("10 m").units == Unit("10 m")
      assert Measure("24(3)cm").convert("10 m").implied == False
      # From Magnitude And Prefix
      assert Measure("24 10^3 cm").convert("10 m").value == Decimal("24")
      assert Measure("24 10^3 cm").convert("10 m").units == Unit("10 m")
      assert Measure("24 10^3 cm").convert("10 m").error == Decimal("0.5")
      assert Measure("24 10^3 cm").convert("10 m").implied == True
    # Conversion to Magnitude Prefix
    if(True):
      # From Prefix Unit with Implied Error
      assert Measure("24cm").convert("10 mm").value == Decimal("24")
      assert Measure("24cm").convert("10 mm").units == Unit("10 mm")
      assert Measure("24cm").convert("10 mm").error == Decimal("0.5")
      assert Measure("24cm").convert("10 mm").implied == True
      # From Prefix Unit with Explicit Error
      assert Measure("24(3)cm").convert("10 mm").value == Decimal("24")
      assert Measure("24(3)cm").convert("10 mm").error == Decimal("3")
      assert Measure("24(3)cm").convert("10 mm").units == Unit("10 mm")
      assert Measure("24(3)cm").convert("10 mm").implied == False
      # From Magnitude And Prefix
      assert Measure("24 10^3 cm").convert("10 mm").value == Decimal("24000")
      assert Measure("24 10^3 cm").convert("10 mm").units == Unit("10 mm")
      assert Measure("24 10^3 cm").convert("10 mm").error == Decimal("500")
      assert Measure("24 10^3 cm").convert("10 mm").implied == True
    # Conversion To and From Function Units 
    if(True):
      # From Fahrenheit to Celsius
      if(True):
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("\u00B0C").value == Decimal("5")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("\u00B0C").units == Unit("\u00B0C")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("\u00B0C").error < Decimal("0.278")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("\u00B0C").error > Decimal("0.276")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("\u00B0C").implied == True
        # From Fahrenheit to milli-Celsius
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("m\u00B0C").value == Decimal("5000")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("m\u00B0C").units == Unit("m\u00B0C")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("m\u00B0C").error < Decimal("277.778")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("m\u00B0C").error > Decimal("277.776")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("m\u00B0C").implied == True
        # From Fahrenheit to 10 Celsius
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("10 \u00B0C").value == Decimal("0.5")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("10 \u00B0C").units == Unit("10 \u00B0C")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("10 \u00B0C").error < Decimal("0.027778")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("10 \u00B0C").error > Decimal("0.027776")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("10 \u00B0C").implied == True
      # From Fahrenheit to Kelvin
      if(True):
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("K").value == Decimal("278.15")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("K").units == Unit("K")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("K").error > Decimal("0.277776")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("K").error < Decimal("0.277778")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("K").implied == True
        # From Fahrenheit to milliKelvin
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("mK").value == Decimal("278150")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("mK").units == Unit("mK")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("mK").error > Decimal("277.776")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("mK").error < Decimal("277.778")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("mK").implied == True
        # From Fahrenheit to 10 Kelvin
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("10 K").value == Decimal("27.815")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("10 K").units == Unit("10 K")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("10 K").error > Decimal("0.0277776")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("10 K").error < Decimal("0.0277778")
        assert Measure(value="41", units=Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).convert("10 K").implied == True
      # From Celsius to Fahrenheit
      if(True):
        # Defined in Convert
        assert Measure(value="25", units="\u00B0C").convert(Unit("\u00B0F"),Unit.IMPERIAL_UNITS).value == Decimal("77")
        assert Measure(value="25", units="\u00B0C").convert(Unit("\u00B0F"),Unit.IMPERIAL_UNITS).units == Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)
        assert Measure(value="25", units="\u00B0C").convert(Unit("\u00B0F"),Unit.IMPERIAL_UNITS).error == Decimal("0.9")
        assert Measure(value="25", units="\u00B0C").convert(Unit("\u00B0F"),Unit.IMPERIAL_UNITS).implied == True
        # Defined Unit
        assert Measure(value="25", units="\u00B0C").convert(Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).value == Decimal("77")
        assert Measure(value="25", units="\u00B0C").convert(Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).units == Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)
        assert Measure(value="25", units="\u00B0C").convert(Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).error == Decimal("0.9")
        assert Measure(value="25", units="\u00B0C").convert(Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).implied == True
        # From Celsius to 10 Fahrenheit
        assert Measure(value="25", units="\u00B0C").convert(Unit("10 \u00B0F",definitions = Unit.IMPERIAL_UNITS)).value == Decimal("7.7")
        assert Measure(value="25", units="\u00B0C").convert(Unit("10 \u00B0F",definitions = Unit.IMPERIAL_UNITS)).units == Unit("10 \u00B0F",definitions = Unit.IMPERIAL_UNITS)
        assert Measure(value="25", units="\u00B0C").convert(Unit("10 \u00B0F",definitions = Unit.IMPERIAL_UNITS)).error == Decimal("0.09")
        assert Measure(value="25", units="\u00B0C").convert(Unit("10 \u00B0F",definitions = Unit.IMPERIAL_UNITS)).implied == True
        # From  milli-Celsius to Fahrenheit
        assert Measure(value="25000", units="m\u00B0C").convert(Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).value == Decimal("77")
        assert Measure(value="25000", units="m\u00B0C").convert(Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).units == Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)
        assert Measure(value="25000", units="m\u00B0C").convert(Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).error == Decimal("0.9")
        assert Measure(value="25000", units="m\u00B0C").convert(Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).implied == True
        # From 10 Celsius to Fahrenheit
        assert Measure(value="2.5", units="10 \u00B0C").convert(Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).value == Decimal("77")
        assert Measure(value="2.5", units="10 \u00B0C").convert(Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).units == Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)
        assert Measure(value="2.5", units="10 \u00B0C").convert(Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).error == Decimal("0.9")
        assert Measure(value="2.5", units="10 \u00B0C").convert(Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)).implied == True
      # From Celsius to Kelvin
      if(True):
        assert Measure(value="25", units="\u00B0C").convert("K").value == Decimal("298.15")
        assert Measure(value="25", units="\u00B0C").convert("K").units == Unit("K")
        assert Measure(value="25", units="\u00B0C").convert("K").error == Decimal("0.5")
        assert Measure(value="25", units="\u00B0C").convert("K").implied == True
        # From Celsius to milliKelvin
        assert Measure(value="25", units="\u00B0C").convert("mK").value == Decimal("298150")
        assert Measure(value="25", units="\u00B0C").convert("mK").units == Unit("mK")
        assert Measure(value="25", units="\u00B0C").convert("mK").error == Decimal("500")
        assert Measure(value="25", units="\u00B0C").convert("mK").implied == True
        # From Celsius to 10 Kelvin
        assert Measure(value="25", units="\u00B0C").convert("10 K").value == Decimal("29.815")
        assert Measure(value="25", units="\u00B0C").convert("10 K").units == Unit("10 K")
        assert Measure(value="25", units="\u00B0C").convert("10 K").error == Decimal("0.05")
        assert Measure(value="25", units="\u00B0C").convert("10 K").implied == True
        # From  milli-Celsius to Kelvin
        assert Measure(value="25000", units="m\u00B0C").convert("K").value == Decimal("298.15")
        assert Measure(value="25000", units="m\u00B0C").convert("K").units == Unit("K")
        assert Measure(value="25000", units="m\u00B0C").convert("K").error == Decimal("0.5")
        assert Measure(value="25000", units="m\u00B0C").convert("K").implied == True
        # From 10 Celsius to Kelvin
        assert Measure(value="2.5", units="10 \u00B0C").convert("K").value == Decimal("298.15")
        assert Measure(value="2.5", units="10 \u00B0C").convert("K").units == Unit("K")
        assert Measure(value="2.5", units="10 \u00B0C").convert("K").error == Decimal("0.5")
        assert Measure(value="2.5", units="10 \u00B0C").convert("K").implied == True
        # From 100 milli-Celsius to 10 kiloKelvin
        assert Measure(value="250", units="100 m\u00B0C").convert("kK").value == Decimal("0.29815")
        assert Measure(value="250", units="100 m\u00B0C").convert("kK").units == Unit("kK")
        assert Measure(value="250", units="100 m\u00B0C").convert("kK").error == Decimal("0.0005")
        assert Measure(value="250", units="100 m\u00B0C").convert("kK").implied == True
      # pH Tests
      if(True):
        # Note: Unit("M") == Unit("10^3 * mol / m^3")
        assert Measure("pH 7").units == Unit("pH",Unit.CONCENTRATION_UNITS)
        assert Measure("pH 7").value == Decimal("7")
        assert Measure("pH 7").units.get_base() == Unit("mol / m^3")
        assert Measure("pH 7").units.magnitude == 1
        assert Measure("pH 7").convert("M").value == Decimal("10")**Decimal("-7")
        assert Measure("pH 7").convert("M").unit == Unit("M")
        assert str(Measure("pH 7")) == "pH 7"
        # Pico Hertz still works
        assert Measure("1e12 pH") == Measure("1 H")
        
    # Simplify
    if(True):
      assert Measure("26.85 \u00B0C").simplify().value == Decimal("300")
      assert Measure("26.85 \u00B0C").simplify().units == Unit("K")
      assert Measure("26.85 \u00B0C").simplify().error == Decimal("0.005")
      assert Measure("26.85 \u00B0C").simplify().implied == True
    # Definitions
    if(True):
      # Todo, To-Do
      #x = Measure("1 lbf" ,Unit.IMPERIAL_UNITS)
      #y = Measure("1 in^2",Unit.IMPERIAL_UNITS)
      #i = (x/y).convert("psi",Unit.PRESSURE_UNITS)
      pass
    # UnitExceptions 
    if(True):
      with pytest.raises(IncompatibleUnitException):
        Measure("12 mg").convert("uL")
  
  def test_hash(self):
    hash(Measure("5 m^3"))
  