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

class TestMeasureOperatorsAdd:
  # Error Formula
  # sig**2 = d/dx(x+y)**2 dx**2 + d/dy(x+y)**2 dy **2
  # sig**2 = (1)**2 dx**2 +  (1)**2 dy **2
  # sig**2 = dx**2 + dy **2
  # 
  # sig = measure._sqrt_( dx**2 + dy **2 )
  
  
  def test_measure_measure_add(self):
    def meas_meas_add(
        x=None,dx=None,xu=None, 
        y=None,dy=None,yu=None, 
        u=None,du=None,mu=None,
        v=None,dv=None,mv=None,
        value = None, error=None, unit=None,
        implied=None):
      log.warning(f"x={x} , dx={dx} , xu={xu} , y={y} , dy={dy} , yu={yu}")
      floats = all([isinstance(i,float) or i==None or i==0 for i in [x,dx,y,dy]])
      
      if(floats):
        # Context Settings
        if( u==None):  u = float( x)           # If  x==None, give value
        if(du==None): du = float(dx)           # If dx==None, give value
        if(mu==None): mu = float(xu.magnitude) # If xu==None, give value
        
        if( v==None):  v = float( y)           # If  y==None, give value
        if(dv==None): dv = float(dy)           # If dy==None, give value
        if(mv==None): mv = float(yu.magnitude) # If yu==None, give value
        
        # Standard Div Values
        if(value == None): value = u+v
        if(unit  == None): 
          identical_units = xu.symbols == yu.symbols and xu.magnitude == yu.magnitude
          if(identical_units): unit = xu
          else: unit = xu.decompose()
          
        n  = float( unit.magnitude )
        if(error == None):  error = measure._sqrt_( (du*mu)**2 + (dv*mv)**2 ) / n
        
        # Standard Div Assertions
        assert isinstance(   (  Measure(value=x,error=dx,unit=xu)  +  Measure(value=y,error=dy,unit=yu)  ), Measure )
        assert math.isclose( (  Measure(value=x,error=dx,unit=xu)  +  Measure(value=y,error=dy,unit=yu)  ).value , value )
        assert math.isclose( (  Measure(value=x,error=dx,unit=xu)  +  Measure(value=y,error=dy,unit=yu)  ).error , error )
        assert (  Measure(value=x,error=dx,unit=xu)  +  Measure(value=y,error=dy,unit=yu)  ).implied == implied
        assert (  Measure(value=x,error=dx,unit=xu)  +  Measure(value=y,error=dy,unit=yu)  ).units.symbols   == unit.symbols
        assert (  Measure(value=x,error=dx,unit=xu)  +  Measure(value=y,error=dy,unit=yu)  ).units.magnitude == unit.magnitude
        assert (  Measure(value=x,error=dx,unit=xu)  +  Measure(value=y,error=dy,unit=yu)  ) == Measure(units=unit, value= value, error=error)
      else:
        # Context Settings
        if( u==None):  u = Decimal( x)  # If  x==None, give value
        if(du==None): du = Decimal(dx)  # If dx==None, give value
        if(mu==None): mu = xu.magnitude # If xu==None, give value
        
        if( v==None):  v = Decimal( y)  # If  y==None, give value
        if(dv==None): dv = Decimal(dy)  # If dy==None, give value
        if(mv==None): mv = yu.magnitude # If yu==None, give value
        
        # Standard Div Values
        if(value == None): value = u+v
        if(unit  == None): 
          identical_units = xu.symbols == yu.symbols and xu.magnitude == yu.magnitude
          if(identical_units): unit = xu
          else: unit = xu.decompose()
        n  = unit.magnitude
        if(error == None): error = measure._sqrt_( (du*mu)**2 + (dv*mv)**2 ) / n
        # Standard Div Assertions
        assert isinstance(            (  Measure(value=x,error=dx,unit=xu)  +  Measure(value=y,error=dy,unit=yu)  ), Measure )
        assert Measure._dec_isclose_( (  Measure(value=x,error=dx,unit=xu)  +  Measure(value=y,error=dy,unit=yu)  ).value , value )
        assert Measure._dec_isclose_( (  Measure(value=x,error=dx,unit=xu)  +  Measure(value=y,error=dy,unit=yu)  ).error , error )
        assert (  Measure(value=x,error=dx,unit=xu)  +  Measure(value=y,error=dy,unit=yu)  ).implied == implied
        assert (  Measure(value=x,error=dx,unit=xu)  +  Measure(value=y,error=dy,unit=yu)  ).units.symbols   == unit.symbols
        assert (  Measure(value=x,error=dx,unit=xu)  +  Measure(value=y,error=dy,unit=yu)  ).units.magnitude == unit.magnitude
        assert (  Measure(value=x,error=dx,unit=xu)  +  Measure(value=y,error=dy,unit=yu)  ) == Measure(units=unit, value= value, error=error)
    
    # Measure (Explicit Error) + Measure (Explicit Error) = Measure (Explicit Error)
    if(True):
      # Unitless + Unitless
      if(True):
        # Value 1: Int
        meas_meas_add(
          x=4     , dx=2              , xu=Unit(), 
          y=3     , dy=1              , yu=Unit(), 
          u=None  , du=None           , mu=None,
          v=None  , dv=None           , mv=None,
          implied=False)
        # Value 2: Float
        meas_meas_add(
          x=0.4   , dx=0.2            , xu=Unit(), 
          y=0.3   , dy=0.1            , yu=Unit(), 
          u=None  , du=None           , mu=None,
          v=None  , dv=None           , mv=None,
          implied=False)
        # Value 3: Decimal
        meas_meas_add(
          x=Decimal("40") , dx=Decimal("20")  , xu=Unit(), 
          y=Decimal("30") , dy=Decimal("10")  , yu=Unit(), 
          u=None          , du=None           , mu=None,
          v=None          , dv=None           , mv=None,
          implied=False)
        # Value 4: Negative
        meas_meas_add(
          x=-4    , dx=2              , xu=Unit(), 
          y=-3    , dy=1              , yu=Unit(),
          u=None  , du=None           , mu=None,
          v=None  , dv=None           , mv=None,
          implied=False)
        # Value 5: Zero
        if(True):
          # Value 1: Int
          meas_meas_add(
            x=4     , dx=2              , xu=Unit(), 
            y=0     , dy=1              , yu=Unit(), 
            u=None  , du=None           , mu=None,
            v=None  , dv=None           , mv=None,
            implied=False)
          # Value 2: Float
          meas_meas_add(
            x=0.4   , dx=0.2            , xu=Unit(), 
            y=0.0   , dy=0.1            , yu=Unit(), 
            u=None  , du=None           , mu=None,
            v=None  , dv=None           , mv=None,
            implied=False)
          # Value 3: Decimal
          meas_meas_add(
            x=Decimal("40") , dx=Decimal("20")  , xu=Unit(), 
            y=Decimal("0")  , dy=Decimal("10")  , yu=Unit(), 
            u=None          , du=None           , mu=None,
            v=None          , dv=None           , mv=None,
            implied=False)
        # Preserve Inputs
        if(True):
          a = Measure(value=4,error=2) 
          b = Measure(value=3,error=2)
          c = a+b
          c = None
          assert a == Measure(value=4,error=2) 
          assert b == Measure(value=3,error=2)
      # Unitless + Unit
      if(True):
        # Normal Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=4,error=2,unit=Unit()) + Measure(value=3,error=1,unit=Unit("cm"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.4,error=0.2,unit=Unit()) + Measure(value=0.3,error=0.1,unit=Unit("cm"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit()) + Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-4,error=2,unit=Unit()) + Measure(value=-3,error=1,unit=Unit("cm"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=2,unit=Unit()) + Measure(value=0,error=1,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=2,unit=Unit()) + Measure(value=3,error=1,unit=Unit("cm"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=0.2,unit=Unit()) + Measure(value=0,error=0.1,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=0.2,unit=Unit()) + Measure(value=0.3,error=0.1,unit=Unit("cm"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit()) + Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit()) + Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=2,unit=Unit()) + Measure(value=0,error=1,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=2,unit=Unit()) + Measure(value=-3,error=1,unit=Unit("cm"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            meas_meas_add(
              x=0     , dx=0              , xu=Unit(), 
              y=3     , dy=1              , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("cm"),
              implied=False)
            meas_meas_add(
              x=4     , dx=2              , xu=Unit(), 
              y=0     , dy=0              , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
            # Value 2: Float
            meas_meas_add(
              x=0     , dx=0              , xu=Unit(), 
              y=0.3   , dy=0.1            , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("cm"),
              implied=False)
            meas_meas_add(
              x=0.4   , dx=0.2            , xu=Unit(), 
              y=0     , dy=0              , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
            # Value 3: Decimal
            meas_meas_add(
              x=Decimal("0")  , dx=Decimal("0")   , xu=Unit(), 
              y=Decimal("30") , dy=Decimal("10")  , yu=Unit("cm"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("cm"),
              implied=False)
            meas_meas_add(
              x=Decimal("40") , dx=Decimal("20")  , xu=Unit(), 
              y=Decimal("0")  , dy=Decimal("0")   , yu=Unit("cm"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
        # Magnitude Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=4,error=2,unit=Unit()) + Measure(value=3,error=1,unit=Unit("5 m^2"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.4,error=0.2,unit=Unit()) + Measure(value=0.3,error=0.1,unit=Unit("5 m^2"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit()) + Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-4,error=2,unit=Unit()) + Measure(value=-3,error=1,unit=Unit("5 m^2"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=2,unit=Unit()) + Measure(value=0,error=1,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=2,unit=Unit()) + Measure(value=3,error=1,unit=Unit("5 m^2"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=0.2,unit=Unit()) + Measure(value=0,error=0.1,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=0.2,unit=Unit()) + Measure(value=0.3,error=0.1,unit=Unit("5 m^2"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit()) + Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit()) + Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=2,unit=Unit()) + Measure(value=0,error=1,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=2,unit=Unit()) + Measure(value=-3,error=1,unit=Unit("5 m^2"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            meas_meas_add(
              x=0     , dx=0              , xu=Unit(), 
              y=3     , dy=1              , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("5 m^2"),
              implied=False)
            meas_meas_add(
              x=4     , dx=2              , xu=Unit(), 
              y=0     , dy=0              , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
            # Value 2: Float
            meas_meas_add(
              x=0     , dx=0              , xu=Unit(), 
              y=0.3   , dy=0.1            , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("5 m^2"),
              implied=False)
            meas_meas_add(
              x=0.4   , dx=0.2            , xu=Unit(), 
              y=0     , dy=0              , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
            # Value 3: Decimal
            meas_meas_add(
              x=Decimal("0")  , dx=Decimal("0")   , xu=Unit(), 
              y=Decimal("30") , dy=Decimal("10")  , yu=Unit("5 m^2"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("5 m^2"),
              implied=False)
            meas_meas_add(
              x=Decimal("40") , dx=Decimal("20")  , xu=Unit(), 
              y=Decimal("0")  , dy=Decimal("0")   , yu=Unit("5 m^2"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
        # Convoluted Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=300,error=2,unit=Unit()) + Measure(value=27,error=1,unit=Unit("\u00B0C"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=299.9,error=0.02,unit=Unit()) + Measure(value=26.85,error=0.01,unit=Unit("\u00B0C"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit()) + Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=300,error=2,unit=Unit()) + Measure(value=-27,error=1,unit=Unit("\u00B0C"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300,error=2,unit=Unit()) + Measure(value=0,error=1,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=2,unit=Unit()) + Measure(value=27,error=1,unit=Unit("\u00B0C"))
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300.0,error=0.02,unit=Unit()) + Measure(value=0.0,error=0.01,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=0.02,unit=Unit()) + Measure(value=26.85,error=0.01,unit=Unit("\u00B0C"))
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit()) + Measure(value=Decimal("0"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("0.02"),unit=Unit()) + Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300,error=2,unit=Unit()) + Measure(value=0,error=0,unit=Unit("\u00B0C"))
            meas_meas_add(
              x=0             , dx=0              , xu=Unit(), 
              y=27            , dy=1              , yu=Unit("\u00B0C"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("\u00B0C"),
              implied=False)
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300.0,error=0.02,unit=Unit()) + Measure(value=0.0,error=0.0,unit=Unit("\u00B0C"))
            meas_meas_add(
              x=0             , dx=0              , xu=Unit(), 
              y=26.85         , dy=0.01           , yu=Unit("\u00B0C"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("\u00B0C"),
              implied=False)
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit()) + Measure(value=Decimal("0"),error=Decimal("0"),unit=Unit("\u00B0C"))
            meas_meas_add(
              x=Decimal("0")      , dx=Decimal("0")     , xu=Unit(), 
              y=Decimal("26.85")  , dy=Decimal("0.01")  , yu=Unit("\u00B0C"), 
              u=None              , du=None             , mu=None,
              v=None              , dv=None             , mv=None,
              unit=Unit("\u00B0C"), 
              implied=False)
      # Unit + Unitless
      if(True):
        # Normal Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=3,error=1,unit=Unit("cm")) + Measure(value=4,error=2,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.3,error=0.1,unit=Unit("cm")) + Measure(value=0.4,error=0.2,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm")) + Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-3,error=1,unit=Unit("cm")) + Measure(value=-4,error=2,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=1,unit=Unit("cm")) + Measure(value=4,error=2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=1,unit=Unit("cm")) + Measure(value=0,error=2,unit=Unit())
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=0.1,unit=Unit("cm")) + Measure(value=0.4,error=0.2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=0.1,unit=Unit("cm")) + Measure(value=0,error=0.2,unit=Unit())
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("cm")) + Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm")) + Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit())
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=1,unit=Unit("cm")) + Measure(value=-4,error=2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-3,error=1,unit=Unit("cm")) + Measure(value=0,error=2,unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            meas_meas_add(
              x=3     , dx=1              , xu=Unit("cm"), 
              y=0     , dy=0              , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("cm"),
              implied=False)
            meas_meas_add(
              x=0     , dx=0              , xu=Unit("cm"), 
              y=4     , dy=2              , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
            # Value 2: Float
            meas_meas_add(
              x=0.3   , dx=0.1            , xu=Unit("cm"), 
              y=0     , dy=0              , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("cm"),
              implied=False)
            meas_meas_add(
              x=0     , dx=0              , xu=Unit("cm"), 
              y=0.4   , dy=0.2            , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
            # Value 3: Decimal
            meas_meas_add(
              x=Decimal("30") , dx=Decimal("10")  , xu=Unit("cm"), 
              y=Decimal("0")  , dy=Decimal("0")   , yu=Unit(), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("cm"),
              implied=False)
            meas_meas_add(
              x=Decimal("0")  , dx=Decimal("0")   , xu=Unit("cm"), 
              y=Decimal("40") , dy=Decimal("20")  , yu=Unit(), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
        # Magnitude Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=3,error=1,unit=Unit("5 m^2")) + Measure(value=4,error=2,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.3,error=0.1,unit=Unit("5 m^2")) + Measure(value=0.4,error=0.2,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2")) + Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-3,error=1,unit=Unit("5 m^2")) + Measure(value=-4,error=2,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=1,unit=Unit("5 m^2")) + Measure(value=4,error=2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=1,unit=Unit("5 m^2")) + Measure(value=0,error=2,unit=Unit())
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=0.1,unit=Unit("5 m^2")) + Measure(value=0.4,error=0.2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=0.1,unit=Unit("5 m^2")) + Measure(value=0,error=0.2,unit=Unit())
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("5 m^2")) + Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2")) + Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit())
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=1,unit=Unit("5 m^2")) + Measure(value=-4,error=2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-3,error=1,unit=Unit("5 m^2")) + Measure(value=0,error=2,unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            meas_meas_add(
              x=3     , dx=1              , xu=Unit("5 m^2"), 
              y=0     , dy=0              , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("5 m^2"),
              implied=False)
            meas_meas_add(
              x=0     , dx=0              , xu=Unit("5 m^2"), 
              y=4     , dy=2              , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
            # Value 2: Float
            meas_meas_add(
              x=0.3   , dx=0.1            , xu=Unit("5 m^2"), 
              y=0     , dy=0              , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("5 m^2"),
              implied=False)
            meas_meas_add(
              x=0     , dx=0              , xu=Unit("5 m^2"), 
              y=0.4   , dy=0.2            , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
            # Value 3: Decimal
            meas_meas_add(
              x=Decimal("30") , dx=Decimal("10")  , xu=Unit("5 m^2"), 
              y=Decimal("0")  , dy=Decimal("0")   , yu=Unit(), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("5 m^2"),
              implied=False)
            meas_meas_add(
              x=Decimal("0")  , dx=Decimal("0")   , xu=Unit("5 m^2"), 
              y=Decimal("40") , dy=Decimal("20")  , yu=Unit(), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
        # Convoluted Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=27,error=1,unit=Unit("\u00B0C")) + Measure(value=300,error=2,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=26.85,error=0.01,unit=Unit("\u00B0C")) + Measure(value=299.9,error=0.02,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C")) + Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-27,error=1,unit=Unit("\u00B0C")) + Measure(value=300,error=2,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=1,unit=Unit("\u00B0C")) + Measure(value=300,error=2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=27,error=1,unit=Unit("\u00B0C")) + Measure(value=0,error=2,unit=Unit())
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=0.01,unit=Unit("\u00B0C")) + Measure(value=300.0,error=0.02,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=26.85,error=0.01,unit=Unit("\u00B0C")) + Measure(value=0.0,error=0.02,unit=Unit())
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("0.01"),unit=Unit("\u00B0C")) + Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C")) + Measure(value=Decimal("0"),error=Decimal("0.02"),unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=0,unit=Unit("\u00B0C")) + Measure(value=300,error=2,unit=Unit())
            meas_meas_add(
              x=27            , dx=1              , xu=Unit("\u00B0C"), 
              y=0             , dy=0              , yu=Unit(), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("\u00B0C"),
              implied=False)
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=0.0,unit=Unit("\u00B0C")) + Measure(value=300.0,error=0.02,unit=Unit())
            meas_meas_add(
              x=26.85         , dx=0.01           , xu=Unit("\u00B0C"), 
              y=0             , dy=0              , yu=Unit(), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("\u00B0C"),
              implied=False)
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("0"),unit=Unit("\u00B0C")) + Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit())
            meas_meas_add(
              x=Decimal("26.85")  , dx=Decimal("0.01")  , xu=Unit("\u00B0C"), 
              y=Decimal("0")      , dy=Decimal("0")     , yu=Unit(), 
              u=None              , du=None             , mu=None,
              v=None              , dv=None             , mv=None,
              unit=Unit("\u00B0C"), 
              implied=False)
      # Unit + Unit
      if(True):
        # Same Units
        if(True):
          # Normal Units
          if(True):
            # Value 1: Int
            meas_meas_add(
              x=4     , dx=2              , xu=Unit("cm"), 
              y=3     , dy=1              , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              implied=False)
            # Value 2: Float
            meas_meas_add(
              x=0.4   , dx=0.2            , xu=Unit("cm"), 
              y=0.3   , dy=0.1            , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              implied=False)
            # Value 3: Decimal
            meas_meas_add(
              x=Decimal("40") , dx=Decimal("20")  , xu=Unit("cm"), 
              y=Decimal("30") , dy=Decimal("10")  , yu=Unit("cm"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              implied=False)
            # Value 4: Negative
            meas_meas_add(
              x=-4    , dx=2              , xu=Unit("cm"), 
              y=-3    , dy=1              , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              implied=False)
            # Value 5: Zero
            if(True):
              # Value 1: Int
              meas_meas_add(
                x=0     , dx=2              , xu=Unit("cm"), 
                y=3     , dy=1              , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
              meas_meas_add(
                x=4     , dx=2              , xu=Unit("cm"), 
                y=0     , dy=1              , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
              # Value 2: Float
              meas_meas_add(
                x=0.0   , dx=0.2            , xu=Unit("cm"), 
                y=0.3   , dy=0.1            , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
              meas_meas_add(
                x=0.4   , dx=0.2            , xu=Unit("cm"), 
                y=0.0   , dy=0.1            , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
              # Value 3: Decimal
              meas_meas_add(
                x=Decimal("0")  , dx=Decimal("20")  , xu=Unit("cm"), 
                y=Decimal("30") , dy=Decimal("10")  , yu=Unit("cm"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=None           , mv=None,
                implied=False)
              meas_meas_add(
                x=Decimal("40") , dx=Decimal("20")  , xu=Unit("cm"), 
                y=Decimal("0")  , dy=Decimal("10")  , yu=Unit("cm"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=None           , mv=None,
                implied=False)
              # Value 4: Negative
              meas_meas_add(
                x=0     , dx=2              , xu=Unit("cm"), 
                y=-3    , dy=1              , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
              meas_meas_add(
                x=-4    , dx=2              , xu=Unit("cm"), 
                y=0     , dy=1              , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
          # Magnitude Units
          if(True):
            # Value 1: Int
            meas_meas_add(
              x=4     , dx=2              , xu=Unit("5 m^2"), 
              y=3     , dy=1              , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              implied=False)
            # Value 2: Float
            meas_meas_add(
              x=0.4   , dx=0.2            , xu=Unit("5 m^2"), 
              y=0.3   , dy=0.1            , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              implied=False)
            # Value 3: Decimal
            meas_meas_add(
              x=Decimal("40") , dx=Decimal("20")  , xu=Unit("5 m^2"), 
              y=Decimal("30") , dy=Decimal("10")  , yu=Unit("5 m^2"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              implied=False)
            # Value 4: Negative
            meas_meas_add(
              x=-4    , dx=2              , xu=Unit("5 m^2"), 
              y=-3    , dy=1              , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              implied=False)
            # Value 5: Zero
            if(True):
              # Value 1: Int
              meas_meas_add(
                x=0     , dx=2              , xu=Unit("5 m^2"), 
                y=3     , dy=1              , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
              meas_meas_add(
                x=4     , dx=2              , xu=Unit("5 m^2"), 
                y=0     , dy=1              , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
              # Value 2: Float
              meas_meas_add(
                x=0.0   , dx=0.2            , xu=Unit("5 m^2"), 
                y=0.3   , dy=0.1            , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
              meas_meas_add(
                x=0.4   , dx=0.2            , xu=Unit("5 m^2"), 
                y=0.0   , dy=0.1            , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
              # Value 3: Decimal
              meas_meas_add(
                x=Decimal("0")  , dx=Decimal("20")  , xu=Unit("5 m^2"), 
                y=Decimal("30") , dy=Decimal("10")  , yu=Unit("5 m^2"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=None           , mv=None,
                implied=False)
              meas_meas_add(
                x=Decimal("40") , dx=Decimal("20")  , xu=Unit("5 m^2"), 
                y=Decimal("0")  , dy=Decimal("10")  , yu=Unit("5 m^2"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=None           , mv=None,
                implied=False)
              # Value 4: Negative
              meas_meas_add(
                x=0     , dx=2              , xu=Unit("5 m^2"), 
                y=-3    , dy=1              , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
              meas_meas_add(
                x=-4    , dx=2              , xu=Unit("5 m^2"), 
                y=0     , dy=1              , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
          # Convoluted Units
          if(True):
            # Value 1: Int
            meas_meas_add(
              x=26                , dx=2    , xu=Unit("\u00B0C"), 
              y=27                , dy=1    , yu=Unit("\u00B0C"), 
              u=Decimal("299.85") , du=None , mu=None,
              v=Decimal("300.15") , dv=None , mv=None,
              value = Decimal("299.85") + Decimal("300.15") - Decimal("273.85"),
              implied=False)
            # Value 2: Float
            meas_meas_add(
              x=26.85 , dx=0.02 , xu=Unit("\u00B0C"), 
              y=26.85 , dy=0.01 , yu=Unit("\u00B0C"), 
              u=300.0 , du=None , mu=None,
              v=300.0 , dv=None , mv=None,
              value = 300.0 + 300.0 - 273.15,
              implied=False)
            # Value 3: Decimal
            meas_meas_add(
              x=Decimal("26.85")  , dx=Decimal("0.02")  , xu=Unit("\u00B0C"), 
              y=Decimal("26.85")  , dy=Decimal("0.01")  , yu=Unit("\u00B0C"), 
              u=Decimal("300")    , du=None             , mu=None,
              v=Decimal("300")    , dv=None             , mv=None,
              value = Decimal("300") + Decimal("300") - Decimal("273.15"),
              implied=False)
            # Value 4: Negative
            meas_meas_add(
              x=-31               , dx=2    , xu=Unit("\u00B0C"), 
              y=-27               , dy=1    , yu=Unit("\u00B0C"), 
              u=Decimal("242.15") , du=None , mu=None,
              v=Decimal("246.15") , dv=None , mv=None,
              value = Decimal("242.15") + Decimal("246.15") - Decimal("273.15"),
              implied=False)
            # Value 5: Zero
            if(True):
              # Int
              meas_meas_add(
                x=27                , dx=2    , xu=Unit("\u00B0C"), 
                y=0                 , dy=1    , yu=Unit("\u00B0C"), 
                u=Decimal("300.15") , du=None , mu=None,
                v=Decimal("273.15") , dv=None , mv=None,
                value = Decimal("300.15") + Decimal("273.15") - Decimal("273.15"),
                implied=False)
              # Float
              meas_meas_add(
                x=26.85   , dx=0.02 , xu=Unit("\u00B0C"), 
                y=0.0     , dy=0.01 , yu=Unit("\u00B0C"), 
                u=300.0   , du=None , mu=None,
                v=273.15  , dv=None , mv=None,
                value = 300.0+273.15-273.15,
                implied=False)
              # Decimal
              meas_meas_add(
                x=Decimal("26.85")  , dx=Decimal("0.02"), xu=Unit("\u00B0C"), 
                y=Decimal("0")      , dy=Decimal("0.01"), yu=Unit("\u00B0C"), 
                u=Decimal("300")    , du=None           , mu=None,
                v=Decimal("273.15") , dv=None           , mv=None,
                value = Decimal("300") + Decimal("273.15") - Decimal("273.15"),
                implied=False)
        # Different Units
        if(True):
          # Normal Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=2,unit=Unit("s")) + Measure(value=3,error=1,unit=Unit("cm"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=0.2,unit=Unit("s")) + Measure(value=0.3,error=0.1,unit=Unit("cm"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("s")) + Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=2,unit=Unit("s")) + Measure(value=-3,error=1,unit=Unit("cm"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=2,unit=Unit("s")) + Measure(value=0,error=1,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=2,unit=Unit("s")) + Measure(value=3,error=1,unit=Unit("cm"))
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=0.2,unit=Unit("s")) + Measure(value=0,error=0.1,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=0.2,unit=Unit("s")) + Measure(value=0.3,error=0.1,unit=Unit("cm"))
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("s")) + Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit("s")) + Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm"))
              # Value 4: Negative
              with pytest.raises(IncompatibleUnitException):
                Measure(value=-4,error=2,unit=Unit("s")) + Measure(value=0,error=1,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=2,unit=Unit("s")) + Measure(value=-3,error=1,unit=Unit("cm"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Value 1: Int
              meas_meas_add(
                x=0     , dx=0              , xu=Unit("s"), 
                y=3     , dy=1              , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("cm"),
                implied=False)
              meas_meas_add(
                x=4     , dx=2              , xu=Unit("s"), 
                y=0     , dy=0              , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("s"),
                implied=False)
              # Value 2: Float
              meas_meas_add(
                x=0     , dx=0              , xu=Unit("s"), 
                y=0.3   , dy=0.1            , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("cm"),
                implied=False)
              meas_meas_add(
                x=0.4   , dx=0.2            , xu=Unit("s"), 
                y=0     , dy=0              , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("s"),
                implied=False)
              # Value 3: Decimal
              meas_meas_add(
                x=Decimal("0")  , dx=Decimal("0")   , xu=Unit("s"), 
                y=Decimal("30") , dy=Decimal("10")  , yu=Unit("cm"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=None           , mv=None,
                unit=Unit("cm"),
                implied=False)
              meas_meas_add(
                x=Decimal("40") , dx=Decimal("20")  , xu=Unit("s"), 
                y=Decimal("0")  , dy=Decimal("0")   , yu=Unit("cm"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=None           , mv=None,
                unit=Unit("s"),
                implied=False)
          # Magnitude Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=2,unit=Unit("5 s")) + Measure(value=3,error=1,unit=Unit("5 m^2"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=0.2,unit=Unit("5 s")) + Measure(value=0.3,error=0.1,unit=Unit("5 m^2"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("5 s")) + Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=2,unit=Unit("5 s")) + Measure(value=-3,error=1,unit=Unit("5 m^2"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=2,unit=Unit("5 s")) + Measure(value=0,error=1,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=2,unit=Unit("5 s")) + Measure(value=3,error=1,unit=Unit("5 m^2"))
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=0.2,unit=Unit("5 s")) + Measure(value=0,error=0.1,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=0.2,unit=Unit("5 s")) + Measure(value=0.3,error=0.1,unit=Unit("5 m^2"))
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("5 s")) + Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit("5 s")) + Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2"))
              # Value 4: Negative
              with pytest.raises(IncompatibleUnitException):
                Measure(value=-4,error=2,unit=Unit("5 s")) + Measure(value=0,error=1,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=2,unit=Unit("5 s")) + Measure(value=-3,error=1,unit=Unit("5 m^2"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Value 1: Int
              meas_meas_add(
                x=0     , dx=0              , xu=Unit("5 s"), 
                y=3     , dy=1              , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("5 m^2"),
                implied=False)
              meas_meas_add(
                x=4     , dx=2              , xu=Unit("5 s"), 
                y=0     , dy=0              , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("5 s"),
                implied=False)
              # Value 2: Float
              meas_meas_add(
                x=0     , dx=0              , xu=Unit("5 s"), 
                y=0.3   , dy=0.1            , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("5 m^2"),
                implied=False)
              meas_meas_add(
                x=0.4   , dx=0.2            , xu=Unit("5 s"), 
                y=0     , dy=0              , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("5 s"),
                implied=False)
              # Value 3: Decimal
              meas_meas_add(
                x=Decimal("0")  , dx=Decimal("0")   , xu=Unit("5 s"), 
                y=Decimal("30") , dy=Decimal("10")  , yu=Unit("5 m^2"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=None           , mv=None,
                unit=Unit("5 m^2"),
                implied=False)
              meas_meas_add(
                x=Decimal("40") , dx=Decimal("20")  , xu=Unit("5 s"), 
                y=Decimal("0")  , dy=Decimal("0")   , yu=Unit("5 m^2"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=None           , mv=None,
                unit=Unit("5 s"),
                implied=False)
          # Convoluted Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=2,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=27,error=1,unit=Unit("\u00B0C"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=2.9,error=0.02,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=26.85,error=0.01,unit=Unit("\u00B0C"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("3"),error=Decimal("0.02"),unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=2,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=-27,error=1,unit=Unit("\u00B0C"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=3,error=2,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=0,error=1,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=2,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=27,error=1,unit=Unit("\u00B0C"))
              # Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=3.0,error=0.02,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=0.0,error=0.01,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=0.02,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=26.85,error=0.01,unit=Unit("\u00B0C"))
              # Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("3"),error=Decimal("0.02"),unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=Decimal("0"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=Decimal("0.02"),unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=0,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=0,error=0,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=0,unit=Unit("\u00B0C")) + Measure(value=0,error=0,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
              # Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=0.0,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=0.0,error=0.0,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=0.0,unit=Unit("\u00B0C")) + Measure(value=0.0,error=0.0,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
              # Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=Decimal("0.0"),unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=Decimal("0"),error=Decimal("0"),unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=Decimal("0"),unit=Unit("\u00B0C")) + Measure(value=Decimal("0"),error=Decimal("0.0"),unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
    # Measure (Explicit Error) + Measure (Implicit Error) = Measure (Implicit Error)
    if(True):
      # Unitless + Unitless
      if(True):
        # Value 1: Int
        meas_meas_add(
          x=4     , dx=2              , xu=Unit(), 
          y=3     , dy=None           , yu=Unit(), 
          u=None  , du=None           , mu=None,
          v=None  , dv=Decimal("0.5") , mv=None,
          implied=True)
        # Value 2: Float
        meas_meas_add(
          x=0.4   , dx=0.2            , xu=Unit(), 
          y=0.3   , dy=None           , yu=Unit(), 
          u=None  , du=None           , mu=None,
          v=None  , dv=0.05           , mv=None,
          implied=True)
        # Value 3: Decimal
        meas_meas_add(
          x=Decimal("40") , dx=Decimal("20")  , xu=Unit(), 
          y=Decimal("30") , dy=None           , yu=Unit(), 
          u=None          , du=None           , mu=None,
          v=None          , dv=Decimal("5")   , mv=None,
          implied=True)
        # Value 4: Negative
        meas_meas_add(
          x=-4    , dx=2              , xu=Unit(), 
          y=-3    , dy=None           , yu=Unit(),
          u=None  , du=None           , mu=None,
          v=None  , dv=Decimal("0.5") , mv=None,
          implied=True)
        # Value 5: Zero
        if(True):
          # Value 1: Int
          meas_meas_add(
            x=4     , dx=2              , xu=Unit(), 
            y=0     , dy=None           , yu=Unit(), 
            u=None  , du=None           , mu=None,
            v=None  , dv=Decimal("0.5") , mv=None,
            implied=True)
          # Value 2: Float
          meas_meas_add(
            x=0.4   , dx=0.2            , xu=Unit(), 
            y=0.0   , dy=None           , yu=Unit(), 
            u=None  , du=None           , mu=None,
            v=None  , dv=0.05           , mv=None,
            implied=True)
          # Value 3: Decimal
          meas_meas_add(
            x=Decimal("40") , dx=Decimal("20")  , xu=Unit(), 
            y=Decimal("0")  , dy=None           , yu=Unit(), 
            u=None          , du=None           , mu=None,
            v=None          , dv=Decimal("0.5") , mv=None,
            implied=True)
        # Preserve Inputs
        if(True):
          a = Measure(value=4,error=2) 
          b = Measure(value=3,error=None)
          c = a+b
          c = None
          assert a == Measure(value=4,error=2) 
          assert b == Measure(value=3,error=None)
      # Unitless + Unit
      if(True):
        # Normal Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=4,error=2,unit=Unit()) + Measure(value=3,error=None,unit=Unit("cm"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.4,error=0.2,unit=Unit()) + Measure(value=0.3,error=None,unit=Unit("cm"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit()) + Measure(value=Decimal("30"),error=None,unit=Unit("cm"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-4,error=2,unit=Unit()) + Measure(value=-3,error=None,unit=Unit("cm"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=2,unit=Unit()) + Measure(value=0,error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=2,unit=Unit()) + Measure(value=3,error=None,unit=Unit("cm"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=0.2,unit=Unit()) + Measure(value=0,error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=0.2,unit=Unit()) + Measure(value=0.3,error=None,unit=Unit("cm"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit()) + Measure(value=Decimal("0"),error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit()) + Measure(value=Decimal("30"),error=None,unit=Unit("cm"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=2,unit=Unit()) + Measure(value=0,error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=2,unit=Unit()) + Measure(value=-3,error=None,unit=Unit("cm"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            meas_meas_add(
              x=0     , dx=0              , xu=Unit(), 
              y=3     , dy=None           , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              unit=Unit("cm"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=2,unit=Unit()) + Measure(value=0,error=None,unit=Unit("cm"))
            # Value 2: Float
            meas_meas_add(
              x=0     , dx=0              , xu=Unit(), 
              y=0.3   , dy=None           , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=0.05           , mv=None,
              unit=Unit("cm"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=0.2,unit=Unit()) + Measure(value=0,error=None,unit=Unit("cm"))
            # Value 3: Decimal
            meas_meas_add(
              x=Decimal("0")  , dx=Decimal("0")   , xu=Unit(), 
              y=Decimal("30") , dy=None           , yu=Unit("cm"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=Decimal("5")   , mv=None,
              unit=Unit("cm"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit()) + Measure(value=Decimal("0"),error=None,unit=Unit("cm"))
        # Magnitude Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=4,error=2,unit=Unit()) + Measure(value=3,error=None,unit=Unit("5 m^2"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.4,error=0.2,unit=Unit()) + Measure(value=0.3,error=None,unit=Unit("5 m^2"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit()) + Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-4,error=2,unit=Unit()) + Measure(value=-3,error=None,unit=Unit("5 m^2"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=2,unit=Unit()) + Measure(value=0,error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=2,unit=Unit()) + Measure(value=3,error=None,unit=Unit("5 m^2"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=0.2,unit=Unit()) + Measure(value=0,error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=0.2,unit=Unit()) + Measure(value=0.3,error=None,unit=Unit("5 m^2"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit()) + Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit()) + Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=2,unit=Unit()) + Measure(value=0,error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=2,unit=Unit()) + Measure(value=-3,error=None,unit=Unit("5 m^2"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            meas_meas_add(
              x=0     , dx=0              , xu=Unit(), 
              y=3     , dy=None           , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              unit=Unit("5 m^2"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=2,unit=Unit()) + Measure(value=0,error=None,unit=Unit("5 m^2"))
            # Value 2: Float
            meas_meas_add(
              x=0     , dx=0              , xu=Unit(), 
              y=0.3   , dy=None           , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=0.05           , mv=None,
              unit=Unit("5 m^2"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=0.2,unit=Unit()) + Measure(value=0.0,error=None,unit=Unit("5 m^2"))
            # Value 3: Decimal
            meas_meas_add(
              x=Decimal("0")  , dx=Decimal("0")   , xu=Unit(), 
              y=Decimal("30") , dy=None           , yu=Unit("5 m^2"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=Decimal("5")   , mv=None,
              unit=Unit("5 m^2"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit()) + Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2"))
        # Convoluted Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=300,error=2,unit=Unit()) + Measure(value=27,error=None,unit=Unit("\u00B0C"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=299.9,error=0.02,unit=Unit()) + Measure(value=26.85,error=None,unit=Unit("\u00B0C"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit()) + Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=300,error=2,unit=Unit()) + Measure(value=-27,error=None,unit=Unit("\u00B0C"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300,error=2,unit=Unit()) + Measure(value=0,error=None,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=2,unit=Unit()) + Measure(value=27,error=None,unit=Unit("\u00B0C"))
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300.0,error=0.02,unit=Unit()) + Measure(value=0.0,error=None,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=0.02,unit=Unit()) + Measure(value=26.85,error=None,unit=Unit("\u00B0C"))
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit()) + Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("0.02"),unit=Unit()) + Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300,error=2,unit=Unit()) + Measure(value=0,error=None,unit=Unit("\u00B0C"))
            meas_meas_add(
              x=0             , dx=0              , xu=Unit(), 
              y=27            , dy=None           , yu=Unit("\u00B0C"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=Decimal("0.5") , mv=None,
              unit=Unit("\u00B0C"),
              implied=True)
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300.0,error=0.02,unit=Unit()) + Measure(value=0.0,error=None,unit=Unit("\u00B0C"))
            meas_meas_add(
              x=0             , dx=0              , xu=Unit(), 
              y=26.85         , dy=None           , yu=Unit("\u00B0C"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=0.005          , mv=None,
              unit=Unit("\u00B0C"),
              implied=True)
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit()) + Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C"))
            meas_meas_add(
              x=Decimal("0")      , dx=Decimal("0")     , xu=Unit(), 
              y=Decimal("26.85")  , dy=None             , yu=Unit("\u00B0C"), 
              u=None              , du=None             , mu=None,
              v=None              , dv=Decimal("0.005") , mv=None,
              unit=Unit("\u00B0C"), 
              implied=True)
      # Unit + Unitless
      if(True):
        # Normal Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=3,error=1,unit=Unit("cm")) + Measure(value=4,error=None,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.3,error=0.1,unit=Unit("cm")) + Measure(value=0.4,error=None,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm")) + Measure(value=Decimal("40"),error=None,unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-3,error=1,unit=Unit("cm")) + Measure(value=-4,error=None,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=1,unit=Unit("cm")) + Measure(value=4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=1,unit=Unit("cm")) + Measure(value=0,error=None,unit=Unit())
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=0.1,unit=Unit("cm")) + Measure(value=0.4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=0.1,unit=Unit("cm")) + Measure(value=0,error=None,unit=Unit())
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("cm")) + Measure(value=Decimal("40"),error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm")) + Measure(value=Decimal("0"),error=None,unit=Unit())
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=1,unit=Unit("cm")) + Measure(value=-4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-3,error=1,unit=Unit("cm")) + Measure(value=0,error=None,unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=1,unit=Unit("cm")) + Measure(value=0,error=None,unit=Unit())
            meas_meas_add(
              x=0     , dx=0              , xu=Unit("cm"), 
              y=4     , dy=None           , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              unit=Unit(),
              implied=True)
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=0.1,unit=Unit("cm")) + Measure(value=0.0,error=None,unit=Unit())
            meas_meas_add(
              x=0     , dx=0              , xu=Unit("cm"), 
              y=0.4   , dy=None           , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=0.05           , mv=None,
              unit=Unit(),
              implied=True)
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm")) + Measure(value=Decimal("0"),error=None,unit=Unit())
            meas_meas_add(
              x=Decimal("0")  , dx=Decimal("0")   , xu=Unit("cm"), 
              y=Decimal("40") , dy=None           , yu=Unit(), 
              u=None          , du=None           , mu=None,
              v=None          , dv=Decimal("5")   , mv=None,
              unit=Unit(),
              implied=True)
        # Magnitude Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=3,error=1,unit=Unit("5 m^2")) + Measure(value=4,error=None,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.3,error=0.1,unit=Unit("5 m^2")) + Measure(value=0.4,error=None,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2")) + Measure(value=Decimal("40"),error=None,unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-3,error=1,unit=Unit("5 m^2")) + Measure(value=-4,error=None,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=1,unit=Unit("5 m^2")) + Measure(value=4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=1,unit=Unit("5 m^2")) + Measure(value=0,error=None,unit=Unit())
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=0.1,unit=Unit("5 m^2")) + Measure(value=0.4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=0.1,unit=Unit("5 m^2")) + Measure(value=0,error=None,unit=Unit())
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("5 m^2")) + Measure(value=Decimal("40"),error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2")) + Measure(value=Decimal("0"),error=None,unit=Unit())
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=1,unit=Unit("5 m^2")) + Measure(value=-4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-3,error=1,unit=Unit("5 m^2")) + Measure(value=0,error=None,unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=1,unit=Unit("5 m^2")) + Measure(value=0,error=None,unit=Unit())
            meas_meas_add(
              x=0     , dx=0              , xu=Unit("5 m^2"), 
              y=4     , dy=None           , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              unit=Unit(),
              implied=True)
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=0.1,unit=Unit("5 m^2")) + Measure(value=0.0,error=None,unit=Unit())
            meas_meas_add(
              x=0     , dx=0              , xu=Unit("5 m^2"), 
              y=0.4   , dy=None           , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=0.05           , mv=None,
              unit=Unit(),
              implied=True)
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2")) + Measure(value=Decimal("0"),error=None,unit=Unit())
            meas_meas_add(
              x=Decimal("0")  , dx=Decimal("0")   , xu=Unit("5 m^2"), 
              y=Decimal("40") , dy=None           , yu=Unit(), 
              u=None          , du=None           , mu=None,
              v=None          , dv=Decimal("5")   , mv=None,
              unit=Unit(),
              implied=True)
        # Convoluted Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=27,error=1,unit=Unit("\u00B0C")) + Measure(value=300,error=None,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=26.85,error=0.01,unit=Unit("\u00B0C")) + Measure(value=299.9,error=None,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C")) + Measure(value=Decimal("300"),error=None,unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-27,error=1,unit=Unit("\u00B0C")) + Measure(value=300,error=None,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=1,unit=Unit("\u00B0C")) + Measure(value=300,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=27,error=1,unit=Unit("\u00B0C")) + Measure(value=0,error=None,unit=Unit())
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=0.01,unit=Unit("\u00B0C")) + Measure(value=300.0,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=26.85,error=0.01,unit=Unit("\u00B0C")) + Measure(value=0.0,error=None,unit=Unit())
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("0.01"),unit=Unit("\u00B0C")) + Measure(value=Decimal("300"),error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C")) + Measure(value=Decimal("0"),error=None,unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=0,unit=Unit("\u00B0C")) + Measure(value=300,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=27,error=1,unit=Unit("\u00B0C")) + Measure(value=0,error=None,unit=Unit())
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=0.0,unit=Unit("\u00B0C")) + Measure(value=300.0,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=26.85,error=0.01,unit=Unit("\u00B0C")) + Measure(value=0.0,error=None,unit=Unit())
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("0"),unit=Unit("\u00B0C")) + Measure(value=Decimal("300"),error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C")) + Measure(value=Decimal("0"),error=None,unit=Unit())
      # Unit + Unit
      if(True):
        # Same Units
        if(True):
          # Normal Units
          if(True):
            # Value 1: Int
            meas_meas_add(
              x=4     , dx=2              , xu=Unit("cm"), 
              y=3     , dy=None           , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              implied=True)
            # Value 2: Float
            meas_meas_add(
              x=0.4   , dx=0.2            , xu=Unit("cm"), 
              y=0.3   , dy=None           , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=0.05           , mv=None,
              implied=True)
            # Value 3: Decimal
            meas_meas_add(
              x=Decimal("40") , dx=Decimal("20")  , xu=Unit("cm"), 
              y=Decimal("30") , dy=None           , yu=Unit("cm"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=Decimal("5")   , mv=None,
              implied=True)
            # Value 4: Negative
            meas_meas_add(
              x=-4    , dx=2              , xu=Unit("cm"), 
              y=-3    , dy=None           , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              implied=True)
            # Value 5: Zero
            if(True):
              # Value 1: Int
              meas_meas_add(
                x=0     , dx=2              , xu=Unit("cm"), 
                y=3     , dy=None           , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              meas_meas_add(
                x=4     , dx=2              , xu=Unit("cm"), 
                y=0     , dy=None           , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              # Value 2: Float
              meas_meas_add(
                x=0.0   , dx=0.2            , xu=Unit("cm"), 
                y=0.3   , dy=None           , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=0.05           , mv=None,
                implied=True)
              meas_meas_add(
                x=0.4   , dx=0.2            , xu=Unit("cm"), 
                y=0.0   , dy=None           , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=0.05           , mv=None,
                implied=True)
              # Value 3: Decimal
              meas_meas_add(
                x=Decimal("0")  , dx=Decimal("20")  , xu=Unit("cm"), 
                y=Decimal("30") , dy=None           , yu=Unit("cm"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=Decimal("5")   , mv=None,
                implied=True)
              meas_meas_add(
                x=Decimal("40") , dx=Decimal("20")  , xu=Unit("cm"), 
                y=Decimal("0")  , dy=None           , yu=Unit("cm"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=Decimal("0.5") , mv=None,
                implied=True)
              # Value 4: Negative
              meas_meas_add(
                x=0     , dx=2              , xu=Unit("cm"), 
                y=-3    , dy=None           , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              meas_meas_add(
                x=-4    , dx=2              , xu=Unit("cm"), 
                y=0     , dy=None           , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
          # Magnitude Units
          if(True):
            # Value 1: Int
            meas_meas_add(
              x=4     , dx=2              , xu=Unit("5 m^2"), 
              y=3     , dy=None           , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              implied=True)
            # Value 2: Float
            meas_meas_add(
              x=0.4   , dx=0.2            , xu=Unit("5 m^2"), 
              y=0.3   , dy=None           , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=0.05           , mv=None,
              implied=True)
            # Value 3: Decimal
            meas_meas_add(
              x=Decimal("40") , dx=Decimal("20")  , xu=Unit("5 m^2"), 
              y=Decimal("30") , dy=None           , yu=Unit("5 m^2"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=Decimal("5")   , mv=None,
              implied=True)
            # Value 4: Negative
            meas_meas_add(
              x=-4    , dx=2              , xu=Unit("5 m^2"), 
              y=-3    , dy=None           , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              implied=True)
            # Value 5: Zero
            if(True):
              # Value 1: Int
              meas_meas_add(
                x=0     , dx=2              , xu=Unit("5 m^2"), 
                y=3     , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              meas_meas_add(
                x=4     , dx=2              , xu=Unit("5 m^2"), 
                y=0     , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              # Value 2: Float
              meas_meas_add(
                x=0.0   , dx=0.2            , xu=Unit("5 m^2"), 
                y=0.3   , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=0.05           , mv=None,
                implied=True)
              meas_meas_add(
                x=0.4   , dx=0.2            , xu=Unit("5 m^2"), 
                y=0.0   , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=0.05           , mv=None,
                implied=True)
              # Value 3: Decimal
              meas_meas_add(
                x=Decimal("0")  , dx=Decimal("20")  , xu=Unit("5 m^2"), 
                y=Decimal("30") , dy=None           , yu=Unit("5 m^2"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=Decimal("5")   , mv=None,
                implied=True)
              meas_meas_add(
                x=Decimal("40") , dx=Decimal("20")  , xu=Unit("5 m^2"), 
                y=Decimal("0")  , dy=None           , yu=Unit("5 m^2"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=Decimal("0.5") , mv=None,
                implied=True)
              # Value 4: Negative
              meas_meas_add(
                x=0     , dx=2              , xu=Unit("5 m^2"), 
                y=-3    , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              meas_meas_add(
                x=-4    , dx=2              , xu=Unit("5 m^2"), 
                y=0     , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
          # Convoluted Units
          if(True):
            # Value 1: Int
            meas_meas_add(
              x=26                , dx=2              , xu=Unit("\u00B0C"), 
              y=27                , dy=None           , yu=Unit("\u00B0C"), 
              u=Decimal("299.85") , du=None           , mu=None,
              v=Decimal("300.15") , dv=Decimal("0.5") , mv=None,
              value = Decimal("299.85") + Decimal("300.15") - Decimal("273.85"),
              implied=True)
            # Value 2: Float
            meas_meas_add(
              x=26.85 , dx=0.02  , xu=Unit("\u00B0C"), 
              y=26.85 , dy=None  , yu=Unit("\u00B0C"), 
              u=300.0 , du=None  , mu=None,
              v=300.0 , dv=0.005 , mv=None,
              value = 300.0 + 300.0 - 273.15,
              implied=True)
            # Value 3: Decimal
            meas_meas_add(
              x=Decimal("26.85")  , dx=Decimal("0.02")  , xu=Unit("\u00B0C"), 
              y=Decimal("26.85")  , dy=None             , yu=Unit("\u00B0C"), 
              u=Decimal("300")    , du=None             , mu=None,
              v=Decimal("300")    , dv=Decimal("0.005") , mv=None,
              value = Decimal("300") + Decimal("300") - Decimal("273.15"),
              implied=True)
            # Value 4: Negative
            meas_meas_add(
              x=-31               , dx=2              , xu=Unit("\u00B0C"), 
              y=-27               , dy=None           , yu=Unit("\u00B0C"), 
              u=Decimal("242.15") , du=None           , mu=None,
              v=Decimal("246.15") , dv=Decimal("0.5") , mv=None,
              value = Decimal("242.15") + Decimal("246.15") - Decimal("273.15"),
              implied=True)
            # Value 5: Zero
            if(True):
              # Int
              meas_meas_add(
                x=27                , dx=2              , xu=Unit("\u00B0C"), 
                y=0                 , dy=None           , yu=Unit("\u00B0C"), 
                u=Decimal("300.15") , du=None           , mu=None,
                v=Decimal("273.15") , dv=Decimal("0.5") , mv=None,
                value = Decimal("300.15") + Decimal("273.15") - Decimal("273.15"),
                implied=True)
              # Float
              meas_meas_add(
                x=26.85   , dx=0.02 , xu=Unit("\u00B0C"), 
                y=0.0     , dy=None , yu=Unit("\u00B0C"), 
                u=300.0   , du=None , mu=None,
                v=273.15  , dv=0.05 , mv=None,
                value = 300.0+273.15-273.15,
                implied=True)
              # Decimal
              meas_meas_add(
                x=Decimal("26.85")  , dx=Decimal("0.02"), xu=Unit("\u00B0C"), 
                y=Decimal("0")      , dy=None           , yu=Unit("\u00B0C"), 
                u=Decimal("300")    , du=None           , mu=None,
                v=Decimal("273.15") , dv=Decimal("0.5") , mv=None,
                value = Decimal("300") + Decimal("273.15") - Decimal("273.15"),
                implied=True)
        # Different Units
        if(True):
          # Normal Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=2,unit=Unit("s")) + Measure(value=3,error=None,unit=Unit("cm"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=0.2,unit=Unit("s")) + Measure(value=0.3,error=None,unit=Unit("cm"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("s")) + Measure(value=Decimal("30"),error=None,unit=Unit("cm"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=2,unit=Unit("s")) + Measure(value=-3,error=None,unit=Unit("cm"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=2,unit=Unit("s")) + Measure(value=0,error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=2,unit=Unit("s")) + Measure(value=3,error=None,unit=Unit("cm"))
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=0.2,unit=Unit("s")) + Measure(value=0,error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=0.2,unit=Unit("s")) + Measure(value=0.3,error=None,unit=Unit("cm"))
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("s")) + Measure(value=Decimal("0"),error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit("s")) + Measure(value=Decimal("30"),error=None,unit=Unit("cm"))
              # Value 4: Negative
              with pytest.raises(IncompatibleUnitException):
                Measure(value=-4,error=2,unit=Unit("s")) + Measure(value=0,error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=2,unit=Unit("s")) + Measure(value=-3,error=None,unit=Unit("cm"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Value 1: Int
              meas_meas_add(
                x=0     , dx=0              , xu=Unit("s"), 
                y=3     , dy=None           , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=Decimal("0.5")  , mv=None,
                unit=Unit("cm"),
                implied=True)
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=2,unit=Unit("s")) + Measure(value=0,error=None,unit=Unit("cm"))
              # Value 2: Float
              meas_meas_add(
                x=0     , dx=0              , xu=Unit("s"), 
                y=0.3   , dy=None           , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=0.05           , mv=None,
                unit=Unit("cm"),
                implied=True)
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=0.2,unit=Unit("s")) + Measure(value=0.0,error=None,unit=Unit("cm"))
              # Value 3: Decimal
              meas_meas_add(
                x=Decimal("0")  , dx=Decimal("0")   , xu=Unit("s"), 
                y=Decimal("30") , dy=None           , yu=Unit("cm"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=Decimal("5")   , mv=None,
                unit=Unit("cm"),
                implied=True)
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("s")) + Measure(value=Decimal("0"),error=None,unit=Unit("cm"))
          # Magnitude Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=2,unit=Unit("5 s")) + Measure(value=3,error=None,unit=Unit("5 m^2"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=0.2,unit=Unit("5 s")) + Measure(value=0.3,error=None,unit=Unit("5 m^2"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("5 s")) + Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=2,unit=Unit("5 s")) + Measure(value=-3,error=None,unit=Unit("5 m^2"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=2,unit=Unit("5 s")) + Measure(value=0,error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=2,unit=Unit("5 s")) + Measure(value=3,error=None,unit=Unit("5 m^2"))
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=0.2,unit=Unit("5 s")) + Measure(value=0,error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=0.2,unit=Unit("5 s")) + Measure(value=0.3,error=None,unit=Unit("5 m^2"))
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("5 s")) + Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit("5 s")) + Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2"))
              # Value 4: Negative
              with pytest.raises(IncompatibleUnitException):
                Measure(value=-4,error=2,unit=Unit("5 s")) + Measure(value=0,error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=2,unit=Unit("5 s")) + Measure(value=-3,error=None,unit=Unit("5 m^2"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Value 1: Int
              meas_meas_add(
                x=0     , dx=0              , xu=Unit("5 s"), 
                y=3     , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                unit=Unit("5 m^2"),
                implied=True)
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=2,unit=Unit("5 s")) + Measure(value=0,error=None,unit=Unit("5 m^2"))
              # Value 2: Float
              meas_meas_add(
                x=0     , dx=0              , xu=Unit("5 s"), 
                y=0.3   , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=0.05           , mv=None,
                unit=Unit("5 m^2"),
                implied=True)
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=0.2,unit=Unit("5 s")) + Measure(value=0.0,error=None,unit=Unit("5 m^2"))
              # Value 3: Decimal
              meas_meas_add(
                x=Decimal("0")  , dx=Decimal("0")   , xu=Unit("5 s"), 
                y=Decimal("30") , dy=None           , yu=Unit("5 m^2"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=Decimal("5")   , mv=None,
                unit=Unit("5 m^2"),
                implied=True)
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("5 s")) + Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2"))
          # Convoluted Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=2,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=27,error=None,unit=Unit("\u00B0C"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=2.9,error=0.02,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=26.85,error=None,unit=Unit("\u00B0C"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("3"),error=Decimal("0.02"),unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=2,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=-27,error=None,unit=Unit("\u00B0C"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=3,error=2,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=0,error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=2,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=27,error=None,unit=Unit("\u00B0C"))
              # Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=3.0,error=0.02,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=0.0,error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=0.02,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=26.85,error=None,unit=Unit("\u00B0C"))
              # Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("3"),error=Decimal("0.02"),unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=Decimal("0.02"),unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=0,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=0,error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=0,unit=Unit("\u00B0C")) + Measure(value=0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
              # Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=0.0,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=0.0,error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=0.0,unit=Unit("\u00B0C")) + Measure(value=0.0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
              # Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=Decimal("0.0"),unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=Decimal("0"),unit=Unit("\u00B0C")) + Measure(value=Decimal("0"),error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
    # Measure (Implicit Error) + Measure (Explicit Error) = Measure (Implicit Error)
    if(True):
      # Unitless + Unitless
      if(True):
        # Value 1: Int
        meas_meas_add(
          x=4     , dx=None           , xu=Unit(), 
          y=3     , dy=1              , yu=Unit(), 
          u=None  , du=Decimal("0.5") , mu=None,
          v=None  , dv=None           , mv=None,
          implied=True)
        # Value 2: Float
        meas_meas_add(
          x=0.4   , dx=None           , xu=Unit(), 
          y=0.3   , dy=0.1            , yu=Unit(), 
          u=None  , du=0.05           , mu=None,
          v=None  , dv=None           , mv=None,
          implied=True)
        # Value 3: Decimal
        meas_meas_add(
          x=Decimal("40") , dx=None           , xu=Unit(), 
          y=Decimal("30") , dy=Decimal("10")  , yu=Unit(), 
          u=None          , du=Decimal("5")   , mu=None,
          v=None          , dv=None           , mv=None,
          implied=True)
        # Value 4: Negative
        meas_meas_add(
          x=-4    , dx=None           , xu=Unit(), 
          y=-3    , dy=1              , yu=Unit(),
          u=None  , du=Decimal("0.5") , mu=None,
          v=None  , dv=None           , mv=None,
          implied=True)
        # Value 5: Zero
        if(True):
          # Value 1: Int
          meas_meas_add(
            x=4     , dx=None           , xu=Unit(), 
            y=0     , dy=1              , yu=Unit(), 
            u=None  , du=Decimal("0.5") , mu=None,
            v=None  , dv=None           , mv=None,
            implied=True)
          # Value 2: Float
          meas_meas_add(
            x=0.4   , dx=None           , xu=Unit(), 
            y=0.0   , dy=0.1            , yu=Unit(), 
            u=None  , du=0.05           , mu=None,
            v=None  , dv=None           , mv=None,
            implied=True)
          # Value 3: Decimal
          meas_meas_add(
            x=Decimal("40") , dx=None           , xu=Unit(), 
            y=Decimal("0")  , dy=Decimal("10")  , yu=Unit(), 
            u=None          , du=Decimal("5")   , mu=None,
            v=None          , dv=None           , mv=None,
            implied=True)
        # Preserve Inputs
        if(True):
          a = Measure(value=4,error=None) 
          b = Measure(value=3,error=2)
          c = a+b
          c = None
          assert a == Measure(value=4,error=None) 
          assert b == Measure(value=3,error=2)
      # Unitless + Unit
      if(True):
        # Normal Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=4,error=None,unit=Unit()) + Measure(value=3,error=1,unit=Unit("cm"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.4,error=None,unit=Unit()) + Measure(value=0.3,error=0.1,unit=Unit("cm"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("40"),error=None,unit=Unit()) + Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-4,error=None,unit=Unit()) + Measure(value=-3,error=1,unit=Unit("cm"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=None,unit=Unit()) + Measure(value=0,error=1,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=3,error=1,unit=Unit("cm"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=None,unit=Unit()) + Measure(value=0,error=0.1,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=0.3,error=0.1,unit=Unit("cm"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=None,unit=Unit()) + Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) + Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=None,unit=Unit()) + Measure(value=0,error=1,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=-3,error=1,unit=Unit("cm"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=3,error=1,unit=Unit("cm"))
            meas_meas_add(
              x=4     , dx=None           , xu=Unit(), 
              y=0     , dy=0              , yu=Unit("cm"), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=True)
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=0.3,error=0.1,unit=Unit("cm"))
            meas_meas_add(
              x=0.4   , dx=None           , xu=Unit(), 
              y=0     , dy=0              , yu=Unit("cm"), 
              u=None  , du=0.05           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=True)
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) + Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm"))
            meas_meas_add(
              x=Decimal("40") , dx=None           , xu=Unit(), 
              y=Decimal("0")  , dy=Decimal("0")   , yu=Unit("cm"), 
              u=None          , du=Decimal("5")   , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit(),
              implied=True)
        # Magnitude Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=4,error=None,unit=Unit()) + Measure(value=3,error=1,unit=Unit("5 m^2"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.4,error=None,unit=Unit()) + Measure(value=0.3,error=0.1,unit=Unit("5 m^2"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("40"),error=None,unit=Unit()) + Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-4,error=None,unit=Unit()) + Measure(value=-3,error=1,unit=Unit("5 m^2"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=None,unit=Unit()) + Measure(value=0,error=1,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=3,error=1,unit=Unit("5 m^2"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=None,unit=Unit()) + Measure(value=0,error=0.1,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=0.3,error=0.1,unit=Unit("5 m^2"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=None,unit=Unit()) + Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) + Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=None,unit=Unit()) + Measure(value=0,error=1,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=-3,error=1,unit=Unit("5 m^2"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=3,error=1,unit=Unit("5 m^2"))
            meas_meas_add(
              x=4     , dx=None           , xu=Unit(), 
              y=0     , dy=0              , yu=Unit("5 m^2"), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=True)
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=0.3,error=0.1,unit=Unit("5 m^2"))
            meas_meas_add(
              x=0.4   , dx=None           , xu=Unit(), 
              y=0     , dy=0              , yu=Unit("5 m^2"), 
              u=None  , du=0.05           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=True)
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) + Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("5 m^2"))
            meas_meas_add(
              x=Decimal("40") , dx=None           , xu=Unit(), 
              y=Decimal("0")  , dy=Decimal("0")   , yu=Unit("5 m^2"), 
              u=None          , du=Decimal("5")   , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit(),
              implied=True)
        # Convoluted Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=300,error=None,unit=Unit()) + Measure(value=27,error=1,unit=Unit("\u00B0C"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=299.9,error=None,unit=Unit()) + Measure(value=26.85,error=0.01,unit=Unit("\u00B0C"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("300"),error=None,unit=Unit()) + Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=300,error=None,unit=Unit()) + Measure(value=-27,error=1,unit=Unit("\u00B0C"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300,error=None,unit=Unit()) + Measure(value=0,error=1,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=27,error=1,unit=Unit("\u00B0C"))
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300.0,error=None,unit=Unit()) + Measure(value=0.0,error=0.01,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit()) + Measure(value=26.85,error=0.01,unit=Unit("\u00B0C"))
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("300"),error=None,unit=Unit()) + Measure(value=Decimal("0"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) + Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300,error=None,unit=Unit()) + Measure(value=0,error=0,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=27,error=1,unit=Unit("\u00B0C"))
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300.0,error=0.02,unit=Unit()) + Measure(value=0.0,error=0.0,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit()) + Measure(value=26.85,error=0.01,unit=Unit("\u00B0C"))
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit()) + Measure(value=Decimal("0"),error=Decimal("0"),unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) + Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
      # Unit + Unitless
      if(True):
        # Normal Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=3,error=None,unit=Unit("cm")) + Measure(value=4,error=2,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.3,error=None,unit=Unit("cm")) + Measure(value=0.4,error=0.2,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("30"),error=None,unit=Unit("cm")) + Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-3,error=None,unit=Unit("cm")) + Measure(value=-4,error=2,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("cm")) + Measure(value=4,error=2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=None,unit=Unit("cm")) + Measure(value=0,error=2,unit=Unit())
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("cm")) + Measure(value=0.4,error=0.2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=None,unit=Unit("cm")) + Measure(value=0,error=0.2,unit=Unit())
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("cm")) + Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=None,unit=Unit("cm")) + Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit())
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("cm")) + Measure(value=-4,error=2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-3,error=None,unit=Unit("cm")) + Measure(value=0,error=2,unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            meas_meas_add(
              x=3     , dx=None           , xu=Unit("cm"), 
              y=0     , dy=0              , yu=Unit(), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("cm"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("cm")) + Measure(value=4,error=2,unit=Unit())
            # Value 2: Float
            meas_meas_add(
              x=0.3   , dx=None           , xu=Unit("cm"), 
              y=0     , dy=0              , yu=Unit(), 
              u=None  , du=0.05           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("cm"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("cm")) + Measure(value=0.4,error=0.2,unit=Unit())
            # Value 3: Decimal
            meas_meas_add(
              x=Decimal("30") , dx=None           , xu=Unit("cm"), 
              y=Decimal("0")  , dy=Decimal("0")   , yu=Unit(), 
              u=None          , du=Decimal("5")   , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("cm"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("cm")) + Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit())
        # Magnitude Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=3,error=None,unit=Unit("5 m^2")) + Measure(value=4,error=2,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.3,error=None,unit=Unit("5 m^2")) + Measure(value=0.4,error=0.2,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2")) + Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-3,error=None,unit=Unit("5 m^2")) + Measure(value=-4,error=2,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("5 m^2")) + Measure(value=4,error=2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=None,unit=Unit("5 m^2")) + Measure(value=0,error=2,unit=Unit())
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("5 m^2")) + Measure(value=0.4,error=0.2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=None,unit=Unit("5 m^2")) + Measure(value=0,error=0.2,unit=Unit())
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2")) + Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2")) + Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit())
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("5 m^2")) + Measure(value=-4,error=2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-3,error=None,unit=Unit("5 m^2")) + Measure(value=0,error=2,unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            meas_meas_add(
              x=3     , dx=None           , xu=Unit("5 m^2"), 
              y=0     , dy=0              , yu=Unit(), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("5 m^2"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("5 m^2")) + Measure(value=4,error=2,unit=Unit())
            # Value 2: Float
            meas_meas_add(
              x=0.3   , dx=None           , xu=Unit("5 m^2"), 
              y=0     , dy=0              , yu=Unit(), 
              u=None  , du=0.05           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("5 m^2"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit("5 m^2")) + Measure(value=0.4,error=0.2,unit=Unit())
            # Value 3: Decimal
            meas_meas_add(
              x=Decimal("30") , dx=None           , xu=Unit("5 m^2"), 
              y=Decimal("0")  , dy=Decimal("0")   , yu=Unit(), 
              u=None          , du=Decimal("5")   , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("5 m^2"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2")) + Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit())
        # Convoluted Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=27,error=None,unit=Unit("\u00B0C")) + Measure(value=300,error=2,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=26.85,error=None,unit=Unit("\u00B0C")) + Measure(value=299.9,error=0.02,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C")) + Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-27,error=None,unit=Unit("\u00B0C")) + Measure(value=300,error=2,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("\u00B0C")) + Measure(value=300,error=2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=27,error=None,unit=Unit("\u00B0C")) + Measure(value=0,error=2,unit=Unit())
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit("\u00B0C")) + Measure(value=300.0,error=0.02,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=26.85,error=None,unit=Unit("\u00B0C")) + Measure(value=0.0,error=0.02,unit=Unit())
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C")) + Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C")) + Measure(value=Decimal("0"),error=Decimal("0.02"),unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("\u00B0C")) + Measure(value=300,error=2,unit=Unit())
            meas_meas_add(
              x=27            , dx=None           , xu=Unit("\u00B0C"), 
              y=0             , dy=0              , yu=Unit(), 
              u=None          , du=Decimal("0.5") , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("\u00B0C"),
              implied=True)
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit("\u00B0C")) + Measure(value=300.0,error=0.02,unit=Unit())
            meas_meas_add(
              x=26.85         , dx=None           , xu=Unit("\u00B0C"), 
              y=0             , dy=0              , yu=Unit(), 
              u=None          , du=0.005          , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("\u00B0C"),
              implied=True)
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C")) + Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit())
            meas_meas_add(
              x=Decimal("26.85")  , dx=None             , xu=Unit("\u00B0C"), 
              y=Decimal("0")      , dy=Decimal("0")     , yu=Unit(), 
              u=None              , du=Decimal("0.005") , mu=None,
              v=None              , dv=None             , mv=None,
              unit=Unit("\u00B0C"), 
              implied=True)
      # Unit + Unit
      if(True):
        # Same Units
        if(True):
          # Normal Units
          if(True):
            # Value 1: Int
            meas_meas_add(
              x=4     , dx=None           , xu=Unit("cm"), 
              y=3     , dy=1              , yu=Unit("cm"), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=None           , mv=None,
              implied=True)
            # Value 2: Float
            meas_meas_add(
              x=0.4   , dx=None           , xu=Unit("cm"), 
              y=0.3   , dy=0.1            , yu=Unit("cm"), 
              u=None  , du=0.05           , mu=None,
              v=None  , dv=None           , mv=None,
              implied=True)
            # Value 3: Decimal
            meas_meas_add(
              x=Decimal("40") , dx=None           , xu=Unit("cm"), 
              y=Decimal("30") , dy=Decimal("10")  , yu=Unit("cm"), 
              u=None          , du=Decimal("5")   , mu=None,
              v=None          , dv=None           , mv=None,
              implied=True)
            # Value 4: Negative
            meas_meas_add(
              x=-4    , dx=None           , xu=Unit("cm"), 
              y=-3    , dy=1              , yu=Unit("cm"), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=None           , mv=None,
              implied=True)
            # Value 5: Zero
            if(True):
              # Value 1: Int
              meas_meas_add(
                x=0     , dx=None           , xu=Unit("cm"), 
                y=3     , dy=1              , yu=Unit("cm"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
              meas_meas_add(
                x=4     , dx=None           , xu=Unit("cm"), 
                y=0     , dy=1              , yu=Unit("cm"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
              # Value 2: Float
              meas_meas_add(
                x=0.0   , dx=None           , xu=Unit("cm"), 
                y=0.3   , dy=0.1            , yu=Unit("cm"), 
                u=None  , du=0.05           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
              meas_meas_add(
                x=0.4   , dx=None           , xu=Unit("cm"), 
                y=0.0   , dy=0.1            , yu=Unit("cm"), 
                u=None  , du=0.05           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
              # Value 3: Decimal
              meas_meas_add(
                x=Decimal("0")  , dx=None           , xu=Unit("cm"), 
                y=Decimal("30") , dy=Decimal("10")  , yu=Unit("cm"), 
                u=None          , du=Decimal("0.5") , mu=None,
                v=None          , dv=None           , mv=None,
                implied=True)
              meas_meas_add(
                x=Decimal("40") , dx=None           , xu=Unit("cm"), 
                y=Decimal("0")  , dy=Decimal("10")  , yu=Unit("cm"), 
                u=None          , du=Decimal("5")   , mu=None,
                v=None          , dv=None           , mv=None,
                implied=True)
              # Value 4: Negative
              meas_meas_add(
                x=0     , dx=None           , xu=Unit("cm"), 
                y=-3    , dy=1              , yu=Unit("cm"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
              meas_meas_add(
                x=-4    , dx=None           , xu=Unit("cm"), 
                y=0     , dy=1              , yu=Unit("cm"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
          # Magnitude Units
          if(True):
            # Value 1: Int
            meas_meas_add(
              x=4     , dx=None           , xu=Unit("5 m^2"), 
              y=3     , dy=1              , yu=Unit("5 m^2"), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=None           , mv=None,
              implied=True)
            # Value 2: Float
            meas_meas_add(
              x=0.4   , dx=None           , xu=Unit("5 m^2"), 
              y=0.3   , dy=0.1            , yu=Unit("5 m^2"), 
              u=None  , du=0.05           , mu=None,
              v=None  , dv=None           , mv=None,
              implied=True)
            # Value 3: Decimal
            meas_meas_add(
              x=Decimal("40") , dx=None           , xu=Unit("5 m^2"), 
              y=Decimal("30") , dy=Decimal("10")  , yu=Unit("5 m^2"), 
              u=None          , du=Decimal("5")   , mu=None,
              v=None          , dv=None           , mv=None,
              implied=True)
            # Value 4: Negative
            meas_meas_add(
              x=-4    , dx=None           , xu=Unit("5 m^2"), 
              y=-3    , dy=1              , yu=Unit("5 m^2"), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=None           , mv=None,
              implied=True)
            # Value 5: Zero
            if(True):
              # Value 1: Int
              meas_meas_add(
                x=0     , dx=None           , xu=Unit("5 m^2"), 
                y=3     , dy=1              , yu=Unit("5 m^2"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
              meas_meas_add(
                x=4     , dx=None           , xu=Unit("5 m^2"), 
                y=0     , dy=1              , yu=Unit("5 m^2"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
              # Value 2: Float
              meas_meas_add(
                x=0.0   , dx=None           , xu=Unit("5 m^2"), 
                y=0.3   , dy=0.1            , yu=Unit("5 m^2"), 
                u=None  , du=0.05           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
              meas_meas_add(
                x=0.4   , dx=None           , xu=Unit("5 m^2"), 
                y=0.0   , dy=0.1            , yu=Unit("5 m^2"), 
                u=None  , du=0.05           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
              # Value 3: Decimal
              meas_meas_add(
                x=Decimal("0")  , dx=None           , xu=Unit("5 m^2"), 
                y=Decimal("30") , dy=Decimal("10")  , yu=Unit("5 m^2"), 
                u=None          , du=Decimal("0.5") , mu=None,
                v=None          , dv=None           , mv=None,
                implied=True)
              meas_meas_add(
                x=Decimal("40") , dx=None           , xu=Unit("5 m^2"), 
                y=Decimal("0")  , dy=Decimal("10")  , yu=Unit("5 m^2"), 
                u=None          , du=Decimal("5")   , mu=None,
                v=None          , dv=None           , mv=None,
                implied=True)
              # Value 4: Negative
              meas_meas_add(
                x=0     , dx=None           , xu=Unit("5 m^2"), 
                y=-3    , dy=1              , yu=Unit("5 m^2"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
              meas_meas_add(
                x=-4    , dx=None           , xu=Unit("5 m^2"), 
                y=0     , dy=1              , yu=Unit("5 m^2"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
          # Convoluted Units
          if(True):
            # Value 1: Int
            meas_meas_add(
              x=26                , dx=None           , xu=Unit("\u00B0C"), 
              y=27                , dy=1              , yu=Unit("\u00B0C"), 
              u=Decimal("299.85") , du=Decimal("0.5") , mu=None,
              v=Decimal("300.15") , dv=None           , mv=None,
              value = Decimal("299.85") + Decimal("300.15") - Decimal("273.85"),
              implied=True)
            # Value 2: Float
            meas_meas_add(
              x=26.85 , dx=None   , xu=Unit("\u00B0C"), 
              y=26.85 , dy=0.01   , yu=Unit("\u00B0C"), 
              u=300.0 , du=0.005  , mu=None,
              v=300.0 , dv=None   , mv=None,
              value = 300.0 + 300.0 - 273.15,
              implied=True)
            # Value 3: Decimal
            meas_meas_add(
              x=Decimal("26.85")  , dx=None             , xu=Unit("\u00B0C"), 
              y=Decimal("26.85")  , dy=Decimal("0.01")  , yu=Unit("\u00B0C"), 
              u=Decimal("300")    , du=Decimal("0.005") , mu=None,
              v=Decimal("300")    , dv=None             , mv=None,
              value = Decimal("300") + Decimal("300") - Decimal("273.15"),
              implied=True)
            # Value 4: Negative
            meas_meas_add(
              x=-31               , dx=None           , xu=Unit("\u00B0C"), 
              y=-27               , dy=1              , yu=Unit("\u00B0C"), 
              u=Decimal("242.15") , du=Decimal("0.5") , mu=None,
              v=Decimal("246.15") , dv=None           , mv=None,
              value = Decimal("242.15") + Decimal("246.15") - Decimal("273.15"),
              implied=True)
            # Value 5: Zero
            if(True):
              # Int
              meas_meas_add(
                x=27                , dx=None           , xu=Unit("\u00B0C"), 
                y=0                 , dy=1              , yu=Unit("\u00B0C"), 
                u=Decimal("300.15") , du=Decimal("0.5") , mu=None,
                v=Decimal("273.15") , dv=None           , mv=None,
                value = Decimal("300.15") + Decimal("273.15") - Decimal("273.15"),
                implied=True)
              # Float
              meas_meas_add(
                x=26.85   , dx=None   , xu=Unit("\u00B0C"), 
                y=0.0     , dy=0.01   , yu=Unit("\u00B0C"), 
                u=300.0   , du=0.005  , mu=None,
                v=273.15  , dv=None   , mv=None,
                value = 300.0+273.15-273.15,
                implied=True)
              # Decimal
              meas_meas_add(
                x=Decimal("26.85")  , dx=None             , xu=Unit("\u00B0C"), 
                y=Decimal("0")      , dy=Decimal("0.01")  , yu=Unit("\u00B0C"), 
                u=Decimal("300")    , du=Decimal("0.005") , mu=None,
                v=Decimal("273.15") , dv=None             , mv=None,
                value = Decimal("300") + Decimal("273.15") - Decimal("273.15"),
                implied=True)
        # Different Units
        if(True):
          # Normal Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=None,unit=Unit("s")) + Measure(value=3,error=1,unit=Unit("cm"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=None,unit=Unit("s")) + Measure(value=0.3,error=0.1,unit=Unit("cm"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=None,unit=Unit("s")) + Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=None,unit=Unit("s")) + Measure(value=-3,error=1,unit=Unit("cm"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=None,unit=Unit("s")) + Measure(value=0,error=1,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("s")) + Measure(value=3,error=1,unit=Unit("cm"))
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=None,unit=Unit("s")) + Measure(value=0,error=0.1,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("s")) + Measure(value=0.3,error=0.1,unit=Unit("cm"))
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=None,unit=Unit("s")) + Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("s")) + Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm"))
              # Value 4: Negative
              with pytest.raises(IncompatibleUnitException):
                Measure(value=-4,error=None,unit=Unit("s")) + Measure(value=0,error=1,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("s")) + Measure(value=-3,error=1,unit=Unit("cm"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("s")) + Measure(value=3,error=1,unit=Unit("cm"))
              meas_meas_add(
                x=4     , dx=None           , xu=Unit("s"), 
                y=0     , dy=0              , yu=Unit("cm"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("s"),
                implied=True)
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("s")) + Measure(value=0.3,error=0.1,unit=Unit("cm"))
              meas_meas_add(
                x=0.4   , dx=None           , xu=Unit("s"), 
                y=0     , dy=0              , yu=Unit("cm"), 
                u=None  , du=0.05           , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("s"),
                implied=True)
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("s")) + Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm"))
              meas_meas_add(
                x=Decimal("40") , dx=None           , xu=Unit("s"), 
                y=Decimal("0")  , dy=Decimal("0")   , yu=Unit("cm"), 
                u=None          , du=Decimal("5")   , mu=None,
                v=None          , dv=None           , mv=None,
                unit=Unit("s"),
                implied=True)
          # Magnitude Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=None,unit=Unit("5 s")) + Measure(value=3,error=1,unit=Unit("5 m^2"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=None,unit=Unit("5 s")) + Measure(value=0.3,error=0.1,unit=Unit("5 m^2"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=None,unit=Unit("5 s")) + Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=None,unit=Unit("5 s")) + Measure(value=-3,error=1,unit=Unit("5 m^2"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=None,unit=Unit("5 s")) + Measure(value=0,error=1,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("5 s")) + Measure(value=3,error=1,unit=Unit("5 m^2"))
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=None,unit=Unit("5 s")) + Measure(value=0,error=0.1,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("5 s")) + Measure(value=0.3,error=0.1,unit=Unit("5 m^2"))
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=None,unit=Unit("5 s")) + Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("5 s")) + Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2"))
              # Value 4: Negative
              with pytest.raises(IncompatibleUnitException):
                Measure(value=-4,error=None,unit=Unit("5 s")) + Measure(value=0,error=1,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("5 s")) + Measure(value=-3,error=1,unit=Unit("5 m^2"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("5 s")) + Measure(value=3,error=1,unit=Unit("5 m^2"))
              meas_meas_add(
                x=4     , dx=None           , xu=Unit("5 s"), 
                y=0     , dy=0              , yu=Unit("5 m^2"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("5 s"),
                implied=True)
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=None,unit=Unit("5 s")) + Measure(value=0.3,error=0.1,unit=Unit("5 m^2"))
              meas_meas_add(
                x=0.4   , dx=None           , xu=Unit("5 s"), 
                y=0     , dy=0              , yu=Unit("5 m^2"), 
                u=None  , du=0.05           , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("5 s"),
                implied=True)
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("5 s")) + Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2"))
              meas_meas_add(
                x=Decimal("40") , dx=None           , xu=Unit("5 s"), 
                y=Decimal("0")  , dy=Decimal("0")   , yu=Unit("5 m^2"), 
                u=None          , du=Decimal("5")   , mu=None,
                v=None          , dv=None           , mv=None,
                unit=Unit("5 s"),
                implied=True)
          # Convoluted Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=27,error=1,unit=Unit("\u00B0C"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=2.9,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=26.85,error=0.01,unit=Unit("\u00B0C"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("3"),error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=-27,error=1,unit=Unit("\u00B0C"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=3,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=0,error=1,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=27,error=1,unit=Unit("\u00B0C"))
              # Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=3.0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=0.0,error=0.01,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=26.85,error=0.01,unit=Unit("\u00B0C"))
              # Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("3"),error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=Decimal("0"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=0,error=0,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("\u00B0C")) + Measure(value=0,error=0,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
              # Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=0.0,error=0.0,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=None,unit=Unit("\u00B0C")) + Measure(value=0.0,error=0.0,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
              # Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=Decimal("0"),error=Decimal("0"),unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C")) + Measure(value=Decimal("0"),error=Decimal("0.0"),unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
    # Measure (Implicit Error) + Measure (Implicit Error) = Measure (Implicit Error)
    if(True):
      # Unitless + Unitless
      if(True):
        # Value 1: Int
        meas_meas_add(
          x=4     , dx=None           , xu=Unit(), 
          y=3     , dy=None           , yu=Unit(), 
          u=None  , du=Decimal("0.5") , mu=None,
          v=None  , dv=Decimal("0.5") , mv=None,
          implied=True)
        # Value 2: Float
        meas_meas_add(
          x=0.4   , dx=None           , xu=Unit(), 
          y=0.3   , dy=None           , yu=Unit(), 
          u=None  , du=0.05           , mu=None,
          v=None  , dv=0.05           , mv=None,
          implied=True)
        # Value 3: Decimal
        meas_meas_add(
          x=Decimal("40") , dx=None           , xu=Unit(), 
          y=Decimal("30") , dy=None           , yu=Unit(), 
          u=None          , du=Decimal("5")   , mu=None,
          v=None          , dv=Decimal("5")   , mv=None,
          implied=True)
        # Value 4: Negative
        meas_meas_add(
          x=-4    , dx=None           , xu=Unit(), 
          y=-3    , dy=None           , yu=Unit(),
          u=None  , du=Decimal("0.5") , mu=None,
          v=None  , dv=Decimal("0.5") , mv=None,
          implied=True)
        # Value 5: Zero
        if(True):
          # Value 1: Int
          meas_meas_add(
            x=4     , dx=None           , xu=Unit(), 
            y=0     , dy=None           , yu=Unit(), 
            u=None  , du=Decimal("0.5") , mu=None,
            v=None  , dv=Decimal("0.5") , mv=None,
            implied=True)
          # Value 2: Float
          meas_meas_add(
            x=0.4   , dx=None           , xu=Unit(), 
            y=0.0   , dy=None           , yu=Unit(), 
            u=None  , du=0.05           , mu=None,
            v=None  , dv=0.05           , mv=None,
            implied=True)
          # Value 3: Decimal
          meas_meas_add(
            x=Decimal("40") , dx=None           , xu=Unit(), 
            y=Decimal("0")  , dy=None           , yu=Unit(), 
            u=None          , du=Decimal("5")   , mu=None,
            v=None          , dv=Decimal("0.5") , mv=None,
            implied=True)
        # Preserve Inputs
        if(True):
          a = Measure(value=4,error=None) 
          b = Measure(value=3,error=None)
          c = a+b
          c = None
          assert a == Measure(value=4,error=None) 
          assert b == Measure(value=3,error=None)
      # Unitless + Unit
      if(True):
        # Normal Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=4,error=None,unit=Unit()) + Measure(value=3,error=None,unit=Unit("cm"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.4,error=None,unit=Unit()) + Measure(value=0.3,error=None,unit=Unit("cm"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("40"),error=None,unit=Unit()) + Measure(value=Decimal("30"),error=None,unit=Unit("cm"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-4,error=None,unit=Unit()) + Measure(value=-3,error=None,unit=Unit("cm"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=None,unit=Unit()) + Measure(value=0,error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=3,error=None,unit=Unit("cm"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=None,unit=Unit()) + Measure(value=0,error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=0.3,error=None,unit=Unit("cm"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=None,unit=Unit()) + Measure(value=Decimal("0"),error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) + Measure(value=Decimal("30"),error=None,unit=Unit("cm"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=None,unit=Unit()) + Measure(value=0,error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=-3,error=None,unit=Unit("cm"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=3,error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=None,unit=Unit()) + Measure(value=0,error=None,unit=Unit("cm"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=0.3,error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=None,unit=Unit()) + Measure(value=0.0,error=None,unit=Unit("cm"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) + Measure(value=Decimal("30"),error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=None,unit=Unit()) + Measure(value=Decimal("0"),error=None,unit=Unit("cm"))
        # Magnitude Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=4,error=None,unit=Unit()) + Measure(value=3,error=None,unit=Unit("5 m^2"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.4,error=None,unit=Unit()) + Measure(value=0.3,error=None,unit=Unit("5 m^2"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("40"),error=None,unit=Unit()) + Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-4,error=None,unit=Unit()) + Measure(value=-3,error=None,unit=Unit("5 m^2"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=None,unit=Unit()) + Measure(value=0,error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=3,error=None,unit=Unit("5 m^2"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=None,unit=Unit()) + Measure(value=0,error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=0.3,error=None,unit=Unit("5 m^2"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=None,unit=Unit()) + Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) + Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=None,unit=Unit()) + Measure(value=0,error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=-3,error=None,unit=Unit("5 m^2"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=3,error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=None,unit=Unit()) + Measure(value=0,error=None,unit=Unit("5 m^2"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=0.3,error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=None,unit=Unit()) + Measure(value=0.0,error=None,unit=Unit("5 m^2"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) + Measure(value=Decimal("40"),error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=None,unit=Unit()) + Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2"))
        # Convoluted Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=300,error=None,unit=Unit()) + Measure(value=27,error=None,unit=Unit("\u00B0C"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=299.9,error=None,unit=Unit()) + Measure(value=26.85,error=None,unit=Unit("\u00B0C"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("300"),error=None,unit=Unit()) + Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=300,error=None,unit=Unit()) + Measure(value=-27,error=None,unit=Unit("\u00B0C"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300,error=None,unit=Unit()) + Measure(value=0,error=None,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=27,error=None,unit=Unit("\u00B0C"))
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300.0,error=None,unit=Unit()) + Measure(value=0.0,error=None,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit()) + Measure(value=26.85,error=None,unit=Unit("\u00B0C"))
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("300"),error=None,unit=Unit()) + Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) + Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300,error=None,unit=Unit()) + Measure(value=0,error=None,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) + Measure(value=27,error=None,unit=Unit("\u00B0C"))
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300.0,error=0.02,unit=Unit()) + Measure(value=0.0,error=None,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit()) + Measure(value=26.85,error=None,unit=Unit("\u00B0C"))
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit()) + Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) + Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C"))
      # Unit + Unitless
      if(True):
        # Normal Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=3,error=None,unit=Unit("cm")) + Measure(value=4,error=None,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.3,error=None,unit=Unit("cm")) + Measure(value=0.4,error=None,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("30"),error=None,unit=Unit("cm")) + Measure(value=Decimal("40"),error=None,unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-3,error=None,unit=Unit("cm")) + Measure(value=-4,error=None,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("cm")) + Measure(value=4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=None,unit=Unit("cm")) + Measure(value=0,error=None,unit=Unit())
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("cm")) + Measure(value=0.4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=None,unit=Unit("cm")) + Measure(value=0,error=None,unit=Unit())
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("cm")) + Measure(value=Decimal("40"),error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=None,unit=Unit("cm")) + Measure(value=Decimal("0"),error=None,unit=Unit())
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("cm")) + Measure(value=-4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-3,error=None,unit=Unit("cm")) + Measure(value=0,error=None,unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=None,unit=Unit("cm")) + Measure(value=0,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("cm")) + Measure(value=4,error=None,unit=Unit())
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=None,unit=Unit("cm")) + Measure(value=0.0,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit("cm")) + Measure(value=0.4,error=None,unit=Unit())
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=None,unit=Unit("cm")) + Measure(value=Decimal("0"),error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("cm")) + Measure(value=Decimal("40"),error=None,unit=Unit())
        # Magnitude Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=3,error=None,unit=Unit("5 m^2")) + Measure(value=4,error=None,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.3,error=None,unit=Unit("5 m^2")) + Measure(value=0.4,error=None,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2")) + Measure(value=Decimal("40"),error=None,unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-3,error=None,unit=Unit("5 m^2")) + Measure(value=-4,error=None,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("5 m^2")) + Measure(value=4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=None,unit=Unit("5 m^2")) + Measure(value=0,error=None,unit=Unit())
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("5 m^2")) + Measure(value=0.4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=None,unit=Unit("5 m^2")) + Measure(value=0,error=None,unit=Unit())
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2")) + Measure(value=Decimal("40"),error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2")) + Measure(value=Decimal("0"),error=None,unit=Unit())
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("5 m^2")) + Measure(value=-4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-3,error=None,unit=Unit("5 m^2")) + Measure(value=0,error=None,unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=None,unit=Unit("5 m^2")) + Measure(value=0,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("5 m^2")) + Measure(value=4,error=None,unit=Unit())
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=None,unit=Unit("5 m^2")) + Measure(value=0.0,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit("5 m^2")) + Measure(value=0.4,error=None,unit=Unit())
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2")) + Measure(value=Decimal("0"),error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2")) + Measure(value=Decimal("40"),error=None,unit=Unit())
        # Convoluted Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=27,error=None,unit=Unit("\u00B0C")) + Measure(value=300,error=None,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=26.85,error=None,unit=Unit("\u00B0C")) + Measure(value=299.9,error=None,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C")) + Measure(value=Decimal("300"),error=None,unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-27,error=None,unit=Unit("\u00B0C")) + Measure(value=300,error=None,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("\u00B0C")) + Measure(value=300,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=27,error=None,unit=Unit("\u00B0C")) + Measure(value=0,error=None,unit=Unit())
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit("\u00B0C")) + Measure(value=300.0,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=26.85,error=None,unit=Unit("\u00B0C")) + Measure(value=0.0,error=None,unit=Unit())
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C")) + Measure(value=Decimal("300"),error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C")) + Measure(value=Decimal("0"),error=None,unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("\u00B0C")) + Measure(value=300,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=27,error=None,unit=Unit("\u00B0C")) + Measure(value=0,error=None,unit=Unit())
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit("\u00B0C")) + Measure(value=300.0,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=26.85,error=None,unit=Unit("\u00B0C")) + Measure(value=0.0,error=None,unit=Unit())
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C")) + Measure(value=Decimal("300"),error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C")) + Measure(value=Decimal("0"),error=None,unit=Unit())
      # Unit + Unit
      if(True):
        # Same Units
        if(True):
          # Normal Units
          if(True):
            # Value 1: Int
            meas_meas_add(
              x=4     , dx=None           , xu=Unit("cm"), 
              y=3     , dy=None           , yu=Unit("cm"), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              implied=True)
            # Value 2: Float
            meas_meas_add(
              x=0.4   , dx=None           , xu=Unit("cm"), 
              y=0.3   , dy=None           , yu=Unit("cm"), 
              u=None  , du=0.05           , mu=None,
              v=None  , dv=0.05           , mv=None,
              implied=True)
            # Value 3: Decimal
            meas_meas_add(
              x=Decimal("40") , dx=None           , xu=Unit("cm"), 
              y=Decimal("30") , dy=None           , yu=Unit("cm"), 
              u=None          , du=Decimal("5")   , mu=None,
              v=None          , dv=Decimal("5")   , mv=None,
              implied=True)
            # Value 4: Negative
            meas_meas_add(
              x=-4    , dx=None           , xu=Unit("cm"), 
              y=-3    , dy=None           , yu=Unit("cm"), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              implied=True)
            # Value 5: Zero
            if(True):
              # Value 1: Int
              meas_meas_add(
                x=0     , dx=None           , xu=Unit("cm"), 
                y=3     , dy=None           , yu=Unit("cm"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              meas_meas_add(
                x=4     , dx=None           , xu=Unit("cm"), 
                y=0     , dy=None           , yu=Unit("cm"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              # Value 2: Float
              meas_meas_add(
                x=0.0   , dx=None           , xu=Unit("cm"), 
                y=0.3   , dy=None           , yu=Unit("cm"), 
                u=None  , du=0.05           , mu=None,
                v=None  , dv=0.05           , mv=None,
                implied=True)
              meas_meas_add(
                x=0.4   , dx=None           , xu=Unit("cm"), 
                y=0.0   , dy=None           , yu=Unit("cm"), 
                u=None  , du=0.05           , mu=None,
                v=None  , dv=0.05           , mv=None,
                implied=True)
              # Value 3: Decimal
              meas_meas_add(
                x=Decimal("0")  , dx=None           , xu=Unit("cm"), 
                y=Decimal("30") , dy=None           , yu=Unit("cm"), 
                u=None          , du=Decimal("0.5") , mu=None,
                v=None          , dv=Decimal("5")   , mv=None,
                implied=True)
              meas_meas_add(
                x=Decimal("40") , dx=None           , xu=Unit("cm"), 
                y=Decimal("0")  , dy=None           , yu=Unit("cm"), 
                u=None          , du=Decimal("5")   , mu=None,
                v=None          , dv=Decimal("0.5") , mv=None,
                implied=True)
              # Value 4: Negative
              meas_meas_add(
                x=0     , dx=None           , xu=Unit("cm"), 
                y=-3    , dy=None           , yu=Unit("cm"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              meas_meas_add(
                x=-4    , dx=None           , xu=Unit("cm"), 
                y=0     , dy=None           , yu=Unit("cm"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
          # Magnitude Units
          if(True):
            # Value 1: Int
            meas_meas_add(
              x=4     , dx=None           , xu=Unit("5 m^2"), 
              y=3     , dy=None           , yu=Unit("5 m^2"), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              implied=True)
            # Value 2: Float
            meas_meas_add(
              x=0.4   , dx=None           , xu=Unit("5 m^2"), 
              y=0.3   , dy=None           , yu=Unit("5 m^2"), 
              u=None  , du=0.05           , mu=None,
              v=None  , dv=0.05           , mv=None,
              implied=True)
            # Value 3: Decimal
            meas_meas_add(
              x=Decimal("40") , dx=None           , xu=Unit("5 m^2"), 
              y=Decimal("30") , dy=None           , yu=Unit("5 m^2"), 
              u=None          , du=Decimal("5")   , mu=None,
              v=None          , dv=Decimal("5")   , mv=None,
              implied=True)
            # Value 4: Negative
            meas_meas_add(
              x=-4    , dx=None           , xu=Unit("5 m^2"), 
              y=-3    , dy=None           , yu=Unit("5 m^2"), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              implied=True)
            # Value 5: Zero
            if(True):
              # Value 1: Int
              meas_meas_add(
                x=0     , dx=None           , xu=Unit("5 m^2"), 
                y=3     , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              meas_meas_add(
                x=4     , dx=None           , xu=Unit("5 m^2"), 
                y=0     , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              # Value 2: Float
              meas_meas_add(
                x=0.0   , dx=None           , xu=Unit("5 m^2"), 
                y=0.3   , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=0.05           , mu=None,
                v=None  , dv=0.05           , mv=None,
                implied=True)
              meas_meas_add(
                x=0.4   , dx=None           , xu=Unit("5 m^2"), 
                y=0.0   , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=0.05           , mu=None,
                v=None  , dv=0.05           , mv=None,
                implied=True)
              # Value 3: Decimal
              meas_meas_add(
                x=Decimal("0")  , dx=None           , xu=Unit("5 m^2"), 
                y=Decimal("30") , dy=None           , yu=Unit("5 m^2"), 
                u=None          , du=Decimal("0.5") , mu=None,
                v=None          , dv=Decimal("5")   , mv=None,
                implied=True)
              meas_meas_add(
                x=Decimal("40") , dx=None           , xu=Unit("5 m^2"), 
                y=Decimal("0")  , dy=None           , yu=Unit("5 m^2"), 
                u=None          , du=Decimal("5")   , mu=None,
                v=None          , dv=Decimal("0.5") , mv=None,
                implied=True)
              # Value 4: Negative
              meas_meas_add(
                x=0     , dx=None           , xu=Unit("5 m^2"), 
                y=-3    , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              meas_meas_add(
                x=-4    , dx=None           , xu=Unit("5 m^2"), 
                y=0     , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
          # Convoluted Units
          if(True):
            # Value 1: Int
            meas_meas_add(
              x=26                , dx=None           , xu=Unit("\u00B0C"), 
              y=27                , dy=None           , yu=Unit("\u00B0C"), 
              u=Decimal("299.85") , du=Decimal("0.5") , mu=None,
              v=Decimal("300.15") , dv=Decimal("0.5") , mv=None,
              value = Decimal("299.85") + Decimal("300.15") - Decimal("273.85"),
              implied=True)
            # Value 2: Float
            meas_meas_add(
              x=26.85 , dx=None   , xu=Unit("\u00B0C"), 
              y=26.85 , dy=None   , yu=Unit("\u00B0C"), 
              u=300.0 , du=0.005  , mu=None,
              v=300.0 , dv=0.005  , mv=None,
              value = 300.0 + 300.0 - 273.15,
              implied=True)
            # Value 3: Decimal
            meas_meas_add(
              x=Decimal("26.85")  , dx=None             , xu=Unit("\u00B0C"), 
              y=Decimal("26.85")  , dy=None             , yu=Unit("\u00B0C"), 
              u=Decimal("300")    , du=Decimal("0.005") , mu=None,
              v=Decimal("300")    , dv=Decimal("0.005") , mv=None,
              value = Decimal("300") + Decimal("300") - Decimal("273.15"),
              implied=True)
            # Value 4: Negative
            meas_meas_add(
              x=-31               , dx=None           , xu=Unit("\u00B0C"), 
              y=-27               , dy=None           , yu=Unit("\u00B0C"), 
              u=Decimal("242.15") , du=Decimal("0.5") , mu=None,
              v=Decimal("246.15") , dv=Decimal("0.5") , mv=None,
              value = Decimal("242.15") + Decimal("246.15") - Decimal("273.15"),
              implied=True)
            # Value 5: Zero
            if(True):
              # Int
              meas_meas_add(
                x=27                , dx=None           , xu=Unit("\u00B0C"), 
                y=0                 , dy=None           , yu=Unit("\u00B0C"), 
                u=Decimal("300.15") , du=Decimal("0.5") , mu=None,
                v=Decimal("273.15") , dv=Decimal("0.5") , mv=None,
                value = Decimal("300.15") + Decimal("273.15") - Decimal("273.15"),
                implied=True)
              # Float
              meas_meas_add(
                x=26.85   , dx=None   , xu=Unit("\u00B0C"), 
                y=0.0     , dy=None   , yu=Unit("\u00B0C"), 
                u=300.0   , du=0.005  , mu=None,
                v=273.15  , dv=0.05   , mv=None,
                value = 300.0+273.15-273.15,
                implied=True)
              # Decimal
              meas_meas_add(
                x=Decimal("26.85")  , dx=None             , xu=Unit("\u00B0C"), 
                y=Decimal("0")      , dy=None             , yu=Unit("\u00B0C"), 
                u=Decimal("300")    , du=Decimal("0.005") , mu=None,
                v=Decimal("273.15") , dv=Decimal("0.5")   , mv=None,
                value = Decimal("300") + Decimal("273.15") - Decimal("273.15"),
                implied=True)
        # Different Units
        if(True):
          # Normal Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=None,unit=Unit("s")) + Measure(value=3,error=None,unit=Unit("cm"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=None,unit=Unit("s")) + Measure(value=0.3,error=None,unit=Unit("cm"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=None,unit=Unit("s")) + Measure(value=Decimal("30"),error=None,unit=Unit("cm"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=None,unit=Unit("s")) + Measure(value=-3,error=None,unit=Unit("cm"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=None,unit=Unit("s")) + Measure(value=0,error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("s")) + Measure(value=3,error=None,unit=Unit("cm"))
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=None,unit=Unit("s")) + Measure(value=0,error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("s")) + Measure(value=0.3,error=None,unit=Unit("cm"))
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=None,unit=Unit("s")) + Measure(value=Decimal("0"),error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("s")) + Measure(value=Decimal("30"),error=None,unit=Unit("cm"))
              # Value 4: Negative
              with pytest.raises(IncompatibleUnitException):
                Measure(value=-4,error=None,unit=Unit("s")) + Measure(value=0,error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("s")) + Measure(value=-3,error=None,unit=Unit("cm"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("s")) + Measure(value=3,error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=None,unit=Unit("s")) + Measure(value=0,error=None,unit=Unit("cm"))
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=None,unit=Unit("s")) + Measure(value=0.3,error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=None,unit=Unit("s")) + Measure(value=0.0,error=None,unit=Unit("cm"))
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("s")) + Measure(value=Decimal("30"),error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=None,unit=Unit("s")) + Measure(value=Decimal("0"),error=None,unit=Unit("cm"))
          # Magnitude Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=None,unit=Unit("5 s")) + Measure(value=3,error=None,unit=Unit("5 m^2"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=None,unit=Unit("5 s")) + Measure(value=0.3,error=None,unit=Unit("5 m^2"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=None,unit=Unit("5 s")) + Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=None,unit=Unit("5 s")) + Measure(value=-3,error=None,unit=Unit("5 m^2"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=None,unit=Unit("5 s")) + Measure(value=0,error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("5 s")) + Measure(value=3,error=None,unit=Unit("5 m^2"))
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=None,unit=Unit("5 s")) + Measure(value=0,error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("5 s")) + Measure(value=0.3,error=None,unit=Unit("5 m^2"))
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=None,unit=Unit("5 s")) + Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("5 s")) + Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2"))
              # Value 4: Negative
              with pytest.raises(IncompatibleUnitException):
                Measure(value=-4,error=None,unit=Unit("5 s")) + Measure(value=0,error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("5 s")) + Measure(value=-3,error=None,unit=Unit("5 m^2"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("5 s")) + Measure(value=3,error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=None,unit=Unit("5 s")) + Measure(value=0,error=None,unit=Unit("5 m^2"))
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=None,unit=Unit("5 s")) + Measure(value=0.3,error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=None,unit=Unit("5 s")) + Measure(value=0.0,error=None,unit=Unit("5 m^2"))
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("5 s")) + Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=None,unit=Unit("5 s")) + Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2"))
          # Convoluted Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=27,error=None,unit=Unit("\u00B0C"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=2.9,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=26.85,error=None,unit=Unit("\u00B0C"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("3"),error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=-27,error=None,unit=Unit("\u00B0C"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=3,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=0,error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=27,error=None,unit=Unit("\u00B0C"))
              # Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=3.0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=0.0,error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=26.85,error=None,unit=Unit("\u00B0C"))
              # Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("3"),error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=0,error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("\u00B0C")) + Measure(value=0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
              # Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=0.0,error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=None,unit=Unit("\u00B0C")) + Measure(value=0.0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
              # Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) + Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C")) + Measure(value=Decimal("0"),error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
  
  
class TestMeasureOperatorsSub:
  # Error Formula
  # sig**2 = d/dx(x-y)**2 dx**2 + d/dy(x-y)**2 dy **2
  # sig**2 = (1)**2 dx**2 +  (-1)**2 dy **2
  # sig**2 = dx**2 + dy **2
  # 
  # sig = measure._sqrt_( dx**2 + dy **2 )
  
  
  def test_measure_measure_sub(self):
    def meas_meas_sub(
        x=None,dx=None,xu=None, 
        y=None,dy=None,yu=None, 
        u=None,du=None,mu=None,
        v=None,dv=None,mv=None,
        value = None, error=None, unit=None,
        implied=None):
      log.warning(f"x={x} , dx={dx} , xu={xu} , y={y} , dy={dy} , yu={yu}")
      floats = all([isinstance(i,float) or i==None or i==0 for i in [x,dx,y,dy]])
      
      if(floats):
        # Context Settings
        if( u==None):  u = float( x)           # If  x==None, give value
        if(du==None): du = float(dx)           # If dx==None, give value
        if(mu==None): mu = float(xu.magnitude) # If xu==None, give value
        
        if( v==None):  v = float( y)           # If  y==None, give value
        if(dv==None): dv = float(dy)           # If dy==None, give value
        if(mv==None): mv = float(yu.magnitude) # If yu==None, give value
        
        # Standard Div Values
        if(value == None): value = u-v
        if(unit  == None): 
          identical_units = xu.symbols == yu.symbols and xu.magnitude == yu.magnitude
          if(identical_units): unit = xu
          else: unit = xu.decompose()
          
        n  = float( unit.magnitude )
        if(error == None):  error = measure._sqrt_( (du*mu)**2 + (dv*mv)**2 ) / n
        
        # Standard Div Assertions
        assert isinstance(   (  Measure(value=x,error=dx,unit=xu)  -  Measure(value=y,error=dy,unit=yu)  ), Measure )
        assert math.isclose( (  Measure(value=x,error=dx,unit=xu)  -  Measure(value=y,error=dy,unit=yu)  ).value , value )
        assert math.isclose( (  Measure(value=x,error=dx,unit=xu)  -  Measure(value=y,error=dy,unit=yu)  ).error , error )
        assert (  Measure(value=x,error=dx,unit=xu)  -  Measure(value=y,error=dy,unit=yu)  ).implied == implied
        assert (  Measure(value=x,error=dx,unit=xu)  -  Measure(value=y,error=dy,unit=yu)  ).units.symbols   == unit.symbols
        assert (  Measure(value=x,error=dx,unit=xu)  -  Measure(value=y,error=dy,unit=yu)  ).units.magnitude == unit.magnitude
        assert (  Measure(value=x,error=dx,unit=xu)  -  Measure(value=y,error=dy,unit=yu)  ) == Measure(units=unit, value= value, error=error)
      else:
        # Context Settings
        if( u==None):  u = Decimal( x)  # If  x==None, give value
        if(du==None): du = Decimal(dx)  # If dx==None, give value
        if(mu==None): mu = xu.magnitude # If xu==None, give value
        
        if( v==None):  v = Decimal( y)  # If  y==None, give value
        if(dv==None): dv = Decimal(dy)  # If dy==None, give value
        if(mv==None): mv = yu.magnitude # If yu==None, give value
        
        # Standard Div Values
        if(value == None): value = u-v
        if(unit  == None): 
          identical_units = xu.symbols == yu.symbols and xu.magnitude == yu.magnitude
          if(identical_units): unit = xu
          else: unit = xu.decompose()
        n  = unit.magnitude
        if(error == None): error = measure._sqrt_( (du*mu)**2 + (dv*mv)**2 ) / n
        # Standard Div Assertions
        assert isinstance(            (  Measure(value=x,error=dx,unit=xu)  -  Measure(value=y,error=dy,unit=yu)  ), Measure )
        assert Measure._dec_isclose_( (  Measure(value=x,error=dx,unit=xu)  -  Measure(value=y,error=dy,unit=yu)  ).value , value )
        assert Measure._dec_isclose_( (  Measure(value=x,error=dx,unit=xu)  -  Measure(value=y,error=dy,unit=yu)  ).error , error )
        assert (  Measure(value=x,error=dx,unit=xu)  -  Measure(value=y,error=dy,unit=yu)  ).implied == implied
        assert (  Measure(value=x,error=dx,unit=xu)  -  Measure(value=y,error=dy,unit=yu)  ).units.symbols   == unit.symbols
        assert (  Measure(value=x,error=dx,unit=xu)  -  Measure(value=y,error=dy,unit=yu)  ).units.magnitude == unit.magnitude
        assert (  Measure(value=x,error=dx,unit=xu)  -  Measure(value=y,error=dy,unit=yu)  ) == Measure(units=unit, value= value, error=error)
    
    # Measure (Explicit Error) - Measure (Explicit Error) = Measure (Explicit Error)
    if(True):
      # Unitless - Unitless
      if(True):
        # Value 1: Int
        meas_meas_sub(
          x=4     , dx=2              , xu=Unit(), 
          y=3     , dy=1              , yu=Unit(), 
          u=None  , du=None           , mu=None,
          v=None  , dv=None           , mv=None,
          implied=False)
        # Value 2: Float
        meas_meas_sub(
          x=0.4   , dx=0.2            , xu=Unit(), 
          y=0.3   , dy=0.1            , yu=Unit(), 
          u=None  , du=None           , mu=None,
          v=None  , dv=None           , mv=None,
          implied=False)
        # Value 3: Decimal
        meas_meas_sub(
          x=Decimal("40") , dx=Decimal("20")  , xu=Unit(), 
          y=Decimal("30") , dy=Decimal("10")  , yu=Unit(), 
          u=None          , du=None           , mu=None,
          v=None          , dv=None           , mv=None,
          implied=False)
        # Value 4: Negative
        meas_meas_sub(
          x=-4    , dx=2              , xu=Unit(), 
          y=-3    , dy=1              , yu=Unit(),
          u=None  , du=None           , mu=None,
          v=None  , dv=None           , mv=None,
          implied=False)
        # Value 5: Zero
        if(True):
          # Value 1: Int
          meas_meas_sub(
            x=4     , dx=2              , xu=Unit(), 
            y=0     , dy=1              , yu=Unit(), 
            u=None  , du=None           , mu=None,
            v=None  , dv=None           , mv=None,
            implied=False)
          # Value 2: Float
          meas_meas_sub(
            x=0.4   , dx=0.2            , xu=Unit(), 
            y=0.0   , dy=0.1            , yu=Unit(), 
            u=None  , du=None           , mu=None,
            v=None  , dv=None           , mv=None,
            implied=False)
          # Value 3: Decimal
          meas_meas_sub(
            x=Decimal("40") , dx=Decimal("20")  , xu=Unit(), 
            y=Decimal("0")  , dy=Decimal("10")  , yu=Unit(), 
            u=None          , du=None           , mu=None,
            v=None          , dv=None           , mv=None,
            implied=False)
        # Preserve Inputs
        if(True):
          a = Measure(value=4,error=2) 
          b = Measure(value=3,error=2)
          c = a-b
          c = None
          assert a == Measure(value=4,error=2) 
          assert b == Measure(value=3,error=2)
      # Unitless - Unit
      if(True):
        # Normal Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=4,error=2,unit=Unit()) - Measure(value=3,error=1,unit=Unit("cm"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.4,error=0.2,unit=Unit()) - Measure(value=0.3,error=0.1,unit=Unit("cm"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit()) - Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-4,error=2,unit=Unit()) - Measure(value=-3,error=1,unit=Unit("cm"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=2,unit=Unit()) - Measure(value=0,error=1,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=2,unit=Unit()) - Measure(value=3,error=1,unit=Unit("cm"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=0.2,unit=Unit()) - Measure(value=0,error=0.1,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=0.2,unit=Unit()) - Measure(value=0.3,error=0.1,unit=Unit("cm"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit()) - Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit()) - Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=2,unit=Unit()) - Measure(value=0,error=1,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=2,unit=Unit()) - Measure(value=-3,error=1,unit=Unit("cm"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            meas_meas_sub(
              x=0     , dx=0              , xu=Unit(), 
              y=3     , dy=1              , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("cm"),
              implied=False)
            meas_meas_sub(
              x=4     , dx=2              , xu=Unit(), 
              y=0     , dy=0              , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
            # Value 2: Float
            meas_meas_sub(
              x=0     , dx=0              , xu=Unit(), 
              y=0.3   , dy=0.1            , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("cm"),
              implied=False)
            meas_meas_sub(
              x=0.4   , dx=0.2            , xu=Unit(), 
              y=0     , dy=0              , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
            # Value 3: Decimal
            meas_meas_sub(
              x=Decimal("0")  , dx=Decimal("0")   , xu=Unit(), 
              y=Decimal("30") , dy=Decimal("10")  , yu=Unit("cm"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("cm"),
              implied=False)
            meas_meas_sub(
              x=Decimal("40") , dx=Decimal("20")  , xu=Unit(), 
              y=Decimal("0")  , dy=Decimal("0")   , yu=Unit("cm"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
        # Magnitude Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=4,error=2,unit=Unit()) - Measure(value=3,error=1,unit=Unit("5 m^2"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.4,error=0.2,unit=Unit()) - Measure(value=0.3,error=0.1,unit=Unit("5 m^2"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit()) - Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-4,error=2,unit=Unit()) - Measure(value=-3,error=1,unit=Unit("5 m^2"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=2,unit=Unit()) - Measure(value=0,error=1,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=2,unit=Unit()) - Measure(value=3,error=1,unit=Unit("5 m^2"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=0.2,unit=Unit()) - Measure(value=0,error=0.1,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=0.2,unit=Unit()) - Measure(value=0.3,error=0.1,unit=Unit("5 m^2"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit()) - Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit()) - Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=2,unit=Unit()) - Measure(value=0,error=1,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=2,unit=Unit()) - Measure(value=-3,error=1,unit=Unit("5 m^2"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            meas_meas_sub(
              x=0     , dx=0              , xu=Unit(), 
              y=3     , dy=1              , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("5 m^2"),
              implied=False)
            meas_meas_sub(
              x=4     , dx=2              , xu=Unit(), 
              y=0     , dy=0              , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
            # Value 2: Float
            meas_meas_sub(
              x=0     , dx=0              , xu=Unit(), 
              y=0.3   , dy=0.1            , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("5 m^2"),
              implied=False)
            meas_meas_sub(
              x=0.4   , dx=0.2            , xu=Unit(), 
              y=0     , dy=0              , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
            # Value 3: Decimal
            meas_meas_sub(
              x=Decimal("0")  , dx=Decimal("0")   , xu=Unit(), 
              y=Decimal("30") , dy=Decimal("10")  , yu=Unit("5 m^2"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("5 m^2"),
              implied=False)
            meas_meas_sub(
              x=Decimal("40") , dx=Decimal("20")  , xu=Unit(), 
              y=Decimal("0")  , dy=Decimal("0")   , yu=Unit("5 m^2"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
        # Convoluted Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=300,error=2,unit=Unit()) - Measure(value=27,error=1,unit=Unit("\u00B0C"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=299.9,error=0.02,unit=Unit()) - Measure(value=26.85,error=0.01,unit=Unit("\u00B0C"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit()) - Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=300,error=2,unit=Unit()) - Measure(value=-27,error=1,unit=Unit("\u00B0C"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300,error=2,unit=Unit()) - Measure(value=0,error=1,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=2,unit=Unit()) - Measure(value=27,error=1,unit=Unit("\u00B0C"))
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300.0,error=0.02,unit=Unit()) - Measure(value=0.0,error=0.01,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=0.02,unit=Unit()) - Measure(value=26.85,error=0.01,unit=Unit("\u00B0C"))
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit()) - Measure(value=Decimal("0"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("0.02"),unit=Unit()) - Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300,error=2,unit=Unit()) - Measure(value=0,error=0,unit=Unit("\u00B0C"))
            meas_meas_sub(
              x=0             , dx=0              , xu=Unit(), 
              y=27            , dy=1              , yu=Unit("\u00B0C"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("\u00B0C"),
              implied=False)
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300.0,error=0.02,unit=Unit()) - Measure(value=0.0,error=0.0,unit=Unit("\u00B0C"))
            meas_meas_sub(
              x=0             , dx=0              , xu=Unit(), 
              y=26.85         , dy=0.01           , yu=Unit("\u00B0C"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("\u00B0C"),
              implied=False)
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit()) - Measure(value=Decimal("0"),error=Decimal("0"),unit=Unit("\u00B0C"))
            meas_meas_sub(
              x=Decimal("0")      , dx=Decimal("0")     , xu=Unit(), 
              y=Decimal("26.85")  , dy=Decimal("0.01")  , yu=Unit("\u00B0C"), 
              u=None              , du=None             , mu=None,
              v=None              , dv=None             , mv=None,
              unit=Unit("\u00B0C"), 
              implied=False)
      # Unit - Unitless
      if(True):
        # Normal Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=3,error=1,unit=Unit("cm")) - Measure(value=4,error=2,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.3,error=0.1,unit=Unit("cm")) - Measure(value=0.4,error=0.2,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm")) - Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-3,error=1,unit=Unit("cm")) - Measure(value=-4,error=2,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=1,unit=Unit("cm")) - Measure(value=4,error=2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=1,unit=Unit("cm")) - Measure(value=0,error=2,unit=Unit())
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=0.1,unit=Unit("cm")) - Measure(value=0.4,error=0.2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=0.1,unit=Unit("cm")) - Measure(value=0,error=0.2,unit=Unit())
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("cm")) - Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm")) - Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit())
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=1,unit=Unit("cm")) - Measure(value=-4,error=2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-3,error=1,unit=Unit("cm")) - Measure(value=0,error=2,unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            meas_meas_sub(
              x=3     , dx=1              , xu=Unit("cm"), 
              y=0     , dy=0              , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("cm"),
              implied=False)
            meas_meas_sub(
              x=0     , dx=0              , xu=Unit("cm"), 
              y=4     , dy=2              , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
            # Value 2: Float
            meas_meas_sub(
              x=0.3   , dx=0.1            , xu=Unit("cm"), 
              y=0     , dy=0              , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("cm"),
              implied=False)
            meas_meas_sub(
              x=0     , dx=0              , xu=Unit("cm"), 
              y=0.4   , dy=0.2            , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
            # Value 3: Decimal
            meas_meas_sub(
              x=Decimal("30") , dx=Decimal("10")  , xu=Unit("cm"), 
              y=Decimal("0")  , dy=Decimal("0")   , yu=Unit(), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("cm"),
              implied=False)
            meas_meas_sub(
              x=Decimal("0")  , dx=Decimal("0")   , xu=Unit("cm"), 
              y=Decimal("40") , dy=Decimal("20")  , yu=Unit(), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
        # Magnitude Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=3,error=1,unit=Unit("5 m^2")) - Measure(value=4,error=2,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.3,error=0.1,unit=Unit("5 m^2")) - Measure(value=0.4,error=0.2,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2")) - Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-3,error=1,unit=Unit("5 m^2")) - Measure(value=-4,error=2,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=1,unit=Unit("5 m^2")) - Measure(value=4,error=2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=1,unit=Unit("5 m^2")) - Measure(value=0,error=2,unit=Unit())
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=0.1,unit=Unit("5 m^2")) - Measure(value=0.4,error=0.2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=0.1,unit=Unit("5 m^2")) - Measure(value=0,error=0.2,unit=Unit())
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("5 m^2")) - Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2")) - Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit())
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=1,unit=Unit("5 m^2")) - Measure(value=-4,error=2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-3,error=1,unit=Unit("5 m^2")) - Measure(value=0,error=2,unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            meas_meas_sub(
              x=3     , dx=1              , xu=Unit("5 m^2"), 
              y=0     , dy=0              , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("5 m^2"),
              implied=False)
            meas_meas_sub(
              x=0     , dx=0              , xu=Unit("5 m^2"), 
              y=4     , dy=2              , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
            # Value 2: Float
            meas_meas_sub(
              x=0.3   , dx=0.1            , xu=Unit("5 m^2"), 
              y=0     , dy=0              , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("5 m^2"),
              implied=False)
            meas_meas_sub(
              x=0     , dx=0              , xu=Unit("5 m^2"), 
              y=0.4   , dy=0.2            , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
            # Value 3: Decimal
            meas_meas_sub(
              x=Decimal("30") , dx=Decimal("10")  , xu=Unit("5 m^2"), 
              y=Decimal("0")  , dy=Decimal("0")   , yu=Unit(), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("5 m^2"),
              implied=False)
            meas_meas_sub(
              x=Decimal("0")  , dx=Decimal("0")   , xu=Unit("5 m^2"), 
              y=Decimal("40") , dy=Decimal("20")  , yu=Unit(), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit(),
              implied=False)
        # Convoluted Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=27,error=1,unit=Unit("\u00B0C")) - Measure(value=300,error=2,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=26.85,error=0.01,unit=Unit("\u00B0C")) - Measure(value=299.9,error=0.02,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C")) - Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-27,error=1,unit=Unit("\u00B0C")) - Measure(value=300,error=2,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=1,unit=Unit("\u00B0C")) - Measure(value=300,error=2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=27,error=1,unit=Unit("\u00B0C")) - Measure(value=0,error=2,unit=Unit())
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=0.01,unit=Unit("\u00B0C")) - Measure(value=300.0,error=0.02,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=26.85,error=0.01,unit=Unit("\u00B0C")) - Measure(value=0.0,error=0.02,unit=Unit())
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("0.01"),unit=Unit("\u00B0C")) - Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C")) - Measure(value=Decimal("0"),error=Decimal("0.02"),unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=0,unit=Unit("\u00B0C")) - Measure(value=300,error=2,unit=Unit())
            meas_meas_sub(
              x=27            , dx=1              , xu=Unit("\u00B0C"), 
              y=0             , dy=0              , yu=Unit(), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("\u00B0C"),
              implied=False)
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=0.0,unit=Unit("\u00B0C")) - Measure(value=300.0,error=0.02,unit=Unit())
            meas_meas_sub(
              x=26.85         , dx=0.01           , xu=Unit("\u00B0C"), 
              y=0             , dy=0              , yu=Unit(), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("\u00B0C"),
              implied=False)
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("0"),unit=Unit("\u00B0C")) - Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit())
            meas_meas_sub(
              x=Decimal("26.85")  , dx=Decimal("0.01")  , xu=Unit("\u00B0C"), 
              y=Decimal("0")      , dy=Decimal("0")     , yu=Unit(), 
              u=None              , du=None             , mu=None,
              v=None              , dv=None             , mv=None,
              unit=Unit("\u00B0C"), 
              implied=False)
      # Unit - Unit
      if(True):
        # Same Units
        if(True):
          # Normal Units
          if(True):
            # Value 1: Int
            meas_meas_sub(
              x=4     , dx=2              , xu=Unit("cm"), 
              y=3     , dy=1              , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              implied=False)
            # Value 2: Float
            meas_meas_sub(
              x=0.4   , dx=0.2            , xu=Unit("cm"), 
              y=0.3   , dy=0.1            , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              implied=False)
            # Value 3: Decimal
            meas_meas_sub(
              x=Decimal("40") , dx=Decimal("20")  , xu=Unit("cm"), 
              y=Decimal("30") , dy=Decimal("10")  , yu=Unit("cm"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              implied=False)
            # Value 4: Negative
            meas_meas_sub(
              x=-4    , dx=2              , xu=Unit("cm"), 
              y=-3    , dy=1              , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              implied=False)
            # Value 5: Zero
            if(True):
              # Value 1: Int
              meas_meas_sub(
                x=0     , dx=2              , xu=Unit("cm"), 
                y=3     , dy=1              , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
              meas_meas_sub(
                x=4     , dx=2              , xu=Unit("cm"), 
                y=0     , dy=1              , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
              # Value 2: Float
              meas_meas_sub(
                x=0.0   , dx=0.2            , xu=Unit("cm"), 
                y=0.3   , dy=0.1            , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
              meas_meas_sub(
                x=0.4   , dx=0.2            , xu=Unit("cm"), 
                y=0.0   , dy=0.1            , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
              # Value 3: Decimal
              meas_meas_sub(
                x=Decimal("0")  , dx=Decimal("20")  , xu=Unit("cm"), 
                y=Decimal("30") , dy=Decimal("10")  , yu=Unit("cm"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=None           , mv=None,
                implied=False)
              meas_meas_sub(
                x=Decimal("40") , dx=Decimal("20")  , xu=Unit("cm"), 
                y=Decimal("0")  , dy=Decimal("10")  , yu=Unit("cm"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=None           , mv=None,
                implied=False)
              # Value 4: Negative
              meas_meas_sub(
                x=0     , dx=2              , xu=Unit("cm"), 
                y=-3    , dy=1              , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
              meas_meas_sub(
                x=-4    , dx=2              , xu=Unit("cm"), 
                y=0     , dy=1              , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
          # Magnitude Units
          if(True):
            # Value 1: Int
            meas_meas_sub(
              x=4     , dx=2              , xu=Unit("5 m^2"), 
              y=3     , dy=1              , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              implied=False)
            # Value 2: Float
            meas_meas_sub(
              x=0.4   , dx=0.2            , xu=Unit("5 m^2"), 
              y=0.3   , dy=0.1            , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              implied=False)
            # Value 3: Decimal
            meas_meas_sub(
              x=Decimal("40") , dx=Decimal("20")  , xu=Unit("5 m^2"), 
              y=Decimal("30") , dy=Decimal("10")  , yu=Unit("5 m^2"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=None           , mv=None,
              implied=False)
            # Value 4: Negative
            meas_meas_sub(
              x=-4    , dx=2              , xu=Unit("5 m^2"), 
              y=-3    , dy=1              , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=None           , mv=None,
              implied=False)
            # Value 5: Zero
            if(True):
              # Value 1: Int
              meas_meas_sub(
                x=0     , dx=2              , xu=Unit("5 m^2"), 
                y=3     , dy=1              , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
              meas_meas_sub(
                x=4     , dx=2              , xu=Unit("5 m^2"), 
                y=0     , dy=1              , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
              # Value 2: Float
              meas_meas_sub(
                x=0.0   , dx=0.2            , xu=Unit("5 m^2"), 
                y=0.3   , dy=0.1            , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
              meas_meas_sub(
                x=0.4   , dx=0.2            , xu=Unit("5 m^2"), 
                y=0.0   , dy=0.1            , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
              # Value 3: Decimal
              meas_meas_sub(
                x=Decimal("0")  , dx=Decimal("20")  , xu=Unit("5 m^2"), 
                y=Decimal("30") , dy=Decimal("10")  , yu=Unit("5 m^2"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=None           , mv=None,
                implied=False)
              meas_meas_sub(
                x=Decimal("40") , dx=Decimal("20")  , xu=Unit("5 m^2"), 
                y=Decimal("0")  , dy=Decimal("10")  , yu=Unit("5 m^2"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=None           , mv=None,
                implied=False)
              # Value 4: Negative
              meas_meas_sub(
                x=0     , dx=2              , xu=Unit("5 m^2"), 
                y=-3    , dy=1              , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
              meas_meas_sub(
                x=-4    , dx=2              , xu=Unit("5 m^2"), 
                y=0     , dy=1              , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=False)
          # Convoluted Units
          if(True):
            # Value 1: Int
            meas_meas_sub(
              x=26                , dx=2    , xu=Unit("\u00B0C"), 
              y=27                , dy=1    , yu=Unit("\u00B0C"), 
              u=Decimal("299.85") , du=None , mu=None,
              v=Decimal("300.15") , dv=None , mv=None,
              value = Decimal("299.85") - Decimal("300.15") - Decimal("273.85"),
              implied=False)
            # Value 2: Float
            meas_meas_sub(
              x=26.85 , dx=0.02 , xu=Unit("\u00B0C"), 
              y=26.85 , dy=0.01 , yu=Unit("\u00B0C"), 
              u=300.0 , du=None , mu=None,
              v=300.0 , dv=None , mv=None,
              value = 300.0 - 300.0 - 273.15,
              implied=False)
            # Value 3: Decimal
            meas_meas_sub(
              x=Decimal("26.85")  , dx=Decimal("0.02")  , xu=Unit("\u00B0C"), 
              y=Decimal("26.85")  , dy=Decimal("0.01")  , yu=Unit("\u00B0C"), 
              u=Decimal("300")    , du=None             , mu=None,
              v=Decimal("300")    , dv=None             , mv=None,
              value = Decimal("300") - Decimal("300") - Decimal("273.15"),
              implied=False)
            # Value 4: Negative
            meas_meas_sub(
              x=-31               , dx=2    , xu=Unit("\u00B0C"), 
              y=-27               , dy=1    , yu=Unit("\u00B0C"), 
              u=Decimal("242.15") , du=None , mu=None,
              v=Decimal("246.15") , dv=None , mv=None,
              value = Decimal("242.15") - Decimal("246.15") - Decimal("273.15"),
              implied=False)
            # Value 5: Zero
            if(True):
              # Int
              meas_meas_sub(
                x=27                , dx=2    , xu=Unit("\u00B0C"), 
                y=0                 , dy=1    , yu=Unit("\u00B0C"), 
                u=Decimal("300.15") , du=None , mu=None,
                v=Decimal("273.15") , dv=None , mv=None,
                value = Decimal("300.15") - Decimal("273.15") - Decimal("273.15"),
                implied=False)
              # Float
              meas_meas_sub(
                x=26.85   , dx=0.02 , xu=Unit("\u00B0C"), 
                y=0.0     , dy=0.01 , yu=Unit("\u00B0C"), 
                u=300.0   , du=None , mu=None,
                v=273.15  , dv=None , mv=None,
                value = 300.0-273.15-273.15,
                implied=False)
              # Decimal
              meas_meas_sub(
                x=Decimal("26.85")  , dx=Decimal("0.02"), xu=Unit("\u00B0C"), 
                y=Decimal("0")      , dy=Decimal("0.01"), yu=Unit("\u00B0C"), 
                u=Decimal("300")    , du=None           , mu=None,
                v=Decimal("273.15") , dv=None           , mv=None,
                value = Decimal("300") - Decimal("273.15") - Decimal("273.15"),
                implied=False)
        # Different Units
        if(True):
          # Normal Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=2,unit=Unit("s")) - Measure(value=3,error=1,unit=Unit("cm"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=0.2,unit=Unit("s")) - Measure(value=0.3,error=0.1,unit=Unit("cm"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("s")) - Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=2,unit=Unit("s")) - Measure(value=-3,error=1,unit=Unit("cm"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=2,unit=Unit("s")) - Measure(value=0,error=1,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=2,unit=Unit("s")) - Measure(value=3,error=1,unit=Unit("cm"))
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=0.2,unit=Unit("s")) - Measure(value=0,error=0.1,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=0.2,unit=Unit("s")) - Measure(value=0.3,error=0.1,unit=Unit("cm"))
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("s")) - Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit("s")) - Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm"))
              # Value 4: Negative
              with pytest.raises(IncompatibleUnitException):
                Measure(value=-4,error=2,unit=Unit("s")) - Measure(value=0,error=1,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=2,unit=Unit("s")) - Measure(value=-3,error=1,unit=Unit("cm"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Value 1: Int
              meas_meas_sub(
                x=0     , dx=0              , xu=Unit("s"), 
                y=3     , dy=1              , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("cm"),
                implied=False)
              meas_meas_sub(
                x=4     , dx=2              , xu=Unit("s"), 
                y=0     , dy=0              , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("s"),
                implied=False)
              # Value 2: Float
              meas_meas_sub(
                x=0     , dx=0              , xu=Unit("s"), 
                y=0.3   , dy=0.1            , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("cm"),
                implied=False)
              meas_meas_sub(
                x=0.4   , dx=0.2            , xu=Unit("s"), 
                y=0     , dy=0              , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("s"),
                implied=False)
              # Value 3: Decimal
              meas_meas_sub(
                x=Decimal("0")  , dx=Decimal("0")   , xu=Unit("s"), 
                y=Decimal("30") , dy=Decimal("10")  , yu=Unit("cm"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=None           , mv=None,
                unit=Unit("cm"),
                implied=False)
              meas_meas_sub(
                x=Decimal("40") , dx=Decimal("20")  , xu=Unit("s"), 
                y=Decimal("0")  , dy=Decimal("0")   , yu=Unit("cm"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=None           , mv=None,
                unit=Unit("s"),
                implied=False)
          # Magnitude Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=2,unit=Unit("5 s")) - Measure(value=3,error=1,unit=Unit("5 m^2"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=0.2,unit=Unit("5 s")) - Measure(value=0.3,error=0.1,unit=Unit("5 m^2"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("5 s")) - Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=2,unit=Unit("5 s")) - Measure(value=-3,error=1,unit=Unit("5 m^2"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=2,unit=Unit("5 s")) - Measure(value=0,error=1,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=2,unit=Unit("5 s")) - Measure(value=3,error=1,unit=Unit("5 m^2"))
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=0.2,unit=Unit("5 s")) - Measure(value=0,error=0.1,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=0.2,unit=Unit("5 s")) - Measure(value=0.3,error=0.1,unit=Unit("5 m^2"))
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("5 s")) - Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit("5 s")) - Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2"))
              # Value 4: Negative
              with pytest.raises(IncompatibleUnitException):
                Measure(value=-4,error=2,unit=Unit("5 s")) - Measure(value=0,error=1,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=2,unit=Unit("5 s")) - Measure(value=-3,error=1,unit=Unit("5 m^2"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Value 1: Int
              meas_meas_sub(
                x=0     , dx=0              , xu=Unit("5 s"), 
                y=3     , dy=1              , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("5 m^2"),
                implied=False)
              meas_meas_sub(
                x=4     , dx=2              , xu=Unit("5 s"), 
                y=0     , dy=0              , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("5 s"),
                implied=False)
              # Value 2: Float
              meas_meas_sub(
                x=0     , dx=0              , xu=Unit("5 s"), 
                y=0.3   , dy=0.1            , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("5 m^2"),
                implied=False)
              meas_meas_sub(
                x=0.4   , dx=0.2            , xu=Unit("5 s"), 
                y=0     , dy=0              , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("5 s"),
                implied=False)
              # Value 3: Decimal
              meas_meas_sub(
                x=Decimal("0")  , dx=Decimal("0")   , xu=Unit("5 s"), 
                y=Decimal("30") , dy=Decimal("10")  , yu=Unit("5 m^2"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=None           , mv=None,
                unit=Unit("5 m^2"),
                implied=False)
              meas_meas_sub(
                x=Decimal("40") , dx=Decimal("20")  , xu=Unit("5 s"), 
                y=Decimal("0")  , dy=Decimal("0")   , yu=Unit("5 m^2"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=None           , mv=None,
                unit=Unit("5 s"),
                implied=False)
          # Convoluted Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=2,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=27,error=1,unit=Unit("\u00B0C"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=2.9,error=0.02,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=26.85,error=0.01,unit=Unit("\u00B0C"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("3"),error=Decimal("0.02"),unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=2,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=-27,error=1,unit=Unit("\u00B0C"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=3,error=2,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=0,error=1,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=2,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=27,error=1,unit=Unit("\u00B0C"))
              # Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=3.0,error=0.02,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=0.0,error=0.01,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=0.02,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=26.85,error=0.01,unit=Unit("\u00B0C"))
              # Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("3"),error=Decimal("0.02"),unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=Decimal("0"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=Decimal("0.02"),unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=0,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=0,error=0,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=0,unit=Unit("\u00B0C")) - Measure(value=0,error=0,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
              # Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=0.0,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=0.0,error=0.0,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=0.0,unit=Unit("\u00B0C")) - Measure(value=0.0,error=0.0,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
              # Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=Decimal("0.0"),unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=Decimal("0"),error=Decimal("0"),unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=Decimal("0"),unit=Unit("\u00B0C")) - Measure(value=Decimal("0"),error=Decimal("0.0"),unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
    # Measure (Explicit Error) - Measure (Implicit Error) = Measure (Implicit Error)
    if(True):
      # Unitless - Unitless
      if(True):
        # Value 1: Int
        meas_meas_sub(
          x=4     , dx=2              , xu=Unit(), 
          y=3     , dy=None           , yu=Unit(), 
          u=None  , du=None           , mu=None,
          v=None  , dv=Decimal("0.5") , mv=None,
          implied=True)
        # Value 2: Float
        meas_meas_sub(
          x=0.4   , dx=0.2            , xu=Unit(), 
          y=0.3   , dy=None           , yu=Unit(), 
          u=None  , du=None           , mu=None,
          v=None  , dv=0.05           , mv=None,
          implied=True)
        # Value 3: Decimal
        meas_meas_sub(
          x=Decimal("40") , dx=Decimal("20")  , xu=Unit(), 
          y=Decimal("30") , dy=None           , yu=Unit(), 
          u=None          , du=None           , mu=None,
          v=None          , dv=Decimal("5")   , mv=None,
          implied=True)
        # Value 4: Negative
        meas_meas_sub(
          x=-4    , dx=2              , xu=Unit(), 
          y=-3    , dy=None           , yu=Unit(),
          u=None  , du=None           , mu=None,
          v=None  , dv=Decimal("0.5") , mv=None,
          implied=True)
        # Value 5: Zero
        if(True):
          # Value 1: Int
          meas_meas_sub(
            x=4     , dx=2              , xu=Unit(), 
            y=0     , dy=None           , yu=Unit(), 
            u=None  , du=None           , mu=None,
            v=None  , dv=Decimal("0.5") , mv=None,
            implied=True)
          # Value 2: Float
          meas_meas_sub(
            x=0.4   , dx=0.2            , xu=Unit(), 
            y=0.0   , dy=None           , yu=Unit(), 
            u=None  , du=None           , mu=None,
            v=None  , dv=0.05           , mv=None,
            implied=True)
          # Value 3: Decimal
          meas_meas_sub(
            x=Decimal("40") , dx=Decimal("20")  , xu=Unit(), 
            y=Decimal("0")  , dy=None           , yu=Unit(), 
            u=None          , du=None           , mu=None,
            v=None          , dv=Decimal("0.5") , mv=None,
            implied=True)
        # Preserve Inputs
        if(True):
          a = Measure(value=4,error=2) 
          b = Measure(value=3,error=None)
          c = a-b
          c = None
          assert a == Measure(value=4,error=2) 
          assert b == Measure(value=3,error=None)
      # Unitless - Unit
      if(True):
        # Normal Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=4,error=2,unit=Unit()) - Measure(value=3,error=None,unit=Unit("cm"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.4,error=0.2,unit=Unit()) - Measure(value=0.3,error=None,unit=Unit("cm"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit()) - Measure(value=Decimal("30"),error=None,unit=Unit("cm"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-4,error=2,unit=Unit()) - Measure(value=-3,error=None,unit=Unit("cm"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=2,unit=Unit()) - Measure(value=0,error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=2,unit=Unit()) - Measure(value=3,error=None,unit=Unit("cm"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=0.2,unit=Unit()) - Measure(value=0,error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=0.2,unit=Unit()) - Measure(value=0.3,error=None,unit=Unit("cm"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit()) - Measure(value=Decimal("0"),error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit()) - Measure(value=Decimal("30"),error=None,unit=Unit("cm"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=2,unit=Unit()) - Measure(value=0,error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=2,unit=Unit()) - Measure(value=-3,error=None,unit=Unit("cm"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            meas_meas_sub(
              x=0     , dx=0              , xu=Unit(), 
              y=3     , dy=None           , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              unit=Unit("cm"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=2,unit=Unit()) - Measure(value=0,error=None,unit=Unit("cm"))
            # Value 2: Float
            meas_meas_sub(
              x=0     , dx=0              , xu=Unit(), 
              y=0.3   , dy=None           , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=0.05           , mv=None,
              unit=Unit("cm"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=0.2,unit=Unit()) - Measure(value=0,error=None,unit=Unit("cm"))
            # Value 3: Decimal
            meas_meas_sub(
              x=Decimal("0")  , dx=Decimal("0")   , xu=Unit(), 
              y=Decimal("30") , dy=None           , yu=Unit("cm"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=Decimal("5")   , mv=None,
              unit=Unit("cm"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit()) - Measure(value=Decimal("0"),error=None,unit=Unit("cm"))
        # Magnitude Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=4,error=2,unit=Unit()) - Measure(value=3,error=None,unit=Unit("5 m^2"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.4,error=0.2,unit=Unit()) - Measure(value=0.3,error=None,unit=Unit("5 m^2"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit()) - Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-4,error=2,unit=Unit()) - Measure(value=-3,error=None,unit=Unit("5 m^2"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=2,unit=Unit()) - Measure(value=0,error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=2,unit=Unit()) - Measure(value=3,error=None,unit=Unit("5 m^2"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=0.2,unit=Unit()) - Measure(value=0,error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=0.2,unit=Unit()) - Measure(value=0.3,error=None,unit=Unit("5 m^2"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit()) - Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit()) - Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=2,unit=Unit()) - Measure(value=0,error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=2,unit=Unit()) - Measure(value=-3,error=None,unit=Unit("5 m^2"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            meas_meas_sub(
              x=0     , dx=0              , xu=Unit(), 
              y=3     , dy=None           , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              unit=Unit("5 m^2"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=2,unit=Unit()) - Measure(value=0,error=None,unit=Unit("5 m^2"))
            # Value 2: Float
            meas_meas_sub(
              x=0     , dx=0              , xu=Unit(), 
              y=0.3   , dy=None           , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=0.05           , mv=None,
              unit=Unit("5 m^2"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=0.2,unit=Unit()) - Measure(value=0.0,error=None,unit=Unit("5 m^2"))
            # Value 3: Decimal
            meas_meas_sub(
              x=Decimal("0")  , dx=Decimal("0")   , xu=Unit(), 
              y=Decimal("30") , dy=None           , yu=Unit("5 m^2"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=Decimal("5")   , mv=None,
              unit=Unit("5 m^2"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit()) - Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2"))
        # Convoluted Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=300,error=2,unit=Unit()) - Measure(value=27,error=None,unit=Unit("\u00B0C"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=299.9,error=0.02,unit=Unit()) - Measure(value=26.85,error=None,unit=Unit("\u00B0C"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit()) - Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=300,error=2,unit=Unit()) - Measure(value=-27,error=None,unit=Unit("\u00B0C"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300,error=2,unit=Unit()) - Measure(value=0,error=None,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=2,unit=Unit()) - Measure(value=27,error=None,unit=Unit("\u00B0C"))
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300.0,error=0.02,unit=Unit()) - Measure(value=0.0,error=None,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=0.02,unit=Unit()) - Measure(value=26.85,error=None,unit=Unit("\u00B0C"))
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit()) - Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("0.02"),unit=Unit()) - Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300,error=2,unit=Unit()) - Measure(value=0,error=None,unit=Unit("\u00B0C"))
            meas_meas_sub(
              x=0             , dx=0              , xu=Unit(), 
              y=27            , dy=None           , yu=Unit("\u00B0C"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=Decimal("0.5") , mv=None,
              unit=Unit("\u00B0C"),
              implied=True)
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300.0,error=0.02,unit=Unit()) - Measure(value=0.0,error=None,unit=Unit("\u00B0C"))
            meas_meas_sub(
              x=0             , dx=0              , xu=Unit(), 
              y=26.85         , dy=None           , yu=Unit("\u00B0C"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=0.005          , mv=None,
              unit=Unit("\u00B0C"),
              implied=True)
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit()) - Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C"))
            meas_meas_sub(
              x=Decimal("0")      , dx=Decimal("0")     , xu=Unit(), 
              y=Decimal("26.85")  , dy=None             , yu=Unit("\u00B0C"), 
              u=None              , du=None             , mu=None,
              v=None              , dv=Decimal("0.005") , mv=None,
              unit=Unit("\u00B0C"), 
              implied=True)
      # Unit - Unitless
      if(True):
        # Normal Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=3,error=1,unit=Unit("cm")) - Measure(value=4,error=None,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.3,error=0.1,unit=Unit("cm")) - Measure(value=0.4,error=None,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm")) - Measure(value=Decimal("40"),error=None,unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-3,error=1,unit=Unit("cm")) - Measure(value=-4,error=None,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=1,unit=Unit("cm")) - Measure(value=4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=1,unit=Unit("cm")) - Measure(value=0,error=None,unit=Unit())
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=0.1,unit=Unit("cm")) - Measure(value=0.4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=0.1,unit=Unit("cm")) - Measure(value=0,error=None,unit=Unit())
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("cm")) - Measure(value=Decimal("40"),error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm")) - Measure(value=Decimal("0"),error=None,unit=Unit())
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=1,unit=Unit("cm")) - Measure(value=-4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-3,error=1,unit=Unit("cm")) - Measure(value=0,error=None,unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=1,unit=Unit("cm")) - Measure(value=0,error=None,unit=Unit())
            meas_meas_sub(
              x=0     , dx=0              , xu=Unit("cm"), 
              y=4     , dy=None           , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              unit=Unit(),
              implied=True)
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=0.1,unit=Unit("cm")) - Measure(value=0.0,error=None,unit=Unit())
            meas_meas_sub(
              x=0     , dx=0              , xu=Unit("cm"), 
              y=0.4   , dy=None           , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=0.05           , mv=None,
              unit=Unit(),
              implied=True)
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm")) - Measure(value=Decimal("0"),error=None,unit=Unit())
            meas_meas_sub(
              x=Decimal("0")  , dx=Decimal("0")   , xu=Unit("cm"), 
              y=Decimal("40") , dy=None           , yu=Unit(), 
              u=None          , du=None           , mu=None,
              v=None          , dv=Decimal("5")   , mv=None,
              unit=Unit(),
              implied=True)
        # Magnitude Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=3,error=1,unit=Unit("5 m^2")) - Measure(value=4,error=None,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.3,error=0.1,unit=Unit("5 m^2")) - Measure(value=0.4,error=None,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2")) - Measure(value=Decimal("40"),error=None,unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-3,error=1,unit=Unit("5 m^2")) - Measure(value=-4,error=None,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=1,unit=Unit("5 m^2")) - Measure(value=4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=1,unit=Unit("5 m^2")) - Measure(value=0,error=None,unit=Unit())
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=0.1,unit=Unit("5 m^2")) - Measure(value=0.4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=0.1,unit=Unit("5 m^2")) - Measure(value=0,error=None,unit=Unit())
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("5 m^2")) - Measure(value=Decimal("40"),error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2")) - Measure(value=Decimal("0"),error=None,unit=Unit())
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=1,unit=Unit("5 m^2")) - Measure(value=-4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-3,error=1,unit=Unit("5 m^2")) - Measure(value=0,error=None,unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=1,unit=Unit("5 m^2")) - Measure(value=0,error=None,unit=Unit())
            meas_meas_sub(
              x=0     , dx=0              , xu=Unit("5 m^2"), 
              y=4     , dy=None           , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              unit=Unit(),
              implied=True)
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=0.1,unit=Unit("5 m^2")) - Measure(value=0.0,error=None,unit=Unit())
            meas_meas_sub(
              x=0     , dx=0              , xu=Unit("5 m^2"), 
              y=0.4   , dy=None           , yu=Unit(), 
              u=None  , du=None           , mu=None,
              v=None  , dv=0.05           , mv=None,
              unit=Unit(),
              implied=True)
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2")) - Measure(value=Decimal("0"),error=None,unit=Unit())
            meas_meas_sub(
              x=Decimal("0")  , dx=Decimal("0")   , xu=Unit("5 m^2"), 
              y=Decimal("40") , dy=None           , yu=Unit(), 
              u=None          , du=None           , mu=None,
              v=None          , dv=Decimal("5")   , mv=None,
              unit=Unit(),
              implied=True)
        # Convoluted Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=27,error=1,unit=Unit("\u00B0C")) - Measure(value=300,error=None,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=26.85,error=0.01,unit=Unit("\u00B0C")) - Measure(value=299.9,error=None,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C")) - Measure(value=Decimal("300"),error=None,unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-27,error=1,unit=Unit("\u00B0C")) - Measure(value=300,error=None,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=1,unit=Unit("\u00B0C")) - Measure(value=300,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=27,error=1,unit=Unit("\u00B0C")) - Measure(value=0,error=None,unit=Unit())
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=0.01,unit=Unit("\u00B0C")) - Measure(value=300.0,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=26.85,error=0.01,unit=Unit("\u00B0C")) - Measure(value=0.0,error=None,unit=Unit())
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("0.01"),unit=Unit("\u00B0C")) - Measure(value=Decimal("300"),error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C")) - Measure(value=Decimal("0"),error=None,unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=0,unit=Unit("\u00B0C")) - Measure(value=300,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=27,error=1,unit=Unit("\u00B0C")) - Measure(value=0,error=None,unit=Unit())
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=0.0,unit=Unit("\u00B0C")) - Measure(value=300.0,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=26.85,error=0.01,unit=Unit("\u00B0C")) - Measure(value=0.0,error=None,unit=Unit())
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=Decimal("0"),unit=Unit("\u00B0C")) - Measure(value=Decimal("300"),error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C")) - Measure(value=Decimal("0"),error=None,unit=Unit())
      # Unit - Unit
      if(True):
        # Same Units
        if(True):
          # Normal Units
          if(True):
            # Value 1: Int
            meas_meas_sub(
              x=4     , dx=2              , xu=Unit("cm"), 
              y=3     , dy=None           , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              implied=True)
            # Value 2: Float
            meas_meas_sub(
              x=0.4   , dx=0.2            , xu=Unit("cm"), 
              y=0.3   , dy=None           , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=0.05           , mv=None,
              implied=True)
            # Value 3: Decimal
            meas_meas_sub(
              x=Decimal("40") , dx=Decimal("20")  , xu=Unit("cm"), 
              y=Decimal("30") , dy=None           , yu=Unit("cm"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=Decimal("5")   , mv=None,
              implied=True)
            # Value 4: Negative
            meas_meas_sub(
              x=-4    , dx=2              , xu=Unit("cm"), 
              y=-3    , dy=None           , yu=Unit("cm"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              implied=True)
            # Value 5: Zero
            if(True):
              # Value 1: Int
              meas_meas_sub(
                x=0     , dx=2              , xu=Unit("cm"), 
                y=3     , dy=None           , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              meas_meas_sub(
                x=4     , dx=2              , xu=Unit("cm"), 
                y=0     , dy=None           , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              # Value 2: Float
              meas_meas_sub(
                x=0.0   , dx=0.2            , xu=Unit("cm"), 
                y=0.3   , dy=None           , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=0.05           , mv=None,
                implied=True)
              meas_meas_sub(
                x=0.4   , dx=0.2            , xu=Unit("cm"), 
                y=0.0   , dy=None           , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=0.05           , mv=None,
                implied=True)
              # Value 3: Decimal
              meas_meas_sub(
                x=Decimal("0")  , dx=Decimal("20")  , xu=Unit("cm"), 
                y=Decimal("30") , dy=None           , yu=Unit("cm"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=Decimal("5")   , mv=None,
                implied=True)
              meas_meas_sub(
                x=Decimal("40") , dx=Decimal("20")  , xu=Unit("cm"), 
                y=Decimal("0")  , dy=None           , yu=Unit("cm"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=Decimal("0.5") , mv=None,
                implied=True)
              # Value 4: Negative
              meas_meas_sub(
                x=0     , dx=2              , xu=Unit("cm"), 
                y=-3    , dy=None           , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              meas_meas_sub(
                x=-4    , dx=2              , xu=Unit("cm"), 
                y=0     , dy=None           , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
          # Magnitude Units
          if(True):
            # Value 1: Int
            meas_meas_sub(
              x=4     , dx=2              , xu=Unit("5 m^2"), 
              y=3     , dy=None           , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              implied=True)
            # Value 2: Float
            meas_meas_sub(
              x=0.4   , dx=0.2            , xu=Unit("5 m^2"), 
              y=0.3   , dy=None           , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=0.05           , mv=None,
              implied=True)
            # Value 3: Decimal
            meas_meas_sub(
              x=Decimal("40") , dx=Decimal("20")  , xu=Unit("5 m^2"), 
              y=Decimal("30") , dy=None           , yu=Unit("5 m^2"), 
              u=None          , du=None           , mu=None,
              v=None          , dv=Decimal("5")   , mv=None,
              implied=True)
            # Value 4: Negative
            meas_meas_sub(
              x=-4    , dx=2              , xu=Unit("5 m^2"), 
              y=-3    , dy=None           , yu=Unit("5 m^2"), 
              u=None  , du=None           , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              implied=True)
            # Value 5: Zero
            if(True):
              # Value 1: Int
              meas_meas_sub(
                x=0     , dx=2              , xu=Unit("5 m^2"), 
                y=3     , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              meas_meas_sub(
                x=4     , dx=2              , xu=Unit("5 m^2"), 
                y=0     , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              # Value 2: Float
              meas_meas_sub(
                x=0.0   , dx=0.2            , xu=Unit("5 m^2"), 
                y=0.3   , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=0.05           , mv=None,
                implied=True)
              meas_meas_sub(
                x=0.4   , dx=0.2            , xu=Unit("5 m^2"), 
                y=0.0   , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=0.05           , mv=None,
                implied=True)
              # Value 3: Decimal
              meas_meas_sub(
                x=Decimal("0")  , dx=Decimal("20")  , xu=Unit("5 m^2"), 
                y=Decimal("30") , dy=None           , yu=Unit("5 m^2"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=Decimal("5")   , mv=None,
                implied=True)
              meas_meas_sub(
                x=Decimal("40") , dx=Decimal("20")  , xu=Unit("5 m^2"), 
                y=Decimal("0")  , dy=None           , yu=Unit("5 m^2"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=Decimal("0.5") , mv=None,
                implied=True)
              # Value 4: Negative
              meas_meas_sub(
                x=0     , dx=2              , xu=Unit("5 m^2"), 
                y=-3    , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              meas_meas_sub(
                x=-4    , dx=2              , xu=Unit("5 m^2"), 
                y=0     , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
          # Convoluted Units
          if(True):
            # Value 1: Int
            meas_meas_sub(
              x=26                , dx=2              , xu=Unit("\u00B0C"), 
              y=27                , dy=None           , yu=Unit("\u00B0C"), 
              u=Decimal("299.85") , du=None           , mu=None,
              v=Decimal("300.15") , dv=Decimal("0.5") , mv=None,
              value = Decimal("299.85") - Decimal("300.15") - Decimal("273.85"),
              implied=True)
            # Value 2: Float
            meas_meas_sub(
              x=26.85 , dx=0.02  , xu=Unit("\u00B0C"), 
              y=26.85 , dy=None  , yu=Unit("\u00B0C"), 
              u=300.0 , du=None  , mu=None,
              v=300.0 , dv=0.005 , mv=None,
              value = 300.0 - 300.0 - 273.15,
              implied=True)
            # Value 3: Decimal
            meas_meas_sub(
              x=Decimal("26.85")  , dx=Decimal("0.02")  , xu=Unit("\u00B0C"), 
              y=Decimal("26.85")  , dy=None             , yu=Unit("\u00B0C"), 
              u=Decimal("300")    , du=None             , mu=None,
              v=Decimal("300")    , dv=Decimal("0.005") , mv=None,
              value = Decimal("300") - Decimal("300") - Decimal("273.15"),
              implied=True)
            # Value 4: Negative
            meas_meas_sub(
              x=-31               , dx=2              , xu=Unit("\u00B0C"), 
              y=-27               , dy=None           , yu=Unit("\u00B0C"), 
              u=Decimal("242.15") , du=None           , mu=None,
              v=Decimal("246.15") , dv=Decimal("0.5") , mv=None,
              value = Decimal("242.15") - Decimal("246.15") - Decimal("273.15"),
              implied=True)
            # Value 5: Zero
            if(True):
              # Int
              meas_meas_sub(
                x=27                , dx=2              , xu=Unit("\u00B0C"), 
                y=0                 , dy=None           , yu=Unit("\u00B0C"), 
                u=Decimal("300.15") , du=None           , mu=None,
                v=Decimal("273.15") , dv=Decimal("0.5") , mv=None,
                value = Decimal("300.15") - Decimal("273.15") - Decimal("273.15"),
                implied=True)
              # Float
              meas_meas_sub(
                x=26.85   , dx=0.02 , xu=Unit("\u00B0C"), 
                y=0.0     , dy=None , yu=Unit("\u00B0C"), 
                u=300.0   , du=None , mu=None,
                v=273.15  , dv=0.05 , mv=None,
                value = 300.0-273.15-273.15,
                implied=True)
              # Decimal
              meas_meas_sub(
                x=Decimal("26.85")  , dx=Decimal("0.02"), xu=Unit("\u00B0C"), 
                y=Decimal("0")      , dy=None           , yu=Unit("\u00B0C"), 
                u=Decimal("300")    , du=None           , mu=None,
                v=Decimal("273.15") , dv=Decimal("0.5") , mv=None,
                value = Decimal("300") - Decimal("273.15") - Decimal("273.15"),
                implied=True)
        # Different Units
        if(True):
          # Normal Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=2,unit=Unit("s")) - Measure(value=3,error=None,unit=Unit("cm"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=0.2,unit=Unit("s")) - Measure(value=0.3,error=None,unit=Unit("cm"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("s")) - Measure(value=Decimal("30"),error=None,unit=Unit("cm"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=2,unit=Unit("s")) - Measure(value=-3,error=None,unit=Unit("cm"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=2,unit=Unit("s")) - Measure(value=0,error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=2,unit=Unit("s")) - Measure(value=3,error=None,unit=Unit("cm"))
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=0.2,unit=Unit("s")) - Measure(value=0,error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=0.2,unit=Unit("s")) - Measure(value=0.3,error=None,unit=Unit("cm"))
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("s")) - Measure(value=Decimal("0"),error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit("s")) - Measure(value=Decimal("30"),error=None,unit=Unit("cm"))
              # Value 4: Negative
              with pytest.raises(IncompatibleUnitException):
                Measure(value=-4,error=2,unit=Unit("s")) - Measure(value=0,error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=2,unit=Unit("s")) - Measure(value=-3,error=None,unit=Unit("cm"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Value 1: Int
              meas_meas_sub(
                x=0     , dx=0              , xu=Unit("s"), 
                y=3     , dy=None           , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=Decimal("0.5")  , mv=None,
                unit=Unit("cm"),
                implied=True)
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=2,unit=Unit("s")) - Measure(value=0,error=None,unit=Unit("cm"))
              # Value 2: Float
              meas_meas_sub(
                x=0     , dx=0              , xu=Unit("s"), 
                y=0.3   , dy=None           , yu=Unit("cm"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=0.05           , mv=None,
                unit=Unit("cm"),
                implied=True)
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=0.2,unit=Unit("s")) - Measure(value=0.0,error=None,unit=Unit("cm"))
              # Value 3: Decimal
              meas_meas_sub(
                x=Decimal("0")  , dx=Decimal("0")   , xu=Unit("s"), 
                y=Decimal("30") , dy=None           , yu=Unit("cm"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=Decimal("5")   , mv=None,
                unit=Unit("cm"),
                implied=True)
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("s")) - Measure(value=Decimal("0"),error=None,unit=Unit("cm"))
          # Magnitude Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=2,unit=Unit("5 s")) - Measure(value=3,error=None,unit=Unit("5 m^2"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=0.2,unit=Unit("5 s")) - Measure(value=0.3,error=None,unit=Unit("5 m^2"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("5 s")) - Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=2,unit=Unit("5 s")) - Measure(value=-3,error=None,unit=Unit("5 m^2"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=2,unit=Unit("5 s")) - Measure(value=0,error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=2,unit=Unit("5 s")) - Measure(value=3,error=None,unit=Unit("5 m^2"))
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=0.2,unit=Unit("5 s")) - Measure(value=0,error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=0.2,unit=Unit("5 s")) - Measure(value=0.3,error=None,unit=Unit("5 m^2"))
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("5 s")) - Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit("5 s")) - Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2"))
              # Value 4: Negative
              with pytest.raises(IncompatibleUnitException):
                Measure(value=-4,error=2,unit=Unit("5 s")) - Measure(value=0,error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=2,unit=Unit("5 s")) - Measure(value=-3,error=None,unit=Unit("5 m^2"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Value 1: Int
              meas_meas_sub(
                x=0     , dx=0              , xu=Unit("5 s"), 
                y=3     , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                unit=Unit("5 m^2"),
                implied=True)
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=2,unit=Unit("5 s")) - Measure(value=0,error=None,unit=Unit("5 m^2"))
              # Value 2: Float
              meas_meas_sub(
                x=0     , dx=0              , xu=Unit("5 s"), 
                y=0.3   , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=None           , mu=None,
                v=None  , dv=0.05           , mv=None,
                unit=Unit("5 m^2"),
                implied=True)
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=0.2,unit=Unit("5 s")) - Measure(value=0.0,error=None,unit=Unit("5 m^2"))
              # Value 3: Decimal
              meas_meas_sub(
                x=Decimal("0")  , dx=Decimal("0")   , xu=Unit("5 s"), 
                y=Decimal("30") , dy=None           , yu=Unit("5 m^2"), 
                u=None          , du=None           , mu=None,
                v=None          , dv=Decimal("5")   , mv=None,
                unit=Unit("5 m^2"),
                implied=True)
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("5 s")) - Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2"))
          # Convoluted Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=2,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=27,error=None,unit=Unit("\u00B0C"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=2.9,error=0.02,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=26.85,error=None,unit=Unit("\u00B0C"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("3"),error=Decimal("0.02"),unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=2,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=-27,error=None,unit=Unit("\u00B0C"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=3,error=2,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=0,error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=2,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=27,error=None,unit=Unit("\u00B0C"))
              # Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=3.0,error=0.02,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=0.0,error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=0.02,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=26.85,error=None,unit=Unit("\u00B0C"))
              # Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("3"),error=Decimal("0.02"),unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=Decimal("0.02"),unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=0,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=0,error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=0,unit=Unit("\u00B0C")) - Measure(value=0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
              # Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=0.0,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=0.0,error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=0.0,unit=Unit("\u00B0C")) - Measure(value=0.0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
              # Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=Decimal("0.0"),unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=Decimal("0"),unit=Unit("\u00B0C")) - Measure(value=Decimal("0"),error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
    # Measure (Implicit Error) - Measure (Explicit Error) = Measure (Implicit Error)
    if(True):
      # Unitless - Unitless
      if(True):
        # Value 1: Int
        meas_meas_sub(
          x=4     , dx=None           , xu=Unit(), 
          y=3     , dy=1              , yu=Unit(), 
          u=None  , du=Decimal("0.5") , mu=None,
          v=None  , dv=None           , mv=None,
          implied=True)
        # Value 2: Float
        meas_meas_sub(
          x=0.4   , dx=None           , xu=Unit(), 
          y=0.3   , dy=0.1            , yu=Unit(), 
          u=None  , du=0.05           , mu=None,
          v=None  , dv=None           , mv=None,
          implied=True)
        # Value 3: Decimal
        meas_meas_sub(
          x=Decimal("40") , dx=None           , xu=Unit(), 
          y=Decimal("30") , dy=Decimal("10")  , yu=Unit(), 
          u=None          , du=Decimal("5")   , mu=None,
          v=None          , dv=None           , mv=None,
          implied=True)
        # Value 4: Negative
        meas_meas_sub(
          x=-4    , dx=None           , xu=Unit(), 
          y=-3    , dy=1              , yu=Unit(),
          u=None  , du=Decimal("0.5") , mu=None,
          v=None  , dv=None           , mv=None,
          implied=True)
        # Value 5: Zero
        if(True):
          # Value 1: Int
          meas_meas_sub(
            x=4     , dx=None           , xu=Unit(), 
            y=0     , dy=1              , yu=Unit(), 
            u=None  , du=Decimal("0.5") , mu=None,
            v=None  , dv=None           , mv=None,
            implied=True)
          # Value 2: Float
          meas_meas_sub(
            x=0.4   , dx=None           , xu=Unit(), 
            y=0.0   , dy=0.1            , yu=Unit(), 
            u=None  , du=0.05           , mu=None,
            v=None  , dv=None           , mv=None,
            implied=True)
          # Value 3: Decimal
          meas_meas_sub(
            x=Decimal("40") , dx=None           , xu=Unit(), 
            y=Decimal("0")  , dy=Decimal("10")  , yu=Unit(), 
            u=None          , du=Decimal("5")   , mu=None,
            v=None          , dv=None           , mv=None,
            implied=True)
        # Preserve Inputs
        if(True):
          a = Measure(value=4,error=None) 
          b = Measure(value=3,error=2)
          c = a-b
          c = None
          assert a == Measure(value=4,error=None) 
          assert b == Measure(value=3,error=2)
      # Unitless - Unit
      if(True):
        # Normal Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=4,error=None,unit=Unit()) - Measure(value=3,error=1,unit=Unit("cm"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.4,error=None,unit=Unit()) - Measure(value=0.3,error=0.1,unit=Unit("cm"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("40"),error=None,unit=Unit()) - Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-4,error=None,unit=Unit()) - Measure(value=-3,error=1,unit=Unit("cm"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=None,unit=Unit()) - Measure(value=0,error=1,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=3,error=1,unit=Unit("cm"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=None,unit=Unit()) - Measure(value=0,error=0.1,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=0.3,error=0.1,unit=Unit("cm"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=None,unit=Unit()) - Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) - Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=None,unit=Unit()) - Measure(value=0,error=1,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=-3,error=1,unit=Unit("cm"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=3,error=1,unit=Unit("cm"))
            meas_meas_sub(
              x=4     , dx=None           , xu=Unit(), 
              y=0     , dy=0              , yu=Unit("cm"), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=True)
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=0.3,error=0.1,unit=Unit("cm"))
            meas_meas_sub(
              x=0.4   , dx=None           , xu=Unit(), 
              y=0     , dy=0              , yu=Unit("cm"), 
              u=None  , du=0.05           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=True)
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) - Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm"))
            meas_meas_sub(
              x=Decimal("40") , dx=None           , xu=Unit(), 
              y=Decimal("0")  , dy=Decimal("0")   , yu=Unit("cm"), 
              u=None          , du=Decimal("5")   , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit(),
              implied=True)
        # Magnitude Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=4,error=None,unit=Unit()) - Measure(value=3,error=1,unit=Unit("5 m^2"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.4,error=None,unit=Unit()) - Measure(value=0.3,error=0.1,unit=Unit("5 m^2"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("40"),error=None,unit=Unit()) - Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-4,error=None,unit=Unit()) - Measure(value=-3,error=1,unit=Unit("5 m^2"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=None,unit=Unit()) - Measure(value=0,error=1,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=3,error=1,unit=Unit("5 m^2"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=None,unit=Unit()) - Measure(value=0,error=0.1,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=0.3,error=0.1,unit=Unit("5 m^2"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=None,unit=Unit()) - Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) - Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=None,unit=Unit()) - Measure(value=0,error=1,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=-3,error=1,unit=Unit("5 m^2"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=3,error=1,unit=Unit("5 m^2"))
            meas_meas_sub(
              x=4     , dx=None           , xu=Unit(), 
              y=0     , dy=0              , yu=Unit("5 m^2"), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=True)
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=0.3,error=0.1,unit=Unit("5 m^2"))
            meas_meas_sub(
              x=0.4   , dx=None           , xu=Unit(), 
              y=0     , dy=0              , yu=Unit("5 m^2"), 
              u=None  , du=0.05           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit(),
              implied=True)
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) - Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit("5 m^2"))
            meas_meas_sub(
              x=Decimal("40") , dx=None           , xu=Unit(), 
              y=Decimal("0")  , dy=Decimal("0")   , yu=Unit("5 m^2"), 
              u=None          , du=Decimal("5")   , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit(),
              implied=True)
        # Convoluted Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=300,error=None,unit=Unit()) - Measure(value=27,error=1,unit=Unit("\u00B0C"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=299.9,error=None,unit=Unit()) - Measure(value=26.85,error=0.01,unit=Unit("\u00B0C"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("300"),error=None,unit=Unit()) - Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=300,error=None,unit=Unit()) - Measure(value=-27,error=1,unit=Unit("\u00B0C"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300,error=None,unit=Unit()) - Measure(value=0,error=1,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=27,error=1,unit=Unit("\u00B0C"))
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300.0,error=None,unit=Unit()) - Measure(value=0.0,error=0.01,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit()) - Measure(value=26.85,error=0.01,unit=Unit("\u00B0C"))
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("300"),error=None,unit=Unit()) - Measure(value=Decimal("0"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) - Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300,error=None,unit=Unit()) - Measure(value=0,error=0,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=27,error=1,unit=Unit("\u00B0C"))
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300.0,error=0.02,unit=Unit()) - Measure(value=0.0,error=0.0,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit()) - Measure(value=26.85,error=0.01,unit=Unit("\u00B0C"))
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit()) - Measure(value=Decimal("0"),error=Decimal("0"),unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) - Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
      # Unit - Unitless
      if(True):
        # Normal Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=3,error=None,unit=Unit("cm")) - Measure(value=4,error=2,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.3,error=None,unit=Unit("cm")) - Measure(value=0.4,error=0.2,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("30"),error=None,unit=Unit("cm")) - Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-3,error=None,unit=Unit("cm")) - Measure(value=-4,error=2,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("cm")) - Measure(value=4,error=2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=None,unit=Unit("cm")) - Measure(value=0,error=2,unit=Unit())
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("cm")) - Measure(value=0.4,error=0.2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=None,unit=Unit("cm")) - Measure(value=0,error=0.2,unit=Unit())
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("cm")) - Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=None,unit=Unit("cm")) - Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit())
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("cm")) - Measure(value=-4,error=2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-3,error=None,unit=Unit("cm")) - Measure(value=0,error=2,unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            meas_meas_sub(
              x=3     , dx=None           , xu=Unit("cm"), 
              y=0     , dy=0              , yu=Unit(), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("cm"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("cm")) - Measure(value=4,error=2,unit=Unit())
            # Value 2: Float
            meas_meas_sub(
              x=0.3   , dx=None           , xu=Unit("cm"), 
              y=0     , dy=0              , yu=Unit(), 
              u=None  , du=0.05           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("cm"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("cm")) - Measure(value=0.4,error=0.2,unit=Unit())
            # Value 3: Decimal
            meas_meas_sub(
              x=Decimal("30") , dx=None           , xu=Unit("cm"), 
              y=Decimal("0")  , dy=Decimal("0")   , yu=Unit(), 
              u=None          , du=Decimal("5")   , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("cm"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("cm")) - Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit())
        # Magnitude Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=3,error=None,unit=Unit("5 m^2")) - Measure(value=4,error=2,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.3,error=None,unit=Unit("5 m^2")) - Measure(value=0.4,error=0.2,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2")) - Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-3,error=None,unit=Unit("5 m^2")) - Measure(value=-4,error=2,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("5 m^2")) - Measure(value=4,error=2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=None,unit=Unit("5 m^2")) - Measure(value=0,error=2,unit=Unit())
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("5 m^2")) - Measure(value=0.4,error=0.2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=None,unit=Unit("5 m^2")) - Measure(value=0,error=0.2,unit=Unit())
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2")) - Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2")) - Measure(value=Decimal("0"),error=Decimal("20"),unit=Unit())
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("5 m^2")) - Measure(value=-4,error=2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-3,error=None,unit=Unit("5 m^2")) - Measure(value=0,error=2,unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            meas_meas_sub(
              x=3     , dx=None           , xu=Unit("5 m^2"), 
              y=0     , dy=0              , yu=Unit(), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("5 m^2"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("5 m^2")) - Measure(value=4,error=2,unit=Unit())
            # Value 2: Float
            meas_meas_sub(
              x=0.3   , dx=None           , xu=Unit("5 m^2"), 
              y=0     , dy=0              , yu=Unit(), 
              u=None  , du=0.05           , mu=None,
              v=None  , dv=None           , mv=None,
              unit=Unit("5 m^2"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit("5 m^2")) - Measure(value=0.4,error=0.2,unit=Unit())
            # Value 3: Decimal
            meas_meas_sub(
              x=Decimal("30") , dx=None           , xu=Unit("5 m^2"), 
              y=Decimal("0")  , dy=Decimal("0")   , yu=Unit(), 
              u=None          , du=Decimal("5")   , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("5 m^2"),
              implied=True)
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2")) - Measure(value=Decimal("40"),error=Decimal("20"),unit=Unit())
        # Convoluted Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=27,error=None,unit=Unit("\u00B0C")) - Measure(value=300,error=2,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=26.85,error=None,unit=Unit("\u00B0C")) - Measure(value=299.9,error=0.02,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C")) - Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-27,error=None,unit=Unit("\u00B0C")) - Measure(value=300,error=2,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("\u00B0C")) - Measure(value=300,error=2,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=27,error=None,unit=Unit("\u00B0C")) - Measure(value=0,error=2,unit=Unit())
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit("\u00B0C")) - Measure(value=300.0,error=0.02,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=26.85,error=None,unit=Unit("\u00B0C")) - Measure(value=0.0,error=0.02,unit=Unit())
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C")) - Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C")) - Measure(value=Decimal("0"),error=Decimal("0.02"),unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("\u00B0C")) - Measure(value=300,error=2,unit=Unit())
            meas_meas_sub(
              x=27            , dx=None           , xu=Unit("\u00B0C"), 
              y=0             , dy=0              , yu=Unit(), 
              u=None          , du=Decimal("0.5") , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("\u00B0C"),
              implied=True)
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit("\u00B0C")) - Measure(value=300.0,error=0.02,unit=Unit())
            meas_meas_sub(
              x=26.85         , dx=None           , xu=Unit("\u00B0C"), 
              y=0             , dy=0              , yu=Unit(), 
              u=None          , du=0.005          , mu=None,
              v=None          , dv=None           , mv=None,
              unit=Unit("\u00B0C"),
              implied=True)
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C")) - Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit())
            meas_meas_sub(
              x=Decimal("26.85")  , dx=None             , xu=Unit("\u00B0C"), 
              y=Decimal("0")      , dy=Decimal("0")     , yu=Unit(), 
              u=None              , du=Decimal("0.005") , mu=None,
              v=None              , dv=None             , mv=None,
              unit=Unit("\u00B0C"), 
              implied=True)
      # Unit - Unit
      if(True):
        # Same Units
        if(True):
          # Normal Units
          if(True):
            # Value 1: Int
            meas_meas_sub(
              x=4     , dx=None           , xu=Unit("cm"), 
              y=3     , dy=1              , yu=Unit("cm"), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=None           , mv=None,
              implied=True)
            # Value 2: Float
            meas_meas_sub(
              x=0.4   , dx=None           , xu=Unit("cm"), 
              y=0.3   , dy=0.1            , yu=Unit("cm"), 
              u=None  , du=0.05           , mu=None,
              v=None  , dv=None           , mv=None,
              implied=True)
            # Value 3: Decimal
            meas_meas_sub(
              x=Decimal("40") , dx=None           , xu=Unit("cm"), 
              y=Decimal("30") , dy=Decimal("10")  , yu=Unit("cm"), 
              u=None          , du=Decimal("5")   , mu=None,
              v=None          , dv=None           , mv=None,
              implied=True)
            # Value 4: Negative
            meas_meas_sub(
              x=-4    , dx=None           , xu=Unit("cm"), 
              y=-3    , dy=1              , yu=Unit("cm"), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=None           , mv=None,
              implied=True)
            # Value 5: Zero
            if(True):
              # Value 1: Int
              meas_meas_sub(
                x=0     , dx=None           , xu=Unit("cm"), 
                y=3     , dy=1              , yu=Unit("cm"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
              meas_meas_sub(
                x=4     , dx=None           , xu=Unit("cm"), 
                y=0     , dy=1              , yu=Unit("cm"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
              # Value 2: Float
              meas_meas_sub(
                x=0.0   , dx=None           , xu=Unit("cm"), 
                y=0.3   , dy=0.1            , yu=Unit("cm"), 
                u=None  , du=0.05           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
              meas_meas_sub(
                x=0.4   , dx=None           , xu=Unit("cm"), 
                y=0.0   , dy=0.1            , yu=Unit("cm"), 
                u=None  , du=0.05           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
              # Value 3: Decimal
              meas_meas_sub(
                x=Decimal("0")  , dx=None           , xu=Unit("cm"), 
                y=Decimal("30") , dy=Decimal("10")  , yu=Unit("cm"), 
                u=None          , du=Decimal("0.5") , mu=None,
                v=None          , dv=None           , mv=None,
                implied=True)
              meas_meas_sub(
                x=Decimal("40") , dx=None           , xu=Unit("cm"), 
                y=Decimal("0")  , dy=Decimal("10")  , yu=Unit("cm"), 
                u=None          , du=Decimal("5")   , mu=None,
                v=None          , dv=None           , mv=None,
                implied=True)
              # Value 4: Negative
              meas_meas_sub(
                x=0     , dx=None           , xu=Unit("cm"), 
                y=-3    , dy=1              , yu=Unit("cm"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
              meas_meas_sub(
                x=-4    , dx=None           , xu=Unit("cm"), 
                y=0     , dy=1              , yu=Unit("cm"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
          # Magnitude Units
          if(True):
            # Value 1: Int
            meas_meas_sub(
              x=4     , dx=None           , xu=Unit("5 m^2"), 
              y=3     , dy=1              , yu=Unit("5 m^2"), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=None           , mv=None,
              implied=True)
            # Value 2: Float
            meas_meas_sub(
              x=0.4   , dx=None           , xu=Unit("5 m^2"), 
              y=0.3   , dy=0.1            , yu=Unit("5 m^2"), 
              u=None  , du=0.05           , mu=None,
              v=None  , dv=None           , mv=None,
              implied=True)
            # Value 3: Decimal
            meas_meas_sub(
              x=Decimal("40") , dx=None           , xu=Unit("5 m^2"), 
              y=Decimal("30") , dy=Decimal("10")  , yu=Unit("5 m^2"), 
              u=None          , du=Decimal("5")   , mu=None,
              v=None          , dv=None           , mv=None,
              implied=True)
            # Value 4: Negative
            meas_meas_sub(
              x=-4    , dx=None           , xu=Unit("5 m^2"), 
              y=-3    , dy=1              , yu=Unit("5 m^2"), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=None           , mv=None,
              implied=True)
            # Value 5: Zero
            if(True):
              # Value 1: Int
              meas_meas_sub(
                x=0     , dx=None           , xu=Unit("5 m^2"), 
                y=3     , dy=1              , yu=Unit("5 m^2"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
              meas_meas_sub(
                x=4     , dx=None           , xu=Unit("5 m^2"), 
                y=0     , dy=1              , yu=Unit("5 m^2"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
              # Value 2: Float
              meas_meas_sub(
                x=0.0   , dx=None           , xu=Unit("5 m^2"), 
                y=0.3   , dy=0.1            , yu=Unit("5 m^2"), 
                u=None  , du=0.05           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
              meas_meas_sub(
                x=0.4   , dx=None           , xu=Unit("5 m^2"), 
                y=0.0   , dy=0.1            , yu=Unit("5 m^2"), 
                u=None  , du=0.05           , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
              # Value 3: Decimal
              meas_meas_sub(
                x=Decimal("0")  , dx=None           , xu=Unit("5 m^2"), 
                y=Decimal("30") , dy=Decimal("10")  , yu=Unit("5 m^2"), 
                u=None          , du=Decimal("0.5") , mu=None,
                v=None          , dv=None           , mv=None,
                implied=True)
              meas_meas_sub(
                x=Decimal("40") , dx=None           , xu=Unit("5 m^2"), 
                y=Decimal("0")  , dy=Decimal("10")  , yu=Unit("5 m^2"), 
                u=None          , du=Decimal("5")   , mu=None,
                v=None          , dv=None           , mv=None,
                implied=True)
              # Value 4: Negative
              meas_meas_sub(
                x=0     , dx=None           , xu=Unit("5 m^2"), 
                y=-3    , dy=1              , yu=Unit("5 m^2"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
              meas_meas_sub(
                x=-4    , dx=None           , xu=Unit("5 m^2"), 
                y=0     , dy=1              , yu=Unit("5 m^2"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=None           , mv=None,
                implied=True)
          # Convoluted Units
          if(True):
            # Value 1: Int
            meas_meas_sub(
              x=26                , dx=None           , xu=Unit("\u00B0C"), 
              y=27                , dy=1              , yu=Unit("\u00B0C"), 
              u=Decimal("299.85") , du=Decimal("0.5") , mu=None,
              v=Decimal("300.15") , dv=None           , mv=None,
              value = Decimal("299.85") - Decimal("300.15") - Decimal("273.85"),
              implied=True)
            # Value 2: Float
            meas_meas_sub(
              x=26.85 , dx=None   , xu=Unit("\u00B0C"), 
              y=26.85 , dy=0.01   , yu=Unit("\u00B0C"), 
              u=300.0 , du=0.005  , mu=None,
              v=300.0 , dv=None   , mv=None,
              value = 300.0 - 300.0 - 273.15,
              implied=True)
            # Value 3: Decimal
            meas_meas_sub(
              x=Decimal("26.85")  , dx=None             , xu=Unit("\u00B0C"), 
              y=Decimal("26.85")  , dy=Decimal("0.01")  , yu=Unit("\u00B0C"), 
              u=Decimal("300")    , du=Decimal("0.005") , mu=None,
              v=Decimal("300")    , dv=None             , mv=None,
              value = Decimal("300") - Decimal("300") - Decimal("273.15"),
              implied=True)
            # Value 4: Negative
            meas_meas_sub(
              x=-31               , dx=None           , xu=Unit("\u00B0C"), 
              y=-27               , dy=1              , yu=Unit("\u00B0C"), 
              u=Decimal("242.15") , du=Decimal("0.5") , mu=None,
              v=Decimal("246.15") , dv=None           , mv=None,
              value = Decimal("242.15") - Decimal("246.15") - Decimal("273.15"),
              implied=True)
            # Value 5: Zero
            if(True):
              # Int
              meas_meas_sub(
                x=27                , dx=None           , xu=Unit("\u00B0C"), 
                y=0                 , dy=1              , yu=Unit("\u00B0C"), 
                u=Decimal("300.15") , du=Decimal("0.5") , mu=None,
                v=Decimal("273.15") , dv=None           , mv=None,
                value = Decimal("300.15") - Decimal("273.15") - Decimal("273.15"),
                implied=True)
              # Float
              meas_meas_sub(
                x=26.85   , dx=None   , xu=Unit("\u00B0C"), 
                y=0.0     , dy=0.01   , yu=Unit("\u00B0C"), 
                u=300.0   , du=0.005  , mu=None,
                v=273.15  , dv=None   , mv=None,
                value = 300.0-273.15-273.15,
                implied=True)
              # Decimal
              meas_meas_sub(
                x=Decimal("26.85")  , dx=None             , xu=Unit("\u00B0C"), 
                y=Decimal("0")      , dy=Decimal("0.01")  , yu=Unit("\u00B0C"), 
                u=Decimal("300")    , du=Decimal("0.005") , mu=None,
                v=Decimal("273.15") , dv=None             , mv=None,
                value = Decimal("300") - Decimal("273.15") - Decimal("273.15"),
                implied=True)
        # Different Units
        if(True):
          # Normal Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=None,unit=Unit("s")) - Measure(value=3,error=1,unit=Unit("cm"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=None,unit=Unit("s")) - Measure(value=0.3,error=0.1,unit=Unit("cm"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=None,unit=Unit("s")) - Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=None,unit=Unit("s")) - Measure(value=-3,error=1,unit=Unit("cm"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=None,unit=Unit("s")) - Measure(value=0,error=1,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("s")) - Measure(value=3,error=1,unit=Unit("cm"))
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=None,unit=Unit("s")) - Measure(value=0,error=0.1,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("s")) - Measure(value=0.3,error=0.1,unit=Unit("cm"))
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=None,unit=Unit("s")) - Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("s")) - Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm"))
              # Value 4: Negative
              with pytest.raises(IncompatibleUnitException):
                Measure(value=-4,error=None,unit=Unit("s")) - Measure(value=0,error=1,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("s")) - Measure(value=-3,error=1,unit=Unit("cm"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("s")) - Measure(value=3,error=1,unit=Unit("cm"))
              meas_meas_sub(
                x=4     , dx=None           , xu=Unit("s"), 
                y=0     , dy=0              , yu=Unit("cm"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("s"),
                implied=True)
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("s")) - Measure(value=0.3,error=0.1,unit=Unit("cm"))
              meas_meas_sub(
                x=0.4   , dx=None           , xu=Unit("s"), 
                y=0     , dy=0              , yu=Unit("cm"), 
                u=None  , du=0.05           , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("s"),
                implied=True)
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("s")) - Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("cm"))
              meas_meas_sub(
                x=Decimal("40") , dx=None           , xu=Unit("s"), 
                y=Decimal("0")  , dy=Decimal("0")   , yu=Unit("cm"), 
                u=None          , du=Decimal("5")   , mu=None,
                v=None          , dv=None           , mv=None,
                unit=Unit("s"),
                implied=True)
          # Magnitude Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=None,unit=Unit("5 s")) - Measure(value=3,error=1,unit=Unit("5 m^2"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=None,unit=Unit("5 s")) - Measure(value=0.3,error=0.1,unit=Unit("5 m^2"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=None,unit=Unit("5 s")) - Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=None,unit=Unit("5 s")) - Measure(value=-3,error=1,unit=Unit("5 m^2"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=None,unit=Unit("5 s")) - Measure(value=0,error=1,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("5 s")) - Measure(value=3,error=1,unit=Unit("5 m^2"))
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=None,unit=Unit("5 s")) - Measure(value=0,error=0.1,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("5 s")) - Measure(value=0.3,error=0.1,unit=Unit("5 m^2"))
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=None,unit=Unit("5 s")) - Measure(value=Decimal("0"),error=Decimal("10"),unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("5 s")) - Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2"))
              # Value 4: Negative
              with pytest.raises(IncompatibleUnitException):
                Measure(value=-4,error=None,unit=Unit("5 s")) - Measure(value=0,error=1,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("5 s")) - Measure(value=-3,error=1,unit=Unit("5 m^2"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("5 s")) - Measure(value=3,error=1,unit=Unit("5 m^2"))
              meas_meas_sub(
                x=4     , dx=None           , xu=Unit("5 s"), 
                y=0     , dy=0              , yu=Unit("5 m^2"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("5 s"),
                implied=True)
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=None,unit=Unit("5 s")) - Measure(value=0.3,error=0.1,unit=Unit("5 m^2"))
              meas_meas_sub(
                x=0.4   , dx=None           , xu=Unit("5 s"), 
                y=0     , dy=0              , yu=Unit("5 m^2"), 
                u=None  , du=0.05           , mu=None,
                v=None  , dv=None           , mv=None,
                unit=Unit("5 s"),
                implied=True)
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("5 s")) - Measure(value=Decimal("30"),error=Decimal("10"),unit=Unit("5 m^2"))
              meas_meas_sub(
                x=Decimal("40") , dx=None           , xu=Unit("5 s"), 
                y=Decimal("0")  , dy=Decimal("0")   , yu=Unit("5 m^2"), 
                u=None          , du=Decimal("5")   , mu=None,
                v=None          , dv=None           , mv=None,
                unit=Unit("5 s"),
                implied=True)
          # Convoluted Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=27,error=1,unit=Unit("\u00B0C"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=2.9,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=26.85,error=0.01,unit=Unit("\u00B0C"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("3"),error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=-27,error=1,unit=Unit("\u00B0C"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=3,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=0,error=1,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=27,error=1,unit=Unit("\u00B0C"))
              # Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=3.0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=0.0,error=0.01,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=26.85,error=0.01,unit=Unit("\u00B0C"))
              # Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("3"),error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=Decimal("0"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=Decimal("26.85"),error=Decimal("0.01"),unit=Unit("\u00B0C"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=0,error=0,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("\u00B0C")) - Measure(value=0,error=0,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
              # Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=0.0,error=0.0,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=None,unit=Unit("\u00B0C")) - Measure(value=0.0,error=0.0,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
              # Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=Decimal("0"),error=Decimal("0"),unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C")) - Measure(value=Decimal("0"),error=Decimal("0.0"),unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
    # Measure (Implicit Error) - Measure (Implicit Error) = Measure (Implicit Error)
    if(True):
      # Unitless - Unitless
      if(True):
        # Value 1: Int
        meas_meas_sub(
          x=4     , dx=None           , xu=Unit(), 
          y=3     , dy=None           , yu=Unit(), 
          u=None  , du=Decimal("0.5") , mu=None,
          v=None  , dv=Decimal("0.5") , mv=None,
          implied=True)
        # Value 2: Float
        meas_meas_sub(
          x=0.4   , dx=None           , xu=Unit(), 
          y=0.3   , dy=None           , yu=Unit(), 
          u=None  , du=0.05           , mu=None,
          v=None  , dv=0.05           , mv=None,
          implied=True)
        # Value 3: Decimal
        meas_meas_sub(
          x=Decimal("40") , dx=None           , xu=Unit(), 
          y=Decimal("30") , dy=None           , yu=Unit(), 
          u=None          , du=Decimal("5")   , mu=None,
          v=None          , dv=Decimal("5")   , mv=None,
          implied=True)
        # Value 4: Negative
        meas_meas_sub(
          x=-4    , dx=None           , xu=Unit(), 
          y=-3    , dy=None           , yu=Unit(),
          u=None  , du=Decimal("0.5") , mu=None,
          v=None  , dv=Decimal("0.5") , mv=None,
          implied=True)
        # Value 5: Zero
        if(True):
          # Value 1: Int
          meas_meas_sub(
            x=4     , dx=None           , xu=Unit(), 
            y=0     , dy=None           , yu=Unit(), 
            u=None  , du=Decimal("0.5") , mu=None,
            v=None  , dv=Decimal("0.5") , mv=None,
            implied=True)
          # Value 2: Float
          meas_meas_sub(
            x=0.4   , dx=None           , xu=Unit(), 
            y=0.0   , dy=None           , yu=Unit(), 
            u=None  , du=0.05           , mu=None,
            v=None  , dv=0.05           , mv=None,
            implied=True)
          # Value 3: Decimal
          meas_meas_sub(
            x=Decimal("40") , dx=None           , xu=Unit(), 
            y=Decimal("0")  , dy=None           , yu=Unit(), 
            u=None          , du=Decimal("5")   , mu=None,
            v=None          , dv=Decimal("0.5") , mv=None,
            implied=True)
        # Preserve Inputs
        if(True):
          a = Measure(value=4,error=None) 
          b = Measure(value=3,error=None)
          c = a-b
          c = None
          assert a == Measure(value=4,error=None) 
          assert b == Measure(value=3,error=None)
      # Unitless - Unit
      if(True):
        # Normal Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=4,error=None,unit=Unit()) - Measure(value=3,error=None,unit=Unit("cm"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.4,error=None,unit=Unit()) - Measure(value=0.3,error=None,unit=Unit("cm"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("40"),error=None,unit=Unit()) - Measure(value=Decimal("30"),error=None,unit=Unit("cm"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-4,error=None,unit=Unit()) - Measure(value=-3,error=None,unit=Unit("cm"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=None,unit=Unit()) - Measure(value=0,error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=3,error=None,unit=Unit("cm"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=None,unit=Unit()) - Measure(value=0,error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=0.3,error=None,unit=Unit("cm"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=None,unit=Unit()) - Measure(value=Decimal("0"),error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) - Measure(value=Decimal("30"),error=None,unit=Unit("cm"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=None,unit=Unit()) - Measure(value=0,error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=-3,error=None,unit=Unit("cm"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=3,error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=None,unit=Unit()) - Measure(value=0,error=None,unit=Unit("cm"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=0.3,error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=None,unit=Unit()) - Measure(value=0.0,error=None,unit=Unit("cm"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) - Measure(value=Decimal("30"),error=None,unit=Unit("cm"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=None,unit=Unit()) - Measure(value=Decimal("0"),error=None,unit=Unit("cm"))
        # Magnitude Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=4,error=None,unit=Unit()) - Measure(value=3,error=None,unit=Unit("5 m^2"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.4,error=None,unit=Unit()) - Measure(value=0.3,error=None,unit=Unit("5 m^2"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("40"),error=None,unit=Unit()) - Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-4,error=None,unit=Unit()) - Measure(value=-3,error=None,unit=Unit("5 m^2"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=None,unit=Unit()) - Measure(value=0,error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=3,error=None,unit=Unit("5 m^2"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=None,unit=Unit()) - Measure(value=0,error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=0.3,error=None,unit=Unit("5 m^2"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=None,unit=Unit()) - Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) - Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=None,unit=Unit()) - Measure(value=0,error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=-3,error=None,unit=Unit("5 m^2"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=3,error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=None,unit=Unit()) - Measure(value=0,error=None,unit=Unit("5 m^2"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=0.3,error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=None,unit=Unit()) - Measure(value=0.0,error=None,unit=Unit("5 m^2"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) - Measure(value=Decimal("40"),error=None,unit=Unit("5 m^2"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=None,unit=Unit()) - Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2"))
        # Convoluted Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=300,error=None,unit=Unit()) - Measure(value=27,error=None,unit=Unit("\u00B0C"))
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=299.9,error=None,unit=Unit()) - Measure(value=26.85,error=None,unit=Unit("\u00B0C"))
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("300"),error=None,unit=Unit()) - Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C"))
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=300,error=None,unit=Unit()) - Measure(value=-27,error=None,unit=Unit("\u00B0C"))
          # Value 5: Zero Value, Something Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300,error=None,unit=Unit()) - Measure(value=0,error=None,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=27,error=None,unit=Unit("\u00B0C"))
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300.0,error=None,unit=Unit()) - Measure(value=0.0,error=None,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit()) - Measure(value=26.85,error=None,unit=Unit("\u00B0C"))
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("300"),error=None,unit=Unit()) - Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) - Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C"))
          # Value 5: Zero Value, Zero Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300,error=None,unit=Unit()) - Measure(value=0,error=None,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit()) - Measure(value=27,error=None,unit=Unit("\u00B0C"))
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=300.0,error=0.02,unit=Unit()) - Measure(value=0.0,error=None,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit()) - Measure(value=26.85,error=None,unit=Unit("\u00B0C"))
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("300"),error=Decimal("0.02"),unit=Unit()) - Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C"))
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit()) - Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C"))
      # Unit - Unitless
      if(True):
        # Normal Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=3,error=None,unit=Unit("cm")) - Measure(value=4,error=None,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.3,error=None,unit=Unit("cm")) - Measure(value=0.4,error=None,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("30"),error=None,unit=Unit("cm")) - Measure(value=Decimal("40"),error=None,unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-3,error=None,unit=Unit("cm")) - Measure(value=-4,error=None,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("cm")) - Measure(value=4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=None,unit=Unit("cm")) - Measure(value=0,error=None,unit=Unit())
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("cm")) - Measure(value=0.4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=None,unit=Unit("cm")) - Measure(value=0,error=None,unit=Unit())
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("cm")) - Measure(value=Decimal("40"),error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=None,unit=Unit("cm")) - Measure(value=Decimal("0"),error=None,unit=Unit())
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("cm")) - Measure(value=-4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-3,error=None,unit=Unit("cm")) - Measure(value=0,error=None,unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=None,unit=Unit("cm")) - Measure(value=0,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("cm")) - Measure(value=4,error=None,unit=Unit())
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=None,unit=Unit("cm")) - Measure(value=0.0,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit("cm")) - Measure(value=0.4,error=None,unit=Unit())
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=None,unit=Unit("cm")) - Measure(value=Decimal("0"),error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("cm")) - Measure(value=Decimal("40"),error=None,unit=Unit())
        # Magnitude Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=3,error=None,unit=Unit("5 m^2")) - Measure(value=4,error=None,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=0.3,error=None,unit=Unit("5 m^2")) - Measure(value=0.4,error=None,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2")) - Measure(value=Decimal("40"),error=None,unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-3,error=None,unit=Unit("5 m^2")) - Measure(value=-4,error=None,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("5 m^2")) - Measure(value=4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=None,unit=Unit("5 m^2")) - Measure(value=0,error=None,unit=Unit())
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("5 m^2")) - Measure(value=0.4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=None,unit=Unit("5 m^2")) - Measure(value=0,error=None,unit=Unit())
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2")) - Measure(value=Decimal("40"),error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2")) - Measure(value=Decimal("0"),error=None,unit=Unit())
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("5 m^2")) - Measure(value=-4,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-3,error=None,unit=Unit("5 m^2")) - Measure(value=0,error=None,unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=None,unit=Unit("5 m^2")) - Measure(value=0,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("5 m^2")) - Measure(value=4,error=None,unit=Unit())
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.3,error=None,unit=Unit("5 m^2")) - Measure(value=0.0,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit("5 m^2")) - Measure(value=0.4,error=None,unit=Unit())
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2")) - Measure(value=Decimal("0"),error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2")) - Measure(value=Decimal("40"),error=None,unit=Unit())
        # Convoluted Units
        if(True):
          # Value 1: Int
          with pytest.raises(IncompatibleUnitException):
            Measure(value=27,error=None,unit=Unit("\u00B0C")) - Measure(value=300,error=None,unit=Unit())
          # Value 2: Float
          with pytest.raises(IncompatibleUnitException):
            Measure(value=26.85,error=None,unit=Unit("\u00B0C")) - Measure(value=299.9,error=None,unit=Unit())
          # Value 3: Decimal
          with pytest.raises(IncompatibleUnitException):
            Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C")) - Measure(value=Decimal("300"),error=None,unit=Unit())
          # Value 4: Negative
          with pytest.raises(IncompatibleUnitException):
            Measure(value=-27,error=None,unit=Unit("\u00B0C")) - Measure(value=300,error=None,unit=Unit())
          # Value 5: Zero Value, Something Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("\u00B0C")) - Measure(value=300,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=27,error=None,unit=Unit("\u00B0C")) - Measure(value=0,error=None,unit=Unit())
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit("\u00B0C")) - Measure(value=300.0,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=26.85,error=None,unit=Unit("\u00B0C")) - Measure(value=0.0,error=None,unit=Unit())
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C")) - Measure(value=Decimal("300"),error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C")) - Measure(value=Decimal("0"),error=None,unit=Unit())
          # Value 5: Zero Value, Zero Error
          if(True):
            # Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0,error=None,unit=Unit("\u00B0C")) - Measure(value=300,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=27,error=None,unit=Unit("\u00B0C")) - Measure(value=0,error=None,unit=Unit())
            # Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.0,error=None,unit=Unit("\u00B0C")) - Measure(value=300.0,error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=26.85,error=None,unit=Unit("\u00B0C")) - Measure(value=0.0,error=None,unit=Unit())
            # Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C")) - Measure(value=Decimal("300"),error=None,unit=Unit())
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C")) - Measure(value=Decimal("0"),error=None,unit=Unit())
      # Unit - Unit
      if(True):
        # Same Units
        if(True):
          # Normal Units
          if(True):
            # Value 1: Int
            meas_meas_sub(
              x=4     , dx=None           , xu=Unit("cm"), 
              y=3     , dy=None           , yu=Unit("cm"), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              implied=True)
            # Value 2: Float
            meas_meas_sub(
              x=0.4   , dx=None           , xu=Unit("cm"), 
              y=0.3   , dy=None           , yu=Unit("cm"), 
              u=None  , du=0.05           , mu=None,
              v=None  , dv=0.05           , mv=None,
              implied=True)
            # Value 3: Decimal
            meas_meas_sub(
              x=Decimal("40") , dx=None           , xu=Unit("cm"), 
              y=Decimal("30") , dy=None           , yu=Unit("cm"), 
              u=None          , du=Decimal("5")   , mu=None,
              v=None          , dv=Decimal("5")   , mv=None,
              implied=True)
            # Value 4: Negative
            meas_meas_sub(
              x=-4    , dx=None           , xu=Unit("cm"), 
              y=-3    , dy=None           , yu=Unit("cm"), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              implied=True)
            # Value 5: Zero
            if(True):
              # Value 1: Int
              meas_meas_sub(
                x=0     , dx=None           , xu=Unit("cm"), 
                y=3     , dy=None           , yu=Unit("cm"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              meas_meas_sub(
                x=4     , dx=None           , xu=Unit("cm"), 
                y=0     , dy=None           , yu=Unit("cm"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              # Value 2: Float
              meas_meas_sub(
                x=0.0   , dx=None           , xu=Unit("cm"), 
                y=0.3   , dy=None           , yu=Unit("cm"), 
                u=None  , du=0.05           , mu=None,
                v=None  , dv=0.05           , mv=None,
                implied=True)
              meas_meas_sub(
                x=0.4   , dx=None           , xu=Unit("cm"), 
                y=0.0   , dy=None           , yu=Unit("cm"), 
                u=None  , du=0.05           , mu=None,
                v=None  , dv=0.05           , mv=None,
                implied=True)
              # Value 3: Decimal
              meas_meas_sub(
                x=Decimal("0")  , dx=None           , xu=Unit("cm"), 
                y=Decimal("30") , dy=None           , yu=Unit("cm"), 
                u=None          , du=Decimal("0.5") , mu=None,
                v=None          , dv=Decimal("5")   , mv=None,
                implied=True)
              meas_meas_sub(
                x=Decimal("40") , dx=None           , xu=Unit("cm"), 
                y=Decimal("0")  , dy=None           , yu=Unit("cm"), 
                u=None          , du=Decimal("5")   , mu=None,
                v=None          , dv=Decimal("0.5") , mv=None,
                implied=True)
              # Value 4: Negative
              meas_meas_sub(
                x=0     , dx=None           , xu=Unit("cm"), 
                y=-3    , dy=None           , yu=Unit("cm"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              meas_meas_sub(
                x=-4    , dx=None           , xu=Unit("cm"), 
                y=0     , dy=None           , yu=Unit("cm"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
          # Magnitude Units
          if(True):
            # Value 1: Int
            meas_meas_sub(
              x=4     , dx=None           , xu=Unit("5 m^2"), 
              y=3     , dy=None           , yu=Unit("5 m^2"), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              implied=True)
            # Value 2: Float
            meas_meas_sub(
              x=0.4   , dx=None           , xu=Unit("5 m^2"), 
              y=0.3   , dy=None           , yu=Unit("5 m^2"), 
              u=None  , du=0.05           , mu=None,
              v=None  , dv=0.05           , mv=None,
              implied=True)
            # Value 3: Decimal
            meas_meas_sub(
              x=Decimal("40") , dx=None           , xu=Unit("5 m^2"), 
              y=Decimal("30") , dy=None           , yu=Unit("5 m^2"), 
              u=None          , du=Decimal("5")   , mu=None,
              v=None          , dv=Decimal("5")   , mv=None,
              implied=True)
            # Value 4: Negative
            meas_meas_sub(
              x=-4    , dx=None           , xu=Unit("5 m^2"), 
              y=-3    , dy=None           , yu=Unit("5 m^2"), 
              u=None  , du=Decimal("0.5") , mu=None,
              v=None  , dv=Decimal("0.5") , mv=None,
              implied=True)
            # Value 5: Zero
            if(True):
              # Value 1: Int
              meas_meas_sub(
                x=0     , dx=None           , xu=Unit("5 m^2"), 
                y=3     , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              meas_meas_sub(
                x=4     , dx=None           , xu=Unit("5 m^2"), 
                y=0     , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              # Value 2: Float
              meas_meas_sub(
                x=0.0   , dx=None           , xu=Unit("5 m^2"), 
                y=0.3   , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=0.05           , mu=None,
                v=None  , dv=0.05           , mv=None,
                implied=True)
              meas_meas_sub(
                x=0.4   , dx=None           , xu=Unit("5 m^2"), 
                y=0.0   , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=0.05           , mu=None,
                v=None  , dv=0.05           , mv=None,
                implied=True)
              # Value 3: Decimal
              meas_meas_sub(
                x=Decimal("0")  , dx=None           , xu=Unit("5 m^2"), 
                y=Decimal("30") , dy=None           , yu=Unit("5 m^2"), 
                u=None          , du=Decimal("0.5") , mu=None,
                v=None          , dv=Decimal("5")   , mv=None,
                implied=True)
              meas_meas_sub(
                x=Decimal("40") , dx=None           , xu=Unit("5 m^2"), 
                y=Decimal("0")  , dy=None           , yu=Unit("5 m^2"), 
                u=None          , du=Decimal("5")   , mu=None,
                v=None          , dv=Decimal("0.5") , mv=None,
                implied=True)
              # Value 4: Negative
              meas_meas_sub(
                x=0     , dx=None           , xu=Unit("5 m^2"), 
                y=-3    , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
              meas_meas_sub(
                x=-4    , dx=None           , xu=Unit("5 m^2"), 
                y=0     , dy=None           , yu=Unit("5 m^2"), 
                u=None  , du=Decimal("0.5") , mu=None,
                v=None  , dv=Decimal("0.5") , mv=None,
                implied=True)
          # Convoluted Units
          if(True):
            # Value 1: Int
            meas_meas_sub(
              x=26                , dx=None           , xu=Unit("\u00B0C"), 
              y=27                , dy=None           , yu=Unit("\u00B0C"), 
              u=Decimal("299.85") , du=Decimal("0.5") , mu=None,
              v=Decimal("300.15") , dv=Decimal("0.5") , mv=None,
              value = Decimal("299.85") - Decimal("300.15") - Decimal("273.85"),
              implied=True)
            # Value 2: Float
            meas_meas_sub(
              x=26.85 , dx=None   , xu=Unit("\u00B0C"), 
              y=26.85 , dy=None   , yu=Unit("\u00B0C"), 
              u=300.0 , du=0.005  , mu=None,
              v=300.0 , dv=0.005  , mv=None,
              value = 300.0 - 300.0 - 273.15,
              implied=True)
            # Value 3: Decimal
            meas_meas_sub(
              x=Decimal("26.85")  , dx=None             , xu=Unit("\u00B0C"), 
              y=Decimal("26.85")  , dy=None             , yu=Unit("\u00B0C"), 
              u=Decimal("300")    , du=Decimal("0.005") , mu=None,
              v=Decimal("300")    , dv=Decimal("0.005") , mv=None,
              value = Decimal("300") - Decimal("300") - Decimal("273.15"),
              implied=True)
            # Value 4: Negative
            meas_meas_sub(
              x=-31               , dx=None           , xu=Unit("\u00B0C"), 
              y=-27               , dy=None           , yu=Unit("\u00B0C"), 
              u=Decimal("242.15") , du=Decimal("0.5") , mu=None,
              v=Decimal("246.15") , dv=Decimal("0.5") , mv=None,
              value = Decimal("242.15") - Decimal("246.15") - Decimal("273.15"),
              implied=True)
            # Value 5: Zero
            if(True):
              # Int
              meas_meas_sub(
                x=27                , dx=None           , xu=Unit("\u00B0C"), 
                y=0                 , dy=None           , yu=Unit("\u00B0C"), 
                u=Decimal("300.15") , du=Decimal("0.5") , mu=None,
                v=Decimal("273.15") , dv=Decimal("0.5") , mv=None,
                value = Decimal("300.15") - Decimal("273.15") - Decimal("273.15"),
                implied=True)
              # Float
              meas_meas_sub(
                x=26.85   , dx=None   , xu=Unit("\u00B0C"), 
                y=0.0     , dy=None   , yu=Unit("\u00B0C"), 
                u=300.0   , du=0.005  , mu=None,
                v=273.15  , dv=0.05   , mv=None,
                value = 300.0-273.15-273.15,
                implied=True)
              # Decimal
              meas_meas_sub(
                x=Decimal("26.85")  , dx=None             , xu=Unit("\u00B0C"), 
                y=Decimal("0")      , dy=None             , yu=Unit("\u00B0C"), 
                u=Decimal("300")    , du=Decimal("0.005") , mu=None,
                v=Decimal("273.15") , dv=Decimal("0.5")   , mv=None,
                value = Decimal("300") - Decimal("273.15") - Decimal("273.15"),
                implied=True)
        # Different Units
        if(True):
          # Normal Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=None,unit=Unit("s")) - Measure(value=3,error=None,unit=Unit("cm"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=None,unit=Unit("s")) - Measure(value=0.3,error=None,unit=Unit("cm"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=None,unit=Unit("s")) - Measure(value=Decimal("30"),error=None,unit=Unit("cm"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=None,unit=Unit("s")) - Measure(value=-3,error=None,unit=Unit("cm"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=None,unit=Unit("s")) - Measure(value=0,error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("s")) - Measure(value=3,error=None,unit=Unit("cm"))
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=None,unit=Unit("s")) - Measure(value=0,error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("s")) - Measure(value=0.3,error=None,unit=Unit("cm"))
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=None,unit=Unit("s")) - Measure(value=Decimal("0"),error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("s")) - Measure(value=Decimal("30"),error=None,unit=Unit("cm"))
              # Value 4: Negative
              with pytest.raises(IncompatibleUnitException):
                Measure(value=-4,error=None,unit=Unit("s")) - Measure(value=0,error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("s")) - Measure(value=-3,error=None,unit=Unit("cm"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("s")) - Measure(value=3,error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=None,unit=Unit("s")) - Measure(value=0,error=None,unit=Unit("cm"))
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=None,unit=Unit("s")) - Measure(value=0.3,error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=None,unit=Unit("s")) - Measure(value=0.0,error=None,unit=Unit("cm"))
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("s")) - Measure(value=Decimal("30"),error=None,unit=Unit("cm"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=None,unit=Unit("s")) - Measure(value=Decimal("0"),error=None,unit=Unit("cm"))
          # Magnitude Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=4,error=None,unit=Unit("5 s")) - Measure(value=3,error=None,unit=Unit("5 m^2"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=0.4,error=None,unit=Unit("5 s")) - Measure(value=0.3,error=None,unit=Unit("5 m^2"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("40"),error=None,unit=Unit("5 s")) - Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=-4,error=None,unit=Unit("5 s")) - Measure(value=-3,error=None,unit=Unit("5 m^2"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=None,unit=Unit("5 s")) - Measure(value=0,error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("5 s")) - Measure(value=3,error=None,unit=Unit("5 m^2"))
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=None,unit=Unit("5 s")) - Measure(value=0,error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("5 s")) - Measure(value=0.3,error=None,unit=Unit("5 m^2"))
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=None,unit=Unit("5 s")) - Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("5 s")) - Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2"))
              # Value 4: Negative
              with pytest.raises(IncompatibleUnitException):
                Measure(value=-4,error=None,unit=Unit("5 s")) - Measure(value=0,error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("5 s")) - Measure(value=-3,error=None,unit=Unit("5 m^2"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Value 1: Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("5 s")) - Measure(value=3,error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=4,error=None,unit=Unit("5 s")) - Measure(value=0,error=None,unit=Unit("5 m^2"))
              # Value 2: Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=None,unit=Unit("5 s")) - Measure(value=0.3,error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.4,error=None,unit=Unit("5 s")) - Measure(value=0.0,error=None,unit=Unit("5 m^2"))
              # Value 3: Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("5 s")) - Measure(value=Decimal("30"),error=None,unit=Unit("5 m^2"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("40"),error=None,unit=Unit("5 s")) - Measure(value=Decimal("0"),error=None,unit=Unit("5 m^2"))
          # Convoluted Units
          if(True):
            # Value 1: Int
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=27,error=None,unit=Unit("\u00B0C"))
            # Value 2: Float
            with pytest.raises(IncompatibleUnitException):
              Measure(value=2.9,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=26.85,error=None,unit=Unit("\u00B0C"))
            # Value 3: Decimal
            with pytest.raises(IncompatibleUnitException):
              Measure(value=Decimal("3"),error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C"))
            # Value 4: Negative
            with pytest.raises(IncompatibleUnitException):
              Measure(value=3,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=-27,error=None,unit=Unit("\u00B0C"))
            # Value 5: Zero Value, Something Error
            if(True):
              # Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=3,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=0,error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=27,error=None,unit=Unit("\u00B0C"))
              # Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=3.0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=0.0,error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=26.85,error=None,unit=Unit("\u00B0C"))
              # Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("3"),error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=Decimal("26.85"),error=None,unit=Unit("\u00B0C"))
            # Value 5: Zero Value, Zero Error
            if(True):
              # Int
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=0,error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0,error=None,unit=Unit("\u00B0C")) - Measure(value=0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
              # Float
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=0.0,error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=0.0,error=None,unit=Unit("\u00B0C")) - Measure(value=0.0,error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
              # Decimal
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS) - Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C"))
              with pytest.raises(IncompatibleUnitException):
                Measure(value=Decimal("0"),error=None,unit=Unit("\u00B0C")) - Measure(value=Decimal("0"),error=None,unit=Unit("pH"),definitions=Unit.CONCENTRATION_UNITS)
  
  