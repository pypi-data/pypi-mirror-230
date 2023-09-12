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
  import unitment 

# To-Do add Numpy Tests
# https://numpy.org/doc/stable/reference/ufuncs.html

# Units
"""
from tests.maths.measure.unit_init import *
from tests.maths.measure.unit_str  import *
from tests.maths.measure.unit_op   import *
# Measures
from tests.maths.measure.meas_init import *
from tests.maths.measure.meas_str  import *
from tests.maths.measure.meas_op   import *
#"""
# Testing Protocol 
# pytest tests/maths/measure.py
# coverage run -m pytest tests/maths/measure.py
# coverage report -m 

class TestUnit:
  # If this is failing you have init problems. 
  if(True): UNITS = (
    Unit(["u"]),Unit(["u","u"]),Unit(["ua","ub","ub"]),
    Unit(["nu"],["du"]),Unit(["nu","nu","nu"],["du","du"]),Unit(["nua","nub","nub"],["dua","dub","dub","dub"]),
    Unit(["u"],10.1),Unit(["u","u"],10.1),Unit(["ua","ub","ub"],10.1),
    Unit(["nu"],["du"],10.1),Unit(["nu","nu","nu"],["du","du"],10.1),Unit(["nua","nub","nub"],["dua","dub","dub","dub"],10.1),
    Unit(["u"],10e1),Unit(["u","u"],10e1),Unit(["ua","ub","ub"],10e1),
    Unit(["nu"],["du"],10e1),Unit(["nu","nu","nu"],["du","du"],10e1),Unit(["nua","nub","nub"],["dua","dub","dub","dub"],10e1),
    Unit(["u"],-10.1),Unit(["u","u"],-10.1),Unit(["ua","ub","ub"],-10.1),
    Unit(["nu"],["du"],-10.1),Unit(["nu","nu","nu"],["du","du"],-10.1),Unit(["nua","nub","nub"],["dua","dub","dub","dub"],-10.1),
    Unit(["u"],-10e1),Unit(["u","u"],-10e1),Unit(["ua","ub","ub"],-10e1),
    Unit(["nu"],["du"],-10e1),Unit(["nu","nu","nu"],["du","du"],-10e1),Unit(["nua","nub","nub"],["dua","dub","dub","dub"],-10e1),
    Unit(["u"],"10.1"),Unit(["u","u"],"10.1"),Unit(["ua","ub","ub"],"10.1"),
    Unit(["nu"],["du"],"10.1"),Unit(["nu","nu","nu"],["du","du"],"10.1"),Unit(["nua","nub","nub"],["dua","dub","dub","dub"],"10.1"),
    Unit(["u"],"10e1"),Unit(["u","u"],"10e1"),Unit(["ua","ub","ub"],"10e1"),
    Unit(["nu"],["du"],"10e1"),Unit(["nu","nu","nu"],["du","du"],"10e1"),Unit(["nua","nub","nub"],["dua","dub","dub","dub"],"10e1"),
    Unit(["u"],"-10.1"),Unit(["u","u"],"-10.1"),Unit(["ua","ub","ub"],"-10.1"),
    Unit(["nu"],["du"],"-10.1"),Unit(["nu","nu","nu"],["du","du"],"-10.1"),Unit(["nua","nub","nub"],["dua","dub","dub","dub"],"-10.1"),
    Unit(["u"],"-10e1"),Unit(["u","u"],"-10e1"),Unit(["ua","ub","ub"],"-10e1"),
    Unit(["nu"],["du"],"-10e1"),Unit(["nu","nu","nu"],["du","du"],"-10e1"),Unit(["nua","nub","nub"],["dua","dub","dub","dub"],"-10e1"),
    Unit(10),Unit(-10),Unit(10.1),Unit(10e1),Unit(-10.1),Unit(-10e1),
    Unit("10.1"),Unit("10e1"),Unit("-10.1"),Unit("-10e1"),
    Unit(Decimal("10.1")),Unit(Decimal("10e1")),Unit(Decimal("-10.1")),Unit(Decimal("-10e1")),
    )
  else: UNITS = ()
  
class TestPracticals:
  
  def test_examples(self):
    assert Unit("1e6 fish").magnitude == Unit("fish", magnitude=1e6).magnitude == Unit("1000000 fish").magnitude == Unit("10^6 fish").magnitude
    assert Unit("m/s").symbols == Unit("m s^-1").symbols == Unit(numerators=("m",),denominators=("s",)).symbols == Unit(numerators=(("m",1),),denominators=(("s",1),)).symbols == Unit(symbols=(("m",1),("s",-1),)).symbols
    
    
    weird_unit_dict = {
      # Symbol      Mult              Base-Symbol   Function
      'mu'       : ( Decimal("1e-3"), (('u',1),),  None),
      'ku'       : ( Decimal("1e3"),  (('u',1),),  None),
      }
    assert Measure("5 ku",weird_unit_dict).convert("u").value == Decimal("5e3")
    assert Measure("5 ku",weird_unit_dict).convert("mu",weird_unit_dict).value == Decimal("5e6")
    
    weird_unit_dict = {
      # Symbol      Mult             Base-Symbol   Function
      'u'       : ( Decimal(1),      (('kg',-1),),  None),
      'v'       : ( Decimal("1e3"),  (('s',-2),),  None),
      }
    assert Measure("5 u",weird_unit_dict).convert("kg-1") == Measure("5 kg-1")
    assert Measure("5 v",weird_unit_dict).convert("s-2") == Measure("5e3 s-2")
    
    
    
    def DECIBEL_SELECTOR(exponent):
      """
      In non-under-water Acoustics the decible is defined as follows: 
        dB = 20 log10( value / 20 uPa )
      In base units: 
        dB = 20 log10( value / (20e-6 kg^1 m^-1 s^-2 ) )
      
      To reverse this calculation solve for the initial value: 
        value = 10^(dB / 20) * 20e-6 kg^1 m^-1 s^-2
      """
      
      # Decibel Functions
      def NUMERATOR_FROM_DECIBEL_TO_BASE(val):
        val,scale,ref = unitment._type_corrections_(val,Decimal("20"),Decimal("20e-6"))
        return 10**(val/scale) * ref
      def NUMERATOR_TO_DECIBEL_FROM_BASE(val):
        val,scale,ref = unitment._type_corrections_(val,Decimal("20"),Decimal("20e-6"))
        return scale * (val/ref).log10()
      # Most Function Units behave like normal units when on the denominator.
      def DENOMINATOR_FROM_DECIBEL_TO_BASE(val):
        return val
      def DENOMINATOR_TO_DECIBEL_FROM_BASE(val):
        return val
      
      # Select & Return Correct Function
      if(exponent == 0): return (lambda x:x,lambda x:x)
      if(exponent == 1):  return (   NUMERATOR_FROM_DECIBEL_TO_BASE ,   NUMERATOR_TO_DECIBEL_FROM_BASE )
      if(exponent == -1): return ( DENOMINATOR_FROM_DECIBEL_TO_BASE , DENOMINATOR_TO_DECIBEL_FROM_BASE )
      else:
        raise ValueError(f"Failed to Decompose: Exponent of dB != 1,0,-1. Cannot Deconvolute.")
    
    dB_dict = {
      # Symbol      Mult        Base-Symbol                    Function
      'dB'       : ( 1,         (('kg',1),('m',-1),('s',-2)),  DECIBEL_SELECTOR),
      }
    
    assert Measure("5 dB",dB_dict).convert("uPa").value == (Decimal(10)**(Decimal(5)/Decimal(20)))*Decimal("20")
    
  
  # To-Do: This failed.
  # R  = Measure("8.31446261815324 J K-1 mol-1")
  # R  = Measure("8.31446261815324 J K-1 mol-1")
  # R  = Measure("8.31446261815324 J⋅K-1⋅mol-1")
  # R  = Measure("8.31446261815324 J⋅K−1⋅mol−1")
  # To-DO: This Failed
  # N_A  = Measure("6.02214076 × 10^23")
  # N_A  = Measure("6.02214076 * 10^23")
  
  # Assorted Past Failures
  def test_failures(self):
    Measure("6.02214076 × 10^23")
    Measure("6.02214076 * 10^23")
    # Past Failed Units
    pass
    
  # Exact Unit Conversion.
  def test_conversion_constants(self):
    
    # Pound (lb,lbf), Inch (in), psi Definitions
    lbf = Measure("1 lbf",Unit.IMPERIAL_UNITS)
    in2 = Measure("1 in^2",Unit.IMPERIAL_UNITS)
    psi = (lbf/in2).convert("psi",Unit.PRESSURE_UNITS)
    assert psi.value == 1
    
    # Distance
    assert Measure("12 in",Unit.IMPERIAL_UNITS).convert("ft",Unit.IMPERIAL_UNITS).value == 1
    assert Measure("12 in",Unit.IMPERIAL_UNITS).convert(Unit("ft",Unit.IMPERIAL_UNITS)).value == 1
  
  def test_challenge_problems(self):
    assert Measure("10 K^-1") * Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS) == Decimal("2559.277777777777777777777778")