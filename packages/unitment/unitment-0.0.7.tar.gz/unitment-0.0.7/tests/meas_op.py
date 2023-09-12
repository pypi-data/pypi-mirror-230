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

class TestMeasureOperators:
  
  # Equality
  def test_approx(self):
    assert not Measure("21(1)e4cm").approx(Measure("24(1)e4cm"))
    assert     Measure("22(1)e4cm").approx(Measure("24(1)e4cm"))
    assert     Measure("23(1)e4cm").approx(Measure("24(1)e4cm"))
    assert     Measure("24(1)e4cm").approx(Measure("24(1)e4cm"))
    assert     Measure("25(1)e4cm").approx(Measure("24(1)e4cm"))
    assert     Measure("26(1)e4cm").approx(Measure("24(1)e4cm"))
    assert not Measure("27(1)e4cm").approx(Measure("24(1)e4cm"))
    assert     Measure("5").approx(5)
    assert     Measure("5").approx(Decimal("5"))
    assert     Measure("5 m^2",value="2").approx(Measure("10m^2"))
    with pytest.raises(IncompatibleUnitException):
      Measure("12 mg").approx(Measure("12 uL"))
  def test_eq(self):
    # Units
    assert Measure("24(1)e4cm") == Measure("24(1)e4cm")
    assert Measure("0.64(5)m")  == Measure("64(5)cm")
    assert Measure("5 m^2",value="2") == Measure("10 m^2")
    # unitless 
    assert Measure("24(1)e4") == Measure("24(1)e4")
    assert Measure("5") == Measure(5)
    assert Measure("5") == Decimal("5")
    assert Measure("3000") != True
    # Float Flexibility
    assert Measure(value=2.5,units=None).value == Decimal("2.5")
  def test_ne(self):
    # To-DO Internal Types Don't Matter for equals
    # assert Measure(units="cm", value= 12.4, error=6.2) == Measure(units="cm", value= Decimal("12.4"), error=Decimal("6.2"))
    
    assert Measure("0.64(5)m")  != Measure("64(5)m")
    assert Measure("5") != Measure(1)
    assert Measure("5") != Decimal("1")
    assert Measure("5 m^2",value="2") != Measure("2 m^2")
  
  # Relative
  def test_lt(self):
    # No Uncertainty
    if(True):
      # Units
      assert     Measure("23e4cm") < Measure("24e4cm")
      assert not Measure("24e4cm") < Measure("24e4cm")
      assert not Measure("25e4cm") < Measure("24e4cm")
      # Unitless
      assert     Measure("23e4") < Measure("24e4")
      assert not Measure("24e4") < Measure("24e4")
      assert not Measure("25e4") < Measure("24e4")
      # Decimal 
      assert     Measure("23e4") < Measure("24e4")
      assert not Measure("24e4") < Measure("24e4")
      assert not Measure("25e4") < Measure("24e4")
      # Magnitude
      assert     Measure("5 m^2",value="2") < Measure("11 m^2")
      assert not Measure("5 m^2",value="2") < Measure("10 m^2")
      assert not Measure("5 m^2",value="2") < Measure("9 m^2")
    # Uncertainty
    if(True):
      # Units
      assert     Measure("21(1)e4cm") < Measure("24(1)e4cm")
      assert not Measure("22(1)e4cm") < Measure("24(1)e4cm")
      assert not Measure("23(1)e4cm") < Measure("24(1)e4cm")
      assert not Measure("24(1)e4cm") < Measure("24(1)e4cm")
      assert not Measure("25(1)e4cm") < Measure("24(1)e4cm")
      assert not Measure("26(1)e4cm") < Measure("24(1)e4cm")
      assert not Measure("27(1)e4cm") < Measure("24(1)e4cm")
      # Unitless 
      assert     Measure("21(1)e4") < Measure("24(1)e4")
      assert not Measure("22(1)e4") < Measure("24(1)e4")
      assert not Measure("23(1)e4") < Measure("24(1)e4")
      assert not Measure("24(1)e4") < Measure("24(1)e4")
      assert not Measure("25(1)e4") < Measure("24(1)e4")
      assert not Measure("26(1)e4") < Measure("24(1)e4")
      assert not Measure("27(1)e4") < Measure("24(1)e4")
    # UnitExceptions 
    if(True):
      with pytest.raises(IncompatibleUnitException):
        Measure("12 mg") < Measure("12 uL")
  def test_le(self):
    # No Uncertainty
    if(True):
      # units
      assert     Measure("23e4cm") <= Measure("24e4cm")
      assert     Measure("24e4cm") <= Measure("24e4cm")
      assert not Measure("25e4cm") <= Measure("24e4cm")
      # unitless
      assert     Measure("23e4") <= Measure("24e4")
      assert     Measure("24e4") <= Measure("24e4")
      assert not Measure("25e4") <= Measure("24e4")
      # Decimal
      assert     Measure("23e4") <= Decimal("24e4")
      assert     Measure("24e4") <= Decimal("24e4")
      assert not Measure("25e4") <= Decimal("24e4")
      # Magnitude
      assert     Measure("5 m^2",value="2") <= Measure("11 m^2")
      assert     Measure("5 m^2",value="2") <= Measure("10 m^2")
      assert not Measure("5 m^2",value="2") <= Measure("9 m^2")
    # Uncertainty
    if(True):
      # Units
      assert     Measure("21(1)e4cm") <= Measure("24(1)e4cm")
      assert     Measure("22(1)e4cm") <= Measure("24(1)e4cm")
      assert     Measure("23(1)e4cm") <= Measure("24(1)e4cm")
      assert     Measure("24(1)e4cm") <= Measure("24(1)e4cm")
      assert not Measure("25(1)e4cm") <= Measure("24(1)e4cm")
      assert not Measure("26(1)e4cm") <= Measure("24(1)e4cm")
      assert not Measure("27(1)e4cm") <= Measure("24(1)e4cm")
      # Unitless
      assert     Measure("21(1)e4") <= Measure("24(1)e4")
      assert     Measure("22(1)e4") <= Measure("24(1)e4")
      assert     Measure("23(1)e4") <= Measure("24(1)e4")
      assert     Measure("24(1)e4") <= Measure("24(1)e4")
      assert not Measure("25(1)e4") <= Measure("24(1)e4")
      assert not Measure("26(1)e4") <= Measure("24(1)e4")
      assert not Measure("27(1)e4") <= Measure("24(1)e4")
    # UnitExceptions 
    if(True):
      with pytest.raises(IncompatibleUnitException):
        Measure("12 mg") <= Measure("12 uL")
  def test_gt(self):
    # No Uncertainty
    if(True):
      # Units 
      assert not Measure("23e4cm") > Measure("24e4cm")
      assert not Measure("24e4cm") > Measure("24e4cm")
      assert     Measure("25e4cm") > Measure("24e4cm")
      # Unitless
      assert not Measure("23e4") > Measure("24e4")
      assert not Measure("24e4") > Measure("24e4")
      assert     Measure("25e4") > Measure("24e4")
      # Decimal
      assert not Measure("23e4") > Decimal("24e4")
      assert not Measure("24e4") > Decimal("24e4")
      assert     Measure("25e4") > Decimal("24e4")
      # Magnitude
      assert not Measure("5 m^2",value="2") > Measure("11 m^2")
      assert not Measure("5 m^2",value="2") > Measure("10 m^2")
      assert     Measure("5 m^2",value="2") > Measure("9 m^2")
    # Uncertainty
    if(True):
      # Units
      assert not Measure("21(1)e4cm") > Measure("24(1)e4cm")
      assert not Measure("22(1)e4cm") > Measure("24(1)e4cm")
      assert not Measure("23(1)e4cm") > Measure("24(1)e4cm")
      assert not Measure("24(1)e4cm") > Measure("24(1)e4cm")
      assert not Measure("25(1)e4cm") > Measure("24(1)e4cm")
      assert not Measure("26(1)e4cm") > Measure("24(1)e4cm")
      assert     Measure("27(1)e4cm") > Measure("24(1)e4cm")
      # Unitless
      assert not Measure("21(1)e4") > Measure("24(1)e4")
      assert not Measure("22(1)e4") > Measure("24(1)e4")
      assert not Measure("23(1)e4") > Measure("24(1)e4")
      assert not Measure("24(1)e4") > Measure("24(1)e4")
      assert not Measure("25(1)e4") > Measure("24(1)e4")
      assert not Measure("26(1)e4") > Measure("24(1)e4")
      assert     Measure("27(1)e4") > Measure("24(1)e4")
    # UnitExceptions 
    if(True):
      with pytest.raises(IncompatibleUnitException):
        Measure("12 mg") > Measure("12 uL")
  def test_ge(self):
    # No Uncertainty
    if(True):
      # Units
      assert not Measure("23e4cm") >= Measure("24e4cm")
      assert     Measure("24e4cm") >= Measure("24e4cm")
      assert     Measure("25e4cm") >= Measure("24e4cm")
      # Unitless
      assert not Measure("23e4") >= Measure("24e4")
      assert     Measure("24e4") >= Measure("24e4")
      assert     Measure("25e4") >= Measure("24e4")
      # Decimal
      assert not Measure("23e4") >= Decimal("24e4")
      assert     Measure("24e4") >= Decimal("24e4")
      assert     Measure("25e4") >= Decimal("24e4")
      # Magnitude
      assert not Measure("5 m^2",value="2") >= Measure("11 m^2")
      assert     Measure("5 m^2",value="2") >= Measure("10 m^2")
      assert     Measure("5 m^2",value="2") >= Measure("9 m^2")
    # Uncertainty
    if(True):
      # Units
      assert not Measure("21(1)e4cm") >= Measure("24(1)e4cm")
      assert not Measure("22(1)e4cm") >= Measure("24(1)e4cm")
      assert not Measure("23(1)e4cm") >= Measure("24(1)e4cm")
      assert     Measure("24(1)e4cm") >= Measure("24(1)e4cm")
      assert     Measure("25(1)e4cm") >= Measure("24(1)e4cm")
      assert     Measure("26(1)e4cm") >= Measure("24(1)e4cm")
      assert     Measure("27(1)e4cm") >= Measure("24(1)e4cm")
      # Unitless
      assert not Measure("21(1)e4") >= Measure("24(1)e4")
      assert not Measure("22(1)e4") >= Measure("24(1)e4")
      assert not Measure("23(1)e4") >= Measure("24(1)e4")
      assert     Measure("24(1)e4") >= Measure("24(1)e4")
      assert     Measure("25(1)e4") >= Measure("24(1)e4")
      assert     Measure("26(1)e4") >= Measure("24(1)e4")
      assert     Measure("27(1)e4") >= Measure("24(1)e4")
    # UnitExceptions 
    if(True):
      with pytest.raises(IncompatibleUnitException):
        Measure("12 mg") >= Measure("12 uL")
  
  # Addition & Subtraction Operators
  def test_add(self):
    # Measure
    if(True):
      # Values and Certainties
      assert Measure("24(4)cm") + Measure("24(3)cm") == Measure("48(5)cm")
      assert Measure("24(3)cm") + Measure("24(4)cm") == Measure("48(5)cm")
      assert Measure("12(3)cm") + Measure("36(4)cm") == Measure("48(5)cm")
      assert Measure("12(3)")   + Measure("36(4)")   == Measure("48(5)")
      # Zeros
      assert Measure("0cm")     + Measure("36(4)cm") == Measure("36(4)cm")
      assert Measure("36(4)cm") + Measure("0cm")     == Measure("36(4)cm")
      assert Measure("36(4)")   + Measure("0")       == Measure("36(4)")
      # Implied Uncertainty
      assert (Measure("3 cm") + Measure("4 cm")).implied == True
      assert Measure("5 m^2",value="2") + Measure("10m^2") == Measure("20m^2")
      # Preserve Inputs
      a = Measure("12(3)cm")
      b = Measure("36(4)cm")
      c = a+b 
      c = None
      assert a == Measure("12(3)cm")
      assert b == Measure("36(4)cm")
      assert c == None
      # Mixed Units Compatible
      assert Measure("1(0.03)m") + Measure("36(4)cm") == Measure("136(5)cm")
      # Mixed Units Incompatible
      with pytest.raises(IncompatibleUnitException):
        Measure("3 pigs")+Measure("2 sheep")
      with pytest.raises(IncompatibleUnitException):
        Measure("36(4)") + Measure("0cm")
    # Unit
    if(True):
      assert Measure("5 cm")+Unit("cm")   == Measure("6 cm")
      assert Measure("5 cm")+Unit("10cm") == Measure("15 cm")
      with pytest.raises(IncompatibleUnitException):
        Measure("5 cm")+Unit("mg")
    # Number
    if(True):
      # Values and Certainties
      assert          5   + Measure("36(4)") == Measure("41(4)")
      assert         "5"  + Measure("36(4)") == Measure("41(4)")
      assert Decimal("5") + Measure("36(4)") == Measure("41(4)")
      assert Measure("36(4)") +          5   == Measure("41(4)")
      assert Measure("36(4)") +         "5"  == Measure("41(4)")
      assert Measure("36(4)") + Decimal("5") == Measure("41(4)")
      # Zeros
      assert          0   + Measure("36(4)") == Measure("36(4)")
      assert         "0"  + Measure("36(4)") == Measure("36(4)")
      assert Decimal("0") + Measure("36(4)") == Measure("36(4)")
      assert Measure("36(4)") + 0            == Measure("36(4)")
      assert Measure("36(4)") + "0"          == Measure("36(4)")
      assert Measure("36(4)") + Decimal("0") == Measure("36(4)")
      # Implied Uncertainty
      assert (Measure("3") + Decimal("4")).implied == True
      assert (Measure("3") +         "4" ).implied == True
      assert (Measure("3") +          4  ).implied == True
      # Preserve Inputs
      a = Measure("36(4)")
      b = Decimal("5")
      c = a+b 
      c = None
      assert a == Measure("36(4)")
      assert b == Decimal("5")
      assert c == None
      # Error on Non-Unitless Measure + Decimal 
      # Measure + 5
      if(True):
        with pytest.raises(IncompatibleUnitException):
          Measure("36(4)m") + Decimal("5")
        with pytest.raises(IncompatibleUnitException):
          Measure("36(4)m") + "5"
        with pytest.raises(IncompatibleUnitException):
          Measure("36(4)m") + 5
      # 5 + Measure
      if(True):
        with pytest.raises(IncompatibleUnitException):
          Decimal("5") + Measure("36(4)m")
        with pytest.raises(IncompatibleUnitException):
          "5" + Measure("36(4)m")
        with pytest.raises(IncompatibleUnitException):
          5 + Measure("36(4)m")
      
    # String Measures 
    if(True):
      # Values and Certainties
      assert Measure("24(4)cm") + "24(3)cm" == Measure("48(5)cm")
      assert Measure("24(3)cm") + "24(4)cm" == Measure("48(5)cm")
      assert Measure("12(3)cm") + "36(4)cm" == Measure("48(5)cm")
      assert Measure("12(3)")   + "36(4)"   == Measure("48(5)")
      assert "24(4)cm" + Measure("24(3)cm") == Measure("48(5)cm")
      assert "24(3)cm" + Measure("24(4)cm") == Measure("48(5)cm")
      assert "12(3)cm" + Measure("36(4)cm") == Measure("48(5)cm")
      assert "12(3)"   + Measure("36(4)")   == Measure("48(5)")
      # Zeros
      assert Measure("0cm")     + "36(4)cm" == Measure("36(4)cm")
      assert Measure("36(4)cm") + "0cm"     == Measure("36(4)cm")
      assert Measure("36(4)")   + "0"       == Measure("36(4)")
      assert "0cm"     + Measure("36(4)cm") == Measure("36(4)cm")
      assert "36(4)cm" + Measure("0cm")     == Measure("36(4)cm")
      assert "36(4)"   + Measure("0")       == Measure("36(4)")
      # Implied Uncertainty
      assert (Measure("3 cm") + "4 cm").implied == True
      assert ("3 cm" + Measure("4 cm")).implied == True
      assert Measure("5 m^2",value="2") + "10m^2" == Measure("20m^2")
      assert "10m^2" + Measure("5 m^2",value="2") == Measure("20m^2")
      # Preserve Inputs
      a = Measure("12(3)cm")
      b = "36(4)cm"
      c = a+b 
      c = None
      assert a == Measure("12(3)cm")
      assert b == "36(4)cm"
      assert c == None
      # Mixed Units Compatible
      assert Measure("1(0.03)m") + "36(4)cm" == Measure("136(5)cm")
      assert "1(0.03)m" + Measure("36(4)cm") == Measure("136(5)cm")
      # Mixed Units Incompatible
      with pytest.raises(IncompatibleUnitException):
        Measure("3 pigs")+"2 sheep"
      with pytest.raises(IncompatibleUnitException):
        "3 pigs"+Measure("2 sheep")
      with pytest.raises(IncompatibleUnitException):
        Measure("36(4)") + "0cm"
      with pytest.raises(IncompatibleUnitException):
        "36(4)" + Measure("0cm")
  def test_sub(self):
    # Measure
    if(True):
      # Certainty and Values
      assert Measure("24(4)cm") - Measure("24(3)cm") == Measure("0(5)cm")
      assert Measure("24(3)cm") - Measure("24(4)cm") == Measure("0(5)cm")
      assert Measure("12(3)cm") - Measure("36(4)cm") == Measure("-24(5)cm")
      # Zeros
      assert Measure("0cm")     - Measure("36(4)cm") == Measure("-36(4)cm")
      assert Measure("36(4)cm") - Measure("0cm")     == Measure("36(4)cm")
      # Implied Uncertainty
      assert (Measure("3 cm") - Measure("4 cm")).implied == True
      assert Measure("5 m^2",value="2") - Measure("5 m^2") == Measure("5 m^2")
      # Preserve Inputs 
      a = Measure("12(3)cm")
      b = Measure("36(4)cm")
      c = a-b 
      c = None
      assert a == Measure("12(3)cm")
      assert b == Measure("36(4)cm")
      assert c == None
      # Mixed Units Compatible
      assert Measure("1(0.03)m") - Measure("36(4)cm") == Measure("64(5)cm")
      # Mixed Units Incompatible
      with pytest.raises(IncompatibleUnitException):
        Measure("3 pigs") - Measure("2 sheep")
      with pytest.raises(IncompatibleUnitException):
        Measure("36(4)") - Measure("0cm")
    # Number
    if(True):
      # Certainty and Values
      assert Decimal("5") - Measure("36(4)") == Measure("-31(4)")
      assert         "5"  - Measure("36(4)") == Measure("-31(4)")
      assert          5   - Measure("36(4)") == Measure("-31(4)")
      assert Measure("36(4)") - Decimal("5") == Measure("31(4)")
      assert Measure("36(4)") -         "5"  == Measure("31(4)")
      assert Measure("36(4)") -          5   == Measure("31(4)")
      # Zeros
      assert          0   - Measure("36(4)") == Measure("-36(4)")
      assert         "0"  - Measure("36(4)") == Measure("-36(4)")
      assert Decimal("0") - Measure("36(4)") == Measure("-36(4)")
      assert Measure("36(4)") -          0   == Measure("36(4)")
      assert Measure("36(4)") -         "0"  == Measure("36(4)")
      assert Measure("36(4)") - Decimal("0") == Measure("36(4)")
      # Implied Uncertainty
      assert (Measure("3") - Decimal("4")).implied == True
      assert (Measure("3") -         "4" ).implied == True
      assert (Measure("3") -          4  ).implied == True
      # Preserve Inputs 
      a = Measure("36(4)")
      b = Decimal("5")
      c = a-b 
      c = None
      assert a == Measure("36(4)")
      assert b == Decimal("5")
      assert c == None
      # Error on Non-Unitless Measure - Decimal 
      # Measure - 5 
      if(True):
        with pytest.raises(IncompatibleUnitException):
          Measure("36(4)m") - Decimal("5")
        with pytest.raises(IncompatibleUnitException):
          Measure("36(4)m") - "5"
        with pytest.raises(IncompatibleUnitException):
          Measure("36(4)m") - 5
      # 5 - Measure
      if(True):
        with pytest.raises(IncompatibleUnitException):
          Decimal("5") - Measure("36(4)m")
        with pytest.raises(IncompatibleUnitException):
          "5" - Measure("36(4)m")
        with pytest.raises(IncompatibleUnitException):
          5 - Measure("36(4)m")
      # Measure - 0
      if(True):
        assert Measure("36(4)cm") - Decimal("0") == Measure("36(4)cm")
        assert Measure("36(4)cm") - "0"          == Measure("36(4)cm")
        assert Measure("36(4)cm") - 0            == Measure("36(4)cm")
      # 0 - Measure
      if(True):
        assert Decimal("0") - Measure("36(4)cm")  == Measure("-36(4)cm")
        assert "0" - Measure("36(4)cm")           == Measure("-36(4)cm")
        assert 0 - Measure("36(4)cm")             == Measure("-36(4)cm")
    # Unit
    if(True):
      assert Measure("5 cm")-Unit("cm")   == Measure("4 cm")
      assert Measure("5 cm")-Unit("10cm") == Measure("-5 cm")
      with pytest.raises(IncompatibleUnitException):
        Measure("5 cm")-Unit("mg")
    # String Measures 
    if(True):
      # Certainty and Values
      assert Measure("24(4)cm") - "24(3)cm" == Measure("0(5)cm")
      assert Measure("24(3)cm") - "24(4)cm" == Measure("0(5)cm")
      assert Measure("12(3)cm") - "36(4)cm" == Measure("-24(5)cm")
      assert "24(4)cm" - Measure("24(3)cm") == Measure("0(5)cm")
      assert "24(3)cm" - Measure("24(4)cm") == Measure("0(5)cm")
      assert "12(3)cm" - Measure("36(4)cm") == Measure("-24(5)cm")
      # Zeros
      assert Measure("0cm")     - "36(4)cm" == Measure("-36(4)cm")
      assert Measure("36(4)cm") - "0cm"     == Measure("36(4)cm")
      assert "0cm"     - Measure("36(4)cm") == Measure("-36(4)cm")
      assert "36(4)cm" - Measure("0cm")     == Measure("36(4)cm")
      # Implied Uncertainty
      assert (Measure("3 cm") - "4 cm").implied == True
      assert ("3 cm" - Measure("4 cm")).implied == True
      assert Measure("5 m^2",value="2") - "5 m^2" == Measure("5 m^2")
      assert "5 m^2" - Measure("5 m^2",value="2") == Measure("-5 m^2")
      # Preserve Inputs 
      a = Measure("12(3)cm")
      b = Measure("36(4)cm")
      c = a-b 
      c = None
      assert a == Measure("12(3)cm")
      assert b == Measure("36(4)cm")
      assert c == None
      # Mixed Units Compatible
      assert Measure("1(0.03)m") - "36(4)cm" == Measure("64(5)cm")
      assert "1(0.03)m" - Measure("36(4)cm") == Measure("64(5)cm")
      # Mixed Units Incompatible
      with pytest.raises(IncompatibleUnitException):
        Measure("3 pigs") - "2 sheep"
      with pytest.raises(IncompatibleUnitException):
        "3 pigs" - Measure("2 sheep")
      with pytest.raises(IncompatibleUnitException):
        Measure("36(4)") - "0cm"
      with pytest.raises(IncompatibleUnitException):
        "36(4)" - Measure("0cm")
  
  # Multiplication & Division Operators
  # To-Do: "1 * 5 cm" is a measure. "cm" is a Unit Fix this.
  
  def test_div(self):
    
    # Unit
    if(True):
      # Canceling
      assert Measure("4(2)cm")   / Unit("cm/$")       == Measure("4(2)$")
      assert (Unit("cm/$")/Measure("3(1)cm")).approx(Measure("0.33333(11111)/$"))
      
    # Number
    if(True):
      # Values & Certainties
      assert Measure("4(2)cm") / Decimal("2") == Measure("2(1)cm")
      assert Measure("4(2)cm") /         "2"  == Measure("2(1)cm")
      assert Measure("4(2)cm") /          2   == Measure("2(1)cm")
      assert (Decimal("2") / Measure("3(1)cm")).approx(Measure("0.66666(22222)cm^-1"))
      assert (        "2"  / Measure("3(1)cm")).approx(Measure("0.66666(22222)cm^-1"))
      assert (         2   / Measure("3(1)cm")).approx(Measure("0.66666(22222)cm^-1"))
      # Implied Uncertainty
      assert (Measure("3cm")  / Decimal("2")).implied == True
      assert (Measure("3cm")  /         "2" ).implied == True
      assert (Measure("3cm")  /          2  ).implied == True
      # Divide by Zero Errors
      with pytest.raises(Exception):
        assert Measure("3cm")  / Decimal("0")
      with pytest.raises(Exception):
        assert Measure("3cm")  / "0"
      with pytest.raises(Exception):
        assert Measure("3cm")  / 0
    # String Measure
    if(True):
      # Values, Certainties, Canceling
      assert (Measure("3(1)cm") / "4(2)cm").approx(Measure("0.75(45)"))
      assert ("3(1)cm" / Measure("4(2)cm")).approx(Measure("0.75(45)"))
      # Implied Uncertainty
      assert (Measure("3cm") / "4(2)cm").implied == True
      assert ("3cm" / Measure("4(2)cm")).implied == True
      assert Measure("5 m^2",value="2") / "5 m^2" == Measure("2")
      assert "20 m^2" / Measure("5 m^2",value="2") == Measure("2")
      # Divide By Zero
      with pytest.raises(Exception):
        Measure("3 cm")/"0 m"
      with pytest.raises(Exception):
        "3 cm"/Measure("0 m")
      # Weird unitss 
      assert Measure("26.85 \u00B0C") / "26.85 \u00B0C" == Measure("1")
      assert "26.85 \u00B0C" / Measure("26.85 \u00B0C") == Measure("1")
      assert Measure("5 carrot") / "1 pig" == Measure("5 carrot / pig")
      assert "5 carrot" / Measure("1 pig") == Measure("5 carrot / pig")
      # Past Failed Units
      assert (Measure("5cm")/"1 min").units == Unit("cm/min")
      assert ("5cm"/Measure("1 min")).units == Unit("cm/min")
  
  # Exponents
  def test_power(self):
    # set-up
    a = Measure("4(2)cm")
    b = Measure("6(1)cm/cm")
    three = Decimal("3")
    c = Measure("4096(13536)cm^6")
    d = Measure("64(96)cm^3")
    e = Measure("729(800)")
    # assert
    assert (a**b).approx(c)
    assert (a**three).approx(d)
    assert (three**b).approx(e)
    # Implied Uncertainty
    f = Measure("4")
    g = Measure("6")
    assert (f**g).implied == True
    assert (f**three).implied == True
    # Exceptions
    with pytest.raises(Exception):
      Measure("0")**Measure("0")
  def test_log(self):
    assert Measure.log(Measure("6(1)"),base=Measure("4(2)")).approx(Measure("1(2.97)"))
    assert Measure.log(Decimal("3"),   base=Measure("4(2)")).approx(Measure("1.26(43)"))
    assert Measure.log(Measure("6(1)"),base=Decimal("3")   ).approx(Measure("1.63(2)"))
    # Implied Uncertainty
    f = Measure("4")
    g = Measure("6")
    assert Measure.log(g,base=f).implied == True
    assert Measure.log(3,base=f).implied == True
    
    # Exceptions
    with pytest.raises(IncompatibleUnitException):
      Measure.log(Measure("12 mg"),base=Measure("2 mg"))
  
  def test_ln(self):
    assert -0.02 < Measure("0.99").ln() < 0
  
  
  # Trigonometry
  def test_sin(self):
    # Radians
    a = Measure("3.14(5)")
    b = Measure("0.0016(25)")# +- 0.0025
    c = Measure("3.14")
    assert a.sin().approx(b)
    assert c.sin().implied == True
    # Degrees
    a = Measure("90 deg")
    b = Measure("1")
    assert a.sin().approx(b)
    # Exceptions
    with pytest.raises(IncompatibleUnitException):
      Measure.sin(Measure("12 mg"))
    # Exceptions Radiation Rads
    with pytest.raises(IncompatibleUnitException):
      Measure.sin(Measure("12 rad"))
  def test_cos(self):
    # Radians
    a = Measure("3.5(1)")
    b = Measure("-0.936(1)")# -0.9364 +- 0.0025
    c = Measure("3.5")
    assert a.cos().approx(b)
    assert c.cos().implied == True
    # Degrees
    a = Measure("90 deg")
    b = Measure("0")
    assert a.cos().approx(b)
    # Exceptions
    with pytest.raises(IncompatibleUnitException):
      Measure.cos(Measure("12 mg"))
    # Exceptions Radiation Rads
    with pytest.raises(IncompatibleUnitException):
      Measure.cos(Measure("12 rad"))
  
  #
  def test_round(self):
    a = Measure("0.0016(26)")# +- 0.0025
    b = Measure("0.002(3)")
    assert b == round(a,3)
    assert round(Measure("12.34cm")).implied == True
    assert round(Measure("12.34(2)cm")).implied == False
  
  # 
  def test_in(self):
    assert not ( Measure("300") in [True] )
  