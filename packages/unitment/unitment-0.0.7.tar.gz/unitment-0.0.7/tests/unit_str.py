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

class TestUnitStr:
  
  # To-Do: This failed.
  
  
  
  def test_parse(self):
    # Exponents of Different Forms
    assert Unit("10 u").symbols      == (('u', Decimal('1')),)
    assert Unit("10 u").magnitude    == 10
    assert Unit("10^2 u").symbols    == (('u', Decimal('1')),)
    assert Unit("10^2 u").magnitude  == 100
    assert Unit("10**2 u").symbols   == (('u', Decimal('1')),)
    assert Unit("10**2 u").magnitude == 100
    # Explicit Dividers
    assert Unit("10^5 cm3/mol")        == Unit(["cm","cm","cm"],["mol"],"1e5")
    assert Unit("10^5 cm3 / mol")      == Unit(["cm","cm","cm"],["mol"],"1e5")
    assert Unit("10^5 cm^3 / mol")     == Unit(["cm","cm","cm"],["mol"],"1e5")
    # Explicit Dividers with Multiplication
    assert Unit("10^5 cm^3 / a * mol") == Unit(["cm","cm","cm", "mol"],["a"],"1e5")
    assert Unit("10^5 cm^3 / a mol")   == Unit(["cm","cm","cm"],["a", "mol"],"1e5")
    assert Unit("10^5 M g/mol")        == Unit(["M","g"],["mol"],"1e5")
    assert Unit("31415 M g/mol")       == Unit(["M","g"],["mol"],"31415")
    # Negative Exponents
    assert Unit("10^5 cm^3 * mol^-1")  == Unit(["cm","cm","cm"],["mol"],"1e5")
    assert Unit("10^5 cm^3 mol^-1")    == Unit(["cm","cm","cm"],["mol"],"1e5")
    assert Unit("10^5 cm3mol-1")       == Unit(["cm","cm","cm"],["mol"],"1e5")
    # No-Space Multipliers
    assert Unit("10^5 cm3mol")         == Unit(["cm","cm","cm","mol"],[],"1e5")
    # Multiple Dividers
    assert Unit("10^5 cm^3 / a / mol") == Unit(["cm","cm","cm"],["a","mol"],"1e5")
    # Magnitude Multipliers
    assert Unit("10^5 M g/mol")             == Unit(["M","g"],["mol"],"1e5")
    assert Unit("3.14 M g/mol")             == Unit(["M","g"],["mol"],"3.14")
    assert Unit("3.14x10^5 M g/mol")        == Unit(["M","g"],["mol"],"3.14e5")
    assert Unit("3.14 x 10^5 M g/mol")      == Unit(["M","g"],["mol"],"3.14e5")
    assert Unit("3.14*10^5 M g/mol")        == Unit(["M","g"],["mol"],"3.14e5")
    assert Unit("3.14 * 10^5 M g/mol")      == Unit(["M","g"],["mol"],"3.14e5")
    assert Unit("3.14*10^5 * M g/mol")      == Unit(["M","g"],["mol"],"3.14e5")
    assert Unit("3.14\u00B710^5 M g/mol")   == Unit(["M","g"],["mol"],"3.14e5")
    assert Unit("3.14\u00D710^5 M g/mol")   == Unit(["M","g"],["mol"],"3.14e5")
    # Multipliers in Units
    assert Unit("3.14 M \u00D7 g / mol ") == Unit(["M","g"],["mol"],"3.14")
    assert Unit("3.14 M \u00B7 g / mol ") == Unit(["M","g"],["mol"],"3.14")
    assert Unit("3.14 M \u22C5 g / mol ") == Unit(["M","g"],["mol"],"3.14")
    # Limit x as Multiplier to Magnitude
    assert Unit("12*10^4 x U b") == Unit(["x","U","b"],[],"1.2e5")
    # Permit Magnitude Multiplier in Measure("24(3)*10^3 cm")
    assert Unit("*10^3 cm") == Unit("10^3 cm") 
    assert Unit("*10^3 cm").magnitude == Decimal("1e3")
    # Empty numerators or denominators
    assert Unit("1/m2") == Unit([],["m","m"],1)
    assert Unit("m^-2") == Unit([],["m","m"],1)
    assert Unit("m-2") == Unit([],["m","m"],1)
    assert Unit("m\u22122") == Unit([],["m","m"],1)
    assert Unit("m2")   == Unit(["m","m"],[],1)
    assert Unit("m^2")  == Unit(["m","m"],[],1)
    # Magnitude
    assert Unit("10^6 $") == Unit(numerators=["$"],magnitude=Decimal("1e6"))
    # Extra Spaces
    assert Unit("10^5  cm^3  /  a  *  mol") == Unit(["cm","cm","cm", "mol"],["a"],"1e5")
  def test_str(self):
    # explicit_exponents,explicit_mult,negative_exponents
    the_unit = Unit(["cm","cm","cm","a"],["mol"],1)
    assert the_unit.to_string(True, True, True) == "a * cm^3 * mol^-1"
    the_unit = Unit(["cm","cm","cm","a"],["mol"],1)
    assert the_unit.to_string(False, False, False) == "a cm3 / mol"
    the_unit = Unit(["cm","cm","cm","a"],["mol"],1)
    assert the_unit.to_string(True, False, False) == "a cm^3 / mol"
    the_unit = Unit(["cm","cm","cm","a"],["mol"],1)
    assert the_unit.to_string(False, False, True) == "a cm3 mol-1"
    the_unit = Unit(["cm","cm","cm","a"],["mol"],1)
    assert the_unit.to_string(False, True, False) == "a * cm3 / mol"
    the_unit = Unit(["cm","cm","cm","a"],["mol"],1)
    assert the_unit.to_string(True, False, True) == "a cm^3 mol^-1" 
    the_unit = Unit(["cm","cm","cm","a"],["mol"],1)
    assert the_unit.to_string(False, True, True) == "a * cm3 * mol-1"
    the_unit = Unit(["cm","cm","cm","a"],["mol"],1)
    assert the_unit.to_string(True, True, False) == "a * cm^3 / mol"
    # Empry numerators or denominators
    assert str(Unit(None))==""
    the_unit = Unit(["m","m"],[],1)
    assert the_unit.to_string(True,True,False) == "m^2"
    the_unit = Unit([],["m","m"],1)
    assert the_unit.to_string(True,True,False) == "1 / m^2"
    # Verify Immutability
    x=Unit("mm")
    y = x.to_string()
    assert x == Unit("mm")
  def test_scientific_form(self):
    assert Unit.scientific_form(Decimal(".012345" )) == "1.2345·10^-2"
    assert Unit.scientific_form(Decimal(".12345"  )) == "1.2345·10^-1"
    assert Unit.scientific_form(Decimal("1.2345"  )) == "1.2345"
    assert Unit.scientific_form(Decimal("12.345"  )) == "1.2345·10^1"
    assert Unit.scientific_form(Decimal("123.45"  )) == "1.2345·10^2"
    assert Unit.scientific_form(Decimal("1234.5"  )) == "1.2345·10^3"
    assert Unit.scientific_form(Decimal("12345"   )) == "1.2345·10^4"
    assert Unit.scientific_form(Decimal("12345.0" )) == "1.2345·10^4"
    assert Unit.scientific_form(Decimal("12345.00")) == "1.2345·10^4"
    assert Unit.scientific_form(Decimal("10000"   )) == "10^4"
  
  
  