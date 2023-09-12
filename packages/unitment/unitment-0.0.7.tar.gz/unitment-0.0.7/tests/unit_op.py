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

class TestUnitOperators:
  # Equality-Like Operators
  def test_unitless(self):
    assert Unit(None).unitless()
    assert Unit("").unitless()
  def test_dimensionless(self):
    assert Unit("").dimensionless()
    assert Unit("deg").dimensionless()
  def test_same_dimensions(self):
    a,b = Unit("m"),Unit("mm")
    assert a.decompose().symbols == b.decompose().symbols
    a,b = Unit("\u00B0C"),Unit("\u00B0F",definitions = Unit.IMPERIAL_UNITS)
    assert a.decompose().symbols == b.decompose().symbols
  def test_eq(self):
    # Identical 
    assert Unit() == Unit()
    assert Unit("m^2") == Unit("m2")
    assert not Unit("m3") == Unit("m2")
    # Different Units 
    assert Unit("M g/mol") == Unit("g/L")
    assert Unit("M g/mol") == Unit("mg/mL")
    assert Unit("M g/mol") == Unit("ug/uL")
    assert Unit("mg/mL")   == Unit("ug/uL")
    # Different Magnitudes
    assert Unit("mm") == Unit("m",magnitude=Decimal("1e-3"))
    # Tuple Form (Uncommon)
    assert Unit("m^2") == (("m",2),)
  def test_ne(self):
    assert not Unit() != Unit()
    assert not Unit("m^2") != Unit("m2")
    assert Unit("m3") != Unit("m2")
    # Tuple Form (Uncommon)
    assert not Unit("m^2") == (("m",1),)
  
  # Addition & Subtraction Operators
  def test_add(self):
    # Add Units
    assert Unit("m^2") + Unit("m2") == Measure("2 m2")
    with pytest.raises(IncompatibleUnitException):
      Unit("m^2") + Unit("m3")
    # Add Decimals
    assert Unit()+2 == 3
    assert 2+Unit() == 3
    
    # (2+Unit("\u00B0")) =      Measure("2.017453292519943295088877575")
    assert (2+Unit("\u00B0")) < Measure("2.0174533")
    assert (2+Unit("\u00B0")) > Measure("2.0174532")
  def test_sub(self):
    # Subtract Units
    assert Unit("m^2") - Unit("m2") == Measure(value=0,error=0,units="m2")
    assert Unit("m^2") - Unit("m2") == Measure("0 m2")
    with pytest.raises(IncompatibleUnitException):
      Unit("m^2") - Unit("m3")
    # Subtract Decimals
    assert Unit()-2 == -1
    assert 2-Unit() == 1
    assert Unit("10")-2 == 8
    assert 2-Unit("10") == -8
  
  # Multiplication & Division Operators
  def test_mult(self):
    # Units * Units
    if(True):
      assert Unit("m^2") * Unit("m")   == Unit("m^3")
      assert Unit("M") * Unit("g/mol") == Unit("M g/mol")
    # Decimal * Units
    if(True):
      assert 2*Unit("M") == Unit("2 M")
      assert Unit("M")*2 == Unit("2 M")
    # Function Unit * Function Unit
    if(True):
      with pytest.raises(AmbiguousUnitException):
        Unit("\u00B0C m").decompose()
      with pytest.raises(AmbiguousUnitException):
        Unit("\u00B0C")*Unit("\u00B0C")
      
    # Verify Immutability
    if(True):
      x=Unit("m2")
      y=Unit("m")
      z=x*y
      x._symbols_ = ()
      y._symbols_ = ()
      assert z == Unit("m3")
  def test_div(self):
    # Unit / Unit
    if(True):
      assert Unit("m^2") / Unit("m")     == Unit("m")
      assert Unit("M")   / Unit("g/mol") == Unit("M mol / g")
    # Unit / Decimal
    if(True):
      assert Unit("M") / 1 == Unit("M")
      assert 1 / Unit("M") == Unit("1/M")
      assert Unit("m^2")/2 == Unit("0.5 m^2")
      assert Unit("2 m^2")/2 == Unit("m^2")
    # Function Unit / Function Unit
    if(True):
      assert Unit("\u00B0C")/Unit("\u00B0C") == Unit()
      with pytest.raises(AmbiguousUnitException):
        Unit("\u00B0C")/Unit("\u00B0C^-1")
    # Verify Immutability
    if(True):
      x=Unit("m2")
      y=Unit("m")
      z=x/y
      x._symbols_ = ()
      y._symbols_ = ()
      assert z == Unit("m")
  # Exponent
  def test_pow(self):
    assert Unit("m")**2 == Unit("m^2")
    a = Unit(["nu"],["du"],10)**2 
    assert a.magnitude == Decimal(1e2)
    # Non-Decimal Exponent
    with pytest.raises(Exception):
      Unit("m")**Unit("m")
    # Verify Immutability
    x=Unit("m2")
    y=Decimal("2")
    z=x**y
    x._symbols_ = (("x",Decimal("2")),)
    y = Decimal("5")
    assert z == Unit("m4")
  def test_sqrt(self):
    assert Unit("m2").sqrt() == Unit("m")
    # Verify Immutability
    x=Unit("m2")
    z=x.sqrt()
    x._symbols_ = (("x",Decimal("2")),)
    assert z == Unit("m")
