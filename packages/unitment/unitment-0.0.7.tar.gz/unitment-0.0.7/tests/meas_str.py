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

class TestMeasureStr:
  
  # Test 0.0 with implied error for Reversibility
  
  
  def test_parse(self):
    # Note: Any additions here should be made to test_str String Parser Reversibility 
    # No Error Notation
    if(True):
      assert Measure("24cm").value == Decimal("24")
      assert Measure("24cm").units == Unit("cm")
      assert Measure("24cm").error == Decimal("0.5")
      assert Measure("24cm").implied == True
      # Exponents
      if(True):
        assert Measure("10^2 u").value == 100
        assert Measure("10**2 u").value == 100
      # End with Zero
      if(True):
        assert Measure("240cm").value == Decimal("240")
        assert Measure("240cm").units == Unit("cm")
        assert Measure("240cm").error == Decimal("5")
        assert Measure("240cm").implied == True
      # E notation
      if(True):
        assert Measure("2.4e-3cm").value == Decimal("2.4e-3")
        assert Measure("2.4e-3cm").units == Unit("cm")
        assert Measure("2.4e-3cm").error == Decimal("0.05e-3")
        assert Measure("2.4e-3cm").implied == True
      # Preceding Units
      if(True):
        assert Measure("$2.4e-3").value == Decimal("2.4e-3")
        assert Measure("$2.4e-3").units == Unit("$")
        assert Measure("$2.4e-3").error == Decimal("0.05e-3")
        assert Measure("$2.4e-3").implied == True
        
        assert Measure("$ 2.4e-3").value == Decimal("2.4e-3")
        assert Measure("$ 2.4e-3").units == Unit("$")
        assert Measure("$ 2.4e-3").error == Decimal("0.05e-3")
        assert Measure("$ 2.4e-3").implied == True
      # Zero Value
      if(True):
        assert Measure("0cm").value == Decimal("0")
        assert Measure("0cm").units == Unit("cm")
        assert Measure("0cm").error == Decimal("0.5")
        assert Measure("0cm").implied == True
      # Parse Magnitude
      if(True):
        # Magnitude without Multiplier
        assert Measure("24 10^3 cm").value == Decimal("24")
        assert Measure("24 10^3 cm").units == Unit("10^3 cm")
        assert Measure("24 10^3 cm").error == Decimal("0.5")
        assert Measure("24 10^3 cm").implied == True
        # Magnitude with * Multiplier
        assert Measure("24 * 10^3 cm").value == Decimal("24")
        assert Measure("24 * 10^3 cm").units == Unit("10^3 cm")
        assert Measure("24 * 10^3 cm").error == Decimal("0.5")
        assert Measure("24 * 10^3 cm").implied == True
        # Magnitude with x Multiplier
        assert Measure("24 x 10^3 cm").value == Decimal("24")
        assert Measure("24 x 10^3 cm").units == Unit("10^3 cm")
        assert Measure("24 x 10^3 cm").error == Decimal("0.5")
        assert Measure("24 x 10^3 cm").implied == True
        # Magnitude with \u00B7 Multiplier
        assert Measure("24 \u00B7 10^3 cm").value == Decimal("24")
        assert Measure("24 \u00B7 10^3 cm").units == Unit("10^3 cm")
        assert Measure("24 \u00B7 10^3 cm").error == Decimal("0.5")
        assert Measure("24 \u00B7 10^3 cm").implied == True
        # Magnitude with \u00D7 Multiplier
        assert Measure("24 \u00D7 10^3 cm").value == Decimal("24")
        assert Measure("24 \u00D7 10^3 cm").units == Unit("10^3 cm")
        assert Measure("24 \u00D7 10^3 cm").error == Decimal("0.5")
        assert Measure("24 \u00D7 10^3 cm").implied == True
        # Magnitude with x Multiplier No Spaces
        assert Measure("24x10^3 cm").value == Decimal("24")
        assert Measure("24x10^3 cm").units == Unit("10^3 cm")
        assert Measure("24x10^3 cm").error == Decimal("0.5")
        assert Measure("24x10^3 cm").implied == True
      # Unitless Magnitude
      if(True):
        # Magnitude without Multiplier
        assert Measure("24 10^3").value == Decimal("24")
        assert Measure("24 10^3").units == Unit("10^3")
        assert Measure("24 10^3").error == Decimal("0.5")
        assert Measure("24 10^3").implied == True
        # Magnitude with * Multiplier
        assert Measure("24 * 10^3").value == Decimal("24")
        assert Measure("24 * 10^3").units == Unit("10^3")
        assert Measure("24 * 10^3").error == Decimal("0.5")
        assert Measure("24 * 10^3").implied == True
        # Magnitude with x Multiplier
        assert Measure("24 x 10^3").value == Decimal("24")
        assert Measure("24 x 10^3").units == Unit("10^3")
        assert Measure("24 x 10^3").error == Decimal("0.5")
        assert Measure("24 x 10^3").implied == True
        # Magnitude with \u00B7 Multiplier
        assert Measure("24 \u00B7 10^3").value == Decimal("24")
        assert Measure("24 \u00B7 10^3").units == Unit("10^3")
        assert Measure("24 \u00B7 10^3").error == Decimal("0.5")
        assert Measure("24 \u00B7 10^3").implied == True
        # Magnitude with \u00D7 Multiplier
        assert Measure("24 \u00D7 10^3").value == Decimal("24")
        assert Measure("24 \u00D7 10^3").units == Unit("10^3")
        assert Measure("24 \u00D7 10^3").error == Decimal("0.5")
        assert Measure("24 \u00D7 10^3").implied == True
        # Magnitude with x Multiplier No Spaces
        assert Measure("24x10^3").value == Decimal("24")
        assert Measure("24x10^3").units == Unit("10^3")
        assert Measure("24x10^3").error == Decimal("0.5")
        assert Measure("24x10^3").implied == True
      
      # Unitless
      if(True):
        assert Measure("36").value == Decimal("36")
        assert Measure("36").units == Unit()
        assert Measure("36").error == Decimal("0.5")
        assert Measure("36").implied == True
      
    # Parenthetical Error Notation
    if(True):
      assert Measure("24(3)cm").value == Decimal("24")
      assert Measure("24(3)cm").units == Unit("cm")
      assert Measure("24(3)cm").error == Decimal("3")
      assert Measure("24(3)cm").implied == False
      # End with Zero
      if(True):
        assert Measure("240(3)cm").value == Decimal("240")
        assert Measure("240(3)cm").units == Unit("cm")
        assert Measure("240(3)cm").error == Decimal("30")
        assert Measure("240(3)cm").implied == False
      # E notation
      if(True):
        assert Measure("2.4e-3(22)cm").value == Decimal("2.4e-3")
        assert Measure("2.4e-3(22)cm").error == Decimal("0.0022")
        assert Measure("2.4e-3(22)cm").units == Unit("cm")
        assert Measure("2.4e-3(22)cm").implied == False
      # Preceding Units
      if(True):
        assert Measure("$2.4e-3(22)").value == Decimal("2.4e-3")
        assert Measure("$2.4e-3(22)").units == Unit("$")
        assert Measure("$2.4e-3(22)").error == Decimal("0.0022")
        assert Measure("$2.4e-3(22)").implied == False
      # Zero Value
      if(True):
        assert Measure("0(5)cm").value == Decimal("0")
        assert Measure("0(5)cm").units == Unit("cm")
        assert Measure("0(5)cm").error == Decimal("5")
        assert Measure("0(5)cm").implied == False
      # Parse Magnitude
      if(True):
        # Magnitude without Multiplier
        assert Measure("24(3) 10^3 cm").value == Decimal("24")
        assert Measure("24(3) 10^3 cm").units == Unit("10^3 cm")
        assert Measure("24(3) 10^3 cm").error == Decimal("3")
        assert Measure("24(3) 10^3 cm").implied == False
        # Magnitude with * Multiplier
        assert Measure("24(3) * 10^3 cm").value == Decimal("24")
        assert Measure("24(3) * 10^3 cm").units == Unit("10^3 cm")
        assert Measure("24(3) * 10^3 cm").error == Decimal("3")
        assert Measure("24(3) * 10^3 cm").implied == False
        # Magnitude with x Multiplier
        assert Measure("24(3) x 10^3 cm").value == Decimal("24")
        assert Measure("24(3) x 10^3 cm").units == Unit("10^3 cm")
        assert Measure("24(3) x 10^3 cm").error == Decimal("3")
        assert Measure("24(3) x 10^3 cm").implied == False
        # Magnitude with \u00B7 Multiplier
        assert Measure("24(3) \u00B7 10^3 cm").value == Decimal("24")
        assert Measure("24(3) \u00B7 10^3 cm").units == Unit("10^3 cm")
        assert Measure("24(3) \u00B7 10^3 cm").error == Decimal("3")
        assert Measure("24(3) \u00B7 10^3 cm").implied == False
        # Magnitude with \u00D7 Multiplier
        assert Measure("24(3) \u00D7 10^3 cm").value == Decimal("24")
        assert Measure("24(3) \u00D7 10^3 cm").units == Unit("10^3 cm")
        assert Measure("24(3) \u00D7 10^3 cm").error == Decimal("3")
        assert Measure("24(3) \u00D7 10^3 cm").implied == False
        # Magnitude with x Multiplier No Spaces
        assert Measure("24(3)x10^3 cm").value == Decimal("24")
        assert Measure("24(3)x10^3 cm").units == Unit("10^3 cm")
        assert Measure("24(3)x10^3 cm").error == Decimal("3")
        assert Measure("24(3)x10^3 cm").implied == False
      # Unitless
      if(True):
        assert Measure("36(4)").value == Decimal("36")
        assert Measure("36(4)").units == Unit()
        assert Measure("36(4)").error == Decimal("4")
        assert Measure("36(4)").implied == False
    # Plus Minus Error Notation
    if(True):
      assert Measure("12\u00B11cm").value == Decimal("12")
      assert Measure("12\u00B11cm").units == Unit("cm")
      assert Measure("12\u00B11cm").error == Decimal("1")
      assert Measure("12\u00B11cm").implied == False
      # Decimal Error
      if(True):
        assert Measure("12\u00B10.5cm").value == Decimal("12")
        assert Measure("12\u00B10.5cm").units == Unit("cm")
        assert Measure("12\u00B10.5cm").error == Decimal("0.5")
        assert Measure("12\u00B10.5cm").implied == False
      # End with Zero
      if(True):
        assert Measure("10\u00B11cm").value == Decimal("10")
        assert Measure("10\u00B11cm").units == Unit("cm")
        assert Measure("10\u00B11cm").error == Decimal("1")
        assert Measure("10\u00B11cm").implied == False
      # Preceding Units
      if(True):
        assert Measure("$12\u00B11").value == Decimal("12")
        assert Measure("$12\u00B11").units == Unit("$")
        assert Measure("$12\u00B11").error == Decimal("1")
        assert Measure("$12\u00B11").implied == False
      # E notation
      if(True):
        assert Measure("1.2e1\u00B11cm").value == Decimal("12")
        assert Measure("1.2e1\u00B11cm").units == Unit("cm")
        assert Measure("1.2e1\u00B11cm").error == Decimal("1")
        assert Measure("1.2e1\u00B11cm").implied == False
      # Zero Value
      if(True):
        assert Measure("0\u00B11cm").value == Decimal("0")
        assert Measure("0\u00B11cm").units == Unit("cm")
        assert Measure("0\u00B11cm").error == Decimal("1")
        assert Measure("0\u00B11cm").implied == False
      # Parse Magnitude
      if(True):
        # Magnitude without Multiplier
        assert Measure("24\u00B13 10^3 cm").value == Decimal("24")
        assert Measure("24\u00B13 10^3 cm").units == Unit("10^3 cm")
        assert Measure("24\u00B13 10^3 cm").error == Decimal("3")
        assert Measure("24\u00B13 10^3 cm").implied == False
        # Magnitude with * Multiplier
        assert Measure("24\u00B13 * 10^3 cm").value == Decimal("24")
        assert Measure("24\u00B13 * 10^3 cm").units == Unit("10^3 cm")
        assert Measure("24\u00B13 * 10^3 cm").error == Decimal("3")
        assert Measure("24\u00B13 * 10^3 cm").implied == False
        # Magnitude with x Multiplier
        assert Measure("24\u00B13 x 10^3 cm").value == Decimal("24")
        assert Measure("24\u00B13 x 10^3 cm").units == Unit("10^3 cm")
        assert Measure("24\u00B13 x 10^3 cm").error == Decimal("3")
        assert Measure("24\u00B13 x 10^3 cm").implied == False
        # Magnitude with \u00B7 Multiplier
        assert Measure("24\u00B13 \u00B7 10^3 cm").value == Decimal("24")
        assert Measure("24\u00B13 \u00B7 10^3 cm").units == Unit("10^3 cm")
        assert Measure("24\u00B13 \u00B7 10^3 cm").error == Decimal("3")
        assert Measure("24\u00B13 \u00B7 10^3 cm").implied == False
        # Magnitude with \u00D7 Multiplier
        assert Measure("24\u00B13 \u00D7 10^3 cm").value == Decimal("24")
        assert Measure("24\u00B13 \u00D7 10^3 cm").units == Unit("10^3 cm")
        assert Measure("24\u00B13 \u00D7 10^3 cm").error == Decimal("3")
        assert Measure("24\u00B13 \u00D7 10^3 cm").implied == False
        # Magnitude with x Multiplier No Spaces
        assert Measure("24\u00B13x10^3 cm").value == Decimal("24")
        assert Measure("24\u00B13x10^3 cm").units == Unit("10^3 cm")
        assert Measure("24\u00B13x10^3 cm").error == Decimal("3")
        assert Measure("24\u00B13x10^3 cm").implied == False
      # Unitless
      if(True):
        assert Measure("36 \u00B1 4").value == Decimal("36")
        assert Measure("36 \u00B1 4").units == Unit()
        assert Measure("36 \u00B1 4").error == Decimal("4")
        assert Measure("36 \u00B1 4").implied == False
  def test_str(self):
    
    # Error Notations
    if(True):
      # No Error Notation
      if(True):
        assert str(Measure("12cm"))     == "12 cm"
        assert str(Measure("12.34 cm")) == "12.34 cm"
        assert str(Measure(1.1,"cm")) == "1.1 cm" # do I need this and does it inhibit duck typing and what's most important? 
      # Plus-Minus Error Notation
      if(True):
        # Convert Error Notaiton
        assert str(Measure("24(3)cm"))      == "24 ± 3 cm"
        assert str(Measure("240(3)cm"))     == "240 ± 30 cm"
        assert str(Measure("12(10)cm"))     == "12 ± 10 cm"
        # Convert Decimal
        assert str(Measure("2.4e-3(22)cm")) == "0.0024 ± 0.0022 cm" 
        # Preceding Unit
        assert str(Measure("$2.4e-3(22)"))  == "$0.0024 ± 0.0022"
        # Round by Uncertain Places
        assert Measure("12340.001 \u00B1 0.56").to_string(uncertain_places=2,notation=0) == "12340 \u00B1 0.56"
        assert Measure("12345678 \u00B1 3410").to_string(uncertain_places=2,notation=0) == "12345700 \u00B1 3400"
      # Parenthetical Error Notaiton
      if(True):
        assert Measure("12345678(3410)").to_string(uncertain_places=2,notation=1) == "12345700(34)"
        # Rounding Uncertain Places
        assert Measure("12.543(123)cm").to_string(uncertain_places=2,notation=1) == "12.54(12) cm"
    
    # String Parser Reversibility 
    # Note: Any additions here should be made to test_parse
    if(True):
      # No Error Notation
      if(True):
        assert Measure(str(Measure("24cm"))).value == Decimal("24")
        assert Measure(str(Measure("24cm"))).units == Unit("cm")
        assert Measure(str(Measure("24cm"))).error == Decimal("0.5")
        assert Measure(str(Measure("24cm"))).implied == True
        # End with Zero
        if(True):
          assert Measure(str(Measure("240cm"))).value == Decimal("240")
          assert Measure(str(Measure("240cm"))).units == Unit("cm")
          assert Measure(str(Measure("240cm"))).error == Decimal("5")
          assert Measure(str(Measure("240cm"))).implied == True
        # E notation
        if(True):
          assert Measure(str(Measure("2.4e-3cm"))).value == Decimal("2.4e-3")
          assert Measure(str(Measure("2.4e-3cm"))).units == Unit("cm")
          assert Measure(str(Measure("2.4e-3cm"))).error == Decimal("0.05e-3")
          assert Measure(str(Measure("2.4e-3cm"))).implied == True
        # Preceding Units
        if(True):
          assert Measure(str(Measure("$2.4e-3"))).value == Decimal("2.4e-3")
          assert Measure(str(Measure("$2.4e-3"))).units == Unit("$")
          assert Measure(str(Measure("$2.4e-3"))).error == Decimal("0.05e-3")
          assert Measure(str(Measure("$2.4e-3"))).implied == True
        # Zero Value
        if(True):
          assert Measure(str(Measure("0cm"))).value == Decimal("0")
          assert Measure(str(Measure("0cm"))).units == Unit("cm")
          assert Measure(str(Measure("0cm"))).error == Decimal("0.5")
          assert Measure(str(Measure("0cm"))).implied == True
        # Parse Magnitude
        if(True):
          # Magnitude without Multiplier
          assert Measure(str(Measure("24 10^3 cm"))).value == Decimal("24")
          assert Measure(str(Measure("24 10^3 cm"))).units == Unit("10^3 cm")
          assert Measure(str(Measure("24 10^3 cm"))).error == Decimal("0.5")
          assert Measure(str(Measure("24 10^3 cm"))).implied == True
          # Magnitude with * Multiplier
          assert Measure(str(Measure("24 * 10^3 cm"))).value == Decimal("24")
          assert Measure(str(Measure("24 * 10^3 cm"))).units == Unit("10^3 cm")
          assert Measure(str(Measure("24 * 10^3 cm"))).error == Decimal("0.5")
          assert Measure(str(Measure("24 * 10^3 cm"))).implied == True
          # Magnitude with x Multiplier
          assert Measure(str(Measure("24 x 10^3 cm"))).value == Decimal("24")
          assert Measure(str(Measure("24 x 10^3 cm"))).units == Unit("10^3 cm")
          assert Measure(str(Measure("24 x 10^3 cm"))).error == Decimal("0.5")
          assert Measure(str(Measure("24 x 10^3 cm"))).implied == True
          # Magnitude with \u00B7 Multiplier
          assert Measure(str(Measure("24 \u00B7 10^3 cm"))).value == Decimal("24")
          assert Measure(str(Measure("24 \u00B7 10^3 cm"))).units == Unit("10^3 cm")
          assert Measure(str(Measure("24 \u00B7 10^3 cm"))).error == Decimal("0.5")
          assert Measure(str(Measure("24 \u00B7 10^3 cm"))).implied == True
          # Magnitude with \u00D7 Multiplier
          assert Measure(str(Measure("24 \u00D7 10^3 cm"))).value == Decimal("24")
          assert Measure(str(Measure("24 \u00D7 10^3 cm"))).units == Unit("10^3 cm")
          assert Measure(str(Measure("24 \u00D7 10^3 cm"))).error == Decimal("0.5")
          assert Measure(str(Measure("24 \u00D7 10^3 cm"))).implied == True
          # Magnitude with x Multiplier No Spaces
          assert Measure(str(Measure("24x10^3 cm"))).value == Decimal("24")
          assert Measure(str(Measure("24x10^3 cm"))).units == Unit("10^3 cm")
          assert Measure(str(Measure("24x10^3 cm"))).error == Decimal("0.5")
          assert Measure(str(Measure("24x10^3 cm"))).implied == True
        # Unitless
        if(True):
          assert Measure(str(Measure("36"))).value == Decimal("36")
          assert Measure(str(Measure("36"))).units == Unit()
          assert Measure(str(Measure("36"))).error == Decimal("0.5")
          assert Measure(str(Measure("36"))).implied == True
        # Unitless Magnitude
        if(True):
          # Magnitude without Multiplier
          assert Measure(str(Measure("24 10^3"))).value == Decimal("24")
          assert Measure(str(Measure("24 10^3"))).units == Unit("10^3")
          assert Measure(str(Measure("24 10^3"))).error == Decimal("0.5")
          assert Measure(str(Measure("24 10^3"))).implied == True
          # Magnitude with * Multiplier
          assert Measure(str(Measure("24 * 10^3"))).value == Decimal("24")
          assert Measure(str(Measure("24 * 10^3"))).units == Unit("10^3")
          assert Measure(str(Measure("24 * 10^3"))).error == Decimal("0.5")
          assert Measure(str(Measure("24 * 10^3"))).implied == True
          # Magnitude with x Multiplier
          assert Measure(str(Measure("24 x 10^3"))).value == Decimal("24")
          assert Measure(str(Measure("24 x 10^3"))).units == Unit("10^3")
          assert Measure(str(Measure("24 x 10^3"))).error == Decimal("0.5")
          assert Measure(str(Measure("24 x 10^3"))).implied == True
          # Magnitude with \u00B7 Multiplier
          assert Measure(str(Measure("24 \u00B7 10^3"))).value == Decimal("24")
          assert Measure(str(Measure("24 \u00B7 10^3"))).units == Unit("10^3")
          assert Measure(str(Measure("24 \u00B7 10^3"))).error == Decimal("0.5")
          assert Measure(str(Measure("24 \u00B7 10^3"))).implied == True
          # Magnitude with \u00D7 Multiplier
          assert Measure(str(Measure("24 \u00D7 10^3"))).value == Decimal("24")
          assert Measure(str(Measure("24 \u00D7 10^3"))).units == Unit("10^3")
          assert Measure(str(Measure("24 \u00D7 10^3"))).error == Decimal("0.5")
          assert Measure(str(Measure("24 \u00D7 10^3"))).implied == True
          # Magnitude with x Multiplier No Spaces
          assert Measure(str(Measure("24x10^3"))).value == Decimal("24")
          assert Measure(str(Measure("24x10^3"))).units == Unit("10^3")
          assert Measure(str(Measure("24x10^3"))).error == Decimal("0.5")
          assert Measure(str(Measure("24x10^3"))).implied == True
      # Parenthetical Error Notation
      if(True):
        assert Measure(str(Measure("24(3)cm"))).value == Decimal("24")
        assert Measure(str(Measure("24(3)cm"))).units == Unit("cm")
        assert Measure(str(Measure("24(3)cm"))).error == Decimal("3")
        assert Measure(str(Measure("24(3)cm"))).implied == False
        # End with Zero
        if(True):
          assert Measure(str(Measure("240(3)cm"))).value == Decimal("240")
          assert Measure(str(Measure("240(3)cm"))).units == Unit("cm")
          assert Measure(str(Measure("240(3)cm"))).error == Decimal("30")
          assert Measure(str(Measure("240(3)cm"))).implied == False
        # E notation
        if(True):
          assert Measure(str(Measure("2.4e-3(22)cm"))).value == Decimal("2.4e-3")
          assert Measure(str(Measure("2.4e-3(22)cm"))).error == Decimal("0.0022")
          assert Measure(str(Measure("2.4e-3(22)cm"))).units == Unit("cm")
          assert Measure(str(Measure("2.4e-3(22)cm"))).implied == False
        # Preceding Units
        if(True):
          assert Measure(str(Measure("$2.4e-3(22)"))).value == Decimal("2.4e-3")
          assert Measure(str(Measure("$2.4e-3(22)"))).units == Unit("$")
          assert Measure(str(Measure("$2.4e-3(22)"))).error == Decimal("0.0022")
          assert Measure(str(Measure("$2.4e-3(22)"))).implied == False
        # Zero Value
        if(True):
          assert Measure(str(Measure("0(5)cm"))).value == Decimal("0")
          assert Measure(str(Measure("0(5)cm"))).units == Unit("cm")
          assert Measure(str(Measure("0(5)cm"))).error == Decimal("5")
          assert Measure(str(Measure("0(5)cm"))).implied == False
        # Parse Magnitude
        if(True):
          # Magnitude without Multiplier
          assert Measure(str(Measure("24(3) 10^3 cm"))).value == Decimal("24")
          assert Measure(str(Measure("24(3) 10^3 cm"))).units == Unit("10^3 cm")
          assert Measure(str(Measure("24(3) 10^3 cm"))).error == Decimal("3")
          assert Measure(str(Measure("24(3) 10^3 cm"))).implied == False
          # Magnitude with * Multiplier
          assert Measure(str(Measure("24(3) * 10^3 cm"))).value == Decimal("24")
          assert Measure(str(Measure("24(3) * 10^3 cm"))).units == Unit("10^3 cm")
          assert Measure(str(Measure("24(3) * 10^3 cm"))).error == Decimal("3")
          assert Measure(str(Measure("24(3) * 10^3 cm"))).implied == False
          # Magnitude with x Multiplier
          assert Measure(str(Measure("24(3) x 10^3 cm"))).value == Decimal("24")
          assert Measure(str(Measure("24(3) x 10^3 cm"))).units == Unit("10^3 cm")
          assert Measure(str(Measure("24(3) x 10^3 cm"))).error == Decimal("3")
          assert Measure(str(Measure("24(3) x 10^3 cm"))).implied == False
          # Magnitude with \u00B7 Multiplier
          assert Measure(str(Measure("24(3) \u00B7 10^3 cm"))).value == Decimal("24")
          assert Measure(str(Measure("24(3) \u00B7 10^3 cm"))).units == Unit("10^3 cm")
          assert Measure(str(Measure("24(3) \u00B7 10^3 cm"))).error == Decimal("3")
          assert Measure(str(Measure("24(3) \u00B7 10^3 cm"))).implied == False
          # Magnitude with \u00D7 Multiplier
          assert Measure(str(Measure("24(3) \u00D7 10^3 cm"))).value == Decimal("24")
          assert Measure(str(Measure("24(3) \u00D7 10^3 cm"))).units == Unit("10^3 cm")
          assert Measure(str(Measure("24(3) \u00D7 10^3 cm"))).error == Decimal("3")
          assert Measure(str(Measure("24(3) \u00D7 10^3 cm"))).implied == False
          # Magnitude with x Multiplier No Spaces
          assert Measure(str(Measure("24(3)x10^3 cm"))).value == Decimal("24")
          assert Measure(str(Measure("24(3)x10^3 cm"))).units == Unit("10^3 cm")
          assert Measure(str(Measure("24(3)x10^3 cm"))).error == Decimal("3")
          assert Measure(str(Measure("24(3)x10^3 cm"))).implied == False
        # Unitless
        if(True):
          assert Measure(str(Measure("36(4)"))).value == Decimal("36")
          assert Measure(str(Measure("36(4)"))).units == Unit()
          assert Measure(str(Measure("36(4)"))).error == Decimal("4")
          assert Measure(str(Measure("36(4)"))).implied == False
      # Plus Minus Error Notation
      if(True):
        assert Measure(str(Measure("12\u00B11cm"))).value == Decimal("12")
        assert Measure(str(Measure("12\u00B11cm"))).units == Unit("cm")
        assert Measure(str(Measure("12\u00B11cm"))).error == Decimal("1")
        assert Measure(str(Measure("12\u00B11cm"))).implied == False
        # Decimal Error
        if(True):
          assert Measure(str(Measure("12\u00B10.5cm"))).value == Decimal("12")
          assert Measure(str(Measure("12\u00B10.5cm"))).units == Unit("cm")
          assert Measure(str(Measure("12\u00B10.5cm"))).error == Decimal("0.5")
          assert Measure(str(Measure("12\u00B10.5cm"))).implied == False
        # End with Zero
        if(True):
          assert Measure(str(Measure("10\u00B11cm"))).value == Decimal("10")
          assert Measure(str(Measure("10\u00B11cm"))).units == Unit("cm")
          assert Measure(str(Measure("10\u00B11cm"))).error == Decimal("1")
          assert Measure(str(Measure("10\u00B11cm"))).implied == False
        # Preceding Units
        if(True):
          assert Measure(str(Measure("$12\u00B11"))).value == Decimal("12")
          assert Measure(str(Measure("$12\u00B11"))).units == Unit("$")
          assert Measure(str(Measure("$12\u00B11"))).error == Decimal("1")
          assert Measure(str(Measure("$12\u00B11"))).implied == False
        # E notation
        if(True):
          assert Measure(str(Measure("1.2e1\u00B11cm"))).value == Decimal("12")
          assert Measure(str(Measure("1.2e1\u00B11cm"))).units == Unit("cm")
          assert Measure(str(Measure("1.2e1\u00B11cm"))).error == Decimal("1")
          assert Measure(str(Measure("1.2e1\u00B11cm"))).implied == False
        # Zero Value
        if(True):
          assert Measure(str(Measure("0\u00B11cm"))).value == Decimal("0")
          assert Measure(str(Measure("0\u00B11cm"))).units == Unit("cm")
          assert Measure(str(Measure("0\u00B11cm"))).error == Decimal("1")
          assert Measure(str(Measure("0\u00B11cm"))).implied == False
        # Parse Magnitude
        if(True):
          # Magnitude without Multiplier
          assert Measure(str(Measure("24\u00B13 10^3 cm"))).value == Decimal("24")
          assert Measure(str(Measure("24\u00B13 10^3 cm"))).units == Unit("10^3 cm")
          assert Measure(str(Measure("24\u00B13 10^3 cm"))).error == Decimal("3")
          assert Measure(str(Measure("24\u00B13 10^3 cm"))).implied == False
          # Magnitude with * Multiplier
          assert Measure(str(Measure("24\u00B13 * 10^3 cm"))).value == Decimal("24")
          assert Measure(str(Measure("24\u00B13 * 10^3 cm"))).units == Unit("10^3 cm")
          assert Measure(str(Measure("24\u00B13 * 10^3 cm"))).error == Decimal("3")
          assert Measure(str(Measure("24\u00B13 * 10^3 cm"))).implied == False
          # Magnitude with x Multiplier
          assert Measure(str(Measure("24\u00B13 x 10^3 cm"))).value == Decimal("24")
          assert Measure(str(Measure("24\u00B13 x 10^3 cm"))).units == Unit("10^3 cm")
          assert Measure(str(Measure("24\u00B13 x 10^3 cm"))).error == Decimal("3")
          assert Measure(str(Measure("24\u00B13 x 10^3 cm"))).implied == False
          # Magnitude with \u00B7 Multiplier
          assert Measure(str(Measure("24\u00B13 \u00B7 10^3 cm"))).value == Decimal("24")
          assert Measure(str(Measure("24\u00B13 \u00B7 10^3 cm"))).units == Unit("10^3 cm")
          assert Measure(str(Measure("24\u00B13 \u00B7 10^3 cm"))).error == Decimal("3")
          assert Measure(str(Measure("24\u00B13 \u00B7 10^3 cm"))).implied == False
          # Magnitude with \u00D7 Multiplier
          assert Measure(str(Measure("24\u00B13 \u00D7 10^3 cm"))).value == Decimal("24")
          assert Measure(str(Measure("24\u00B13 \u00D7 10^3 cm"))).units == Unit("10^3 cm")
          assert Measure(str(Measure("24\u00B13 \u00D7 10^3 cm"))).error == Decimal("3")
          assert Measure(str(Measure("24\u00B13 \u00D7 10^3 cm"))).implied == False
          # Magnitude with x Multiplier No Spaces
          assert Measure(str(Measure("24\u00B13x10^3 cm"))).value == Decimal("24")
          assert Measure(str(Measure("24\u00B13x10^3 cm"))).units == Unit("10^3 cm")
          assert Measure(str(Measure("24\u00B13x10^3 cm"))).error == Decimal("3")
          assert Measure(str(Measure("24\u00B13x10^3 cm"))).implied == False
        # Unitless
        if(True):
          assert Measure(str(Measure("36 \u00B1 4"))).value == Decimal("36")
          assert Measure(str(Measure("36 \u00B1 4"))).units == Unit()
          assert Measure(str(Measure("36 \u00B1 4"))).error == Decimal("4")
          assert Measure(str(Measure("36 \u00B1 4"))).implied == False
    
    # Unit Notation Tests 
    if(True):
      # Single inverse units 1/$
      assert str((Unit("cm/$")/Measure("3(1)cm"))) == "0.3333333333333333333333333333 ± 0.1111111111111111111111111111 / $"
  
  def test_repr(self):
    # These tests should be redundant to str parser tests.
    assert eval(repr(Measure("$2.4e-3(22)"))) == Measure("$2.4e-3(22)")
  