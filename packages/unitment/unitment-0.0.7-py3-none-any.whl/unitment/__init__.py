# Header
if(True):
  __doc__          = "The measure modules manages units and propagation of error."
  __version__      = "0.0.1"

  # Python Standard Imports
  import sys, os
  
  # Python Math Imports
  if(True):
    import math,cmath,random
    from decimal import *
    import decimal
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
  
  # Arg-Parse
  if (__name__ == "__main__"):
    import argparse
    
    # Create the parser
    try:
      arg_parse = argparse.ArgumentParser(description=description)
    except Exception:
      arg_parse = argparse.ArgumentParser(description="...")
    
    # Add the arguments
    arg_parse.add_argument('-l','--log',    action='store_true', help='Sets logging level to info.')
    arg_parse.add_argument('-d','--debug',  action='store_true', help='Sets logging level to debug.')
    arg_parse.add_argument('-t','--test',   action='store_true', help='Run Tests.')
    
    # Initiate Arguments
    main_args = arg_parse.parse_args()
    
    # Use Arguments
    if(main_args.log):
      log.setLevel(logging.INFO)
      # Log to Console
      log_console = logging.StreamHandler()
      log_console.setFormatter(logging.Formatter("{asctime} {levelname:<8}  {name:<50}  {message}", style="{"))
      log.addHandler(log_console)
    if(main_args.debug): 
      log.setLevel(logging.DEBUG)
      # Log to File
      log_file = logging.FileHandler(".temp.log.txt")
      log_file.setFormatter(logging.Formatter("{asctime} {levelname:<8}  {name:<50}  {message}", style="{"))
      log.addHandler(log_file)

# Utility Functions
def _is_(lam,*a,**k):
  try:
    lam(*a,**k)
    return True
  except:
    return False
def _try_(lam,*a,**k):
  try:
    return lam(*a,**k)
  except Exception:
    return x

# Typed Utility Functions
if(True):
  def _type_corrections_(*args):
    if(   all([isinstance(_,(Decimal,int,Measure)) for _ in args]) ): return [Decimal(_) if(not isinstance(_,Measure)) else _ for _ in args ]
    elif( any([isinstance(_,complex) for _ in args]) ):               return [complex(_) if(not isinstance(_,Measure)) else _ for _ in args]
    else:                                                             return [float(_)   if(not isinstance(_,Measure)) else _ for _ in args]
  def _sqrt_(x):
    if(isinstance(x,Decimal)): return x.sqrt()
    if(isinstance(x,complex)): return cmath.sqrt(x)
    else: return math.sqrt(x)
  def _ln_(x):
    if(isinstance(x,Decimal)): return x.ln()
    if(isinstance(x,complex)): return cmath.log(x)
    else: return math.log(x)
  def _sin_(x):
    if(isinstance(x,Decimal)): 
      def dec_sin(x):
        """
        Return the sine of x as measured in radians.
        Stolen Directly From Decimal Recipes
        """
        getcontext().prec += 2
        i, lasts, s, fact, num, sign = 1, 0, x, 1, x, 1
        while s != lasts:
            lasts = s
            i += 2
            fact *= i * (i-1)
            num *= x * x
            sign *= -1
            s += num / fact * sign
        getcontext().prec -= 2
        return +s
      return dec_sin(x)
    if(isinstance(x,complex)): return cmath.sin(x)
    else: return math.sin(x)
  def _cos_(x):
    if(isinstance(x,Decimal)): 
      def dec_cos(x):
        """
        Return the cosine of x as measured in radians.
        Stolen Directly From Decimal Recipes
        """
        getcontext().prec += 2
        i, lasts, s, fact, num, sign = 0, 0, 1, 1, 1, 1
        while s != lasts:
            lasts = s
            i += 2
            fact *= i * (i-1)
            num *= x * x
            sign *= -1
            s += num / fact * sign
        getcontext().prec -= 2
        return +s
      return dec_cos(x)
    if(isinstance(x,complex)): return cmath.cos(x)
    else: return math.cos(x)
  def _ceil_(x):
    if(isinstance(x,Decimal)): return x.to_integral_exact(rounding=ROUND_CEILING)
    if(isinstance(x,complex)): return cmath.ceil(x)
    else: return math.ceil(x)
  def _floor_(x):
    if(isinstance(x,Decimal)): return x.to_integral_exact(rounding=ROUND_FLOOR)
    if(isinstance(x,complex)): return cmath.floor(x)
    else: return math.floor(x)
  def _pi_():
    """
    Compute Pi to the current precision.
    Stolen Directly From Decimal Recipes
    """
    getcontext().prec += 2
    three = Decimal(3)
    lasts, t, s, n, na, d, da = 0, three, 3, 1, 0, 0, 24
    while s != lasts:
      lasts = s
      n, na = n+na, na+8
      d, da = d+da, da+32
      t = (t * n) / d
      s += t
    getcontext().prec -= 2
    return +s
  

# Exceptions
class UnitException(Exception):
  pass
class IncompatibleUnitException(UnitException):
  """Incompatible Units. 
  
  Caused by using different non-convertable units where identical base-units are required:
  
  - Impossible Conversions,            e.g: Measure("12 mg").convert("uL")
  - Approximation Operation,           e.g: Measure("12 mg").approx(Measure("12 uL"))
  - Relational Operators,              e.g: Measure("12 mg") <,<=,>=,> Measure("12 uL")
  - Addition & Subtraction,            e.g: Measure("12 mg") +,- Measure("12 uL")
  - Non-Dimensionless Exponents,       e.g: Measure("12 mg")**Measure("12 mg")
  - Non-Dimensionless Logarithm Bases, e.g: Measure.log(Measure("12 mg"),base=Measure("2 mg"))
  - Non-Dimensionless Trigonometry,    e.g: Measure.sin(Measure("12 mg"))
  
  """
  pass
class AmbiguousUnitException(UnitException):
  """Ambiguous Units. 
  
  Usually caused by using non-simplified function-units:
  For example:
    What is 8 degC m? Is it  4m * 2degC  or  2m * 4degC?
    For Non-function units this is irrelevant.
    For function-units the conversion creates ambiguouty. 
  
  """

# Unit and Measure To-Do List
#  - Doc Strings
#  - More Math Functions
#  - Regex Instead of Decimal
#  - Allow exceptions for zero relations
#  - Test NumPy
#

@log_this
class Unit:
  '''
    DESCRIPTION:
      This class helps define a unit in terms of other units (strings). 
      The units are stored as a magnitude with lists of symbols.
    ARGUMENTS/PROPERTIES: Generally, parse a string.
      magnitude     ?= Dec: Multiplier generally used for scaling, but part of the unit (e.g. "10^6 $" != "$")
      symbols       ?= list[(str,Dec)]: List of Symbols sub-units that the unit is composed of with exponents.
      definitions   ?= dict{"unit":(magnitude,(("base",exp),), None)}: Definition of Base Units 
    PROPERTIES:
      None
    NOTABLE ERRORS:
      TypeError: Symbols must be List of Strings
      TypeError: Magnitude must be number greater than zero.
    EXAMPLE:
      Unit("someunit")
      Unit(symbols)
      Unit(numerators,denominators)
      Unit(numerators,denominators,magnitude)
  '''
  
  # Unit Definitions
  if(True):
    # Note: The Minimal Unit Definition is {"unit":(magnitude,(("base",exp),), None)} e.g. {"unit":(1,(("base",1),), None)}
    
    # Note: For Conversions
    # FORWARD means to base units
    # REVERSE means from base units.
    
    
    
    # Unit Conversion Selectors and Functions 
    def DEGREES_CELSIUS_SELECTOR(exponent):
      if(exponent == 0): return (lambda x:x,lambda x:x)
      # Degrees Celsius Functions
      def NUMERATOR_FORWARD_CELSIUS(val):
        # Kelvin = degC + abs_zero
        val,abs_zero =_type_corrections_(val,Decimal("273.15"))
        return val+abs_zero
      def NUMERATOR_REVERSE_CELSIUS(val):
        val,abs_zero =_type_corrections_(val,Decimal("273.15"))
        return val-abs_zero
      def DENOMINATOR_FORWARD_CELSIUS(val):
        return val
      def DENOMINATOR_REVERSE_CELSIUS(val):
        return val
      # Select & Return Correct Function
      if(exponent == 1):  return (NUMERATOR_FORWARD_CELSIUS,NUMERATOR_REVERSE_CELSIUS)
      if(exponent == -1): return (DENOMINATOR_FORWARD_CELSIUS,DENOMINATOR_REVERSE_CELSIUS)
      else:
        raise AmbiguousUnitException(f"Failed to Decompose: Exponent of \u00B0C != 1,0,-1. Cannot Deconvolute.")
    def DEGREES_FAHRENHEIT_SELECTOR(exponent):
      if(exponent == 0): return (lambda x:x,lambda x:x)
      # Degrees Fahrenheit Functions
      def NUMERATOR_FORWARD_FAHRENHEIT(val):
        val,rel_zero,abs_zero,scale =_type_corrections_(val,Decimal("32"),Decimal("273.15"),Decimal(5)/Decimal(9))
        return (val-rel_zero)*scale + abs_zero
      def NUMERATOR_REVERSE_FAHRENHEIT(val):
        val,rel_zero,abs_zero,scale =_type_corrections_(val,Decimal("32"),Decimal("273.15"),Decimal(9)/Decimal(5))
        return (val-abs_zero)*scale + rel_zero
      def DENOMINATOR_FORWARD_FAHRENHEIT(val):
        val,scale =_type_corrections_(val,Decimal(9)/Decimal(5))
        return val*scale
      def DENOMINATOR_REVERSE_FAHRENHEIT(val):
        val,scale =_type_corrections_(val,Decimal(5)/Decimal(9))
        return val*scale
      # Select & Return Correct Function
      if(exponent == 1):  return (NUMERATOR_FORWARD_FAHRENHEIT,NUMERATOR_REVERSE_FAHRENHEIT)
      if(exponent == -1): return (DENOMINATOR_FORWARD_FAHRENHEIT,DENOMINATOR_REVERSE_FAHRENHEIT)
      else:
        raise AmbiguousUnitException(f"Failed to Decompose: Exponent of \u00B0F != 1,0,-1. Cannot Deconvolute.")
    def PH_SELECTOR(exponent):
      def NUMERATOR_FORWARD_PH(val):
        return 10**(-1*val) * (10**3)
      def NUMERATOR_REVERSE_PH(val):
        return -1*_log_(val / 10**3)
      def DENOMINATOR_FORWARD_PH(val):
        return val
      def DENOMINATOR_REVERSE_PH(val):
        return val
      if(exponent == 1):  return (NUMERATOR_FORWARD_PH,NUMERATOR_REVERSE_PH)
      if(exponent == -1): return (DENOMINATOR_FORWARD_PH,DENOMINATOR_REVERSE_PH)
      else:
        raise AmbiguousUnitException(f"Failed to Decompose: Exponent of pH != 1,0,-1. Cannot Deconvolute.")
        
      
    # Metric Definitions 
    _PREFIXES_ = {
      'Y':(Decimal('1e23') ,'yotta'),
      'Z':(Decimal('1e21') ,'zetta'),
      'E':(Decimal('1e18') ,'exa'  ),
      'P':(Decimal('1e15') ,'peta' ),
      'T':(Decimal('1e12') ,'tera' ),
      'G':(Decimal('1e9')  ,'giga' ),
      'M':(Decimal('1e6')  ,'mega' ),
      'k':(Decimal('1e3')  ,'kilo' ),
      'm':(Decimal('1e-3') ,'milli'),
      'u':(Decimal('1e-6') ,'micro'),
      '\u03BC':(Decimal('1e-6') ,'micro'),
      'n':(Decimal('1e-9') ,'nano' ),
      'p':(Decimal('1e-12'),'pico' ),
      'f':(Decimal('1e-15'),'femto'),
      'a':(Decimal('1e-18'),'atto' ),
      'z':(Decimal('1e-21'),'zepto'),
      'y':(Decimal('1e-23'),'yocto')
      }
    _METRICBASE_ = {
      # Symbol  Text      Dimension
      'm'   : ('Meter',   'Distance'            ),
      's'   : ('Second',  'Time'                ),
      'mol' : ('Mole',    'Amount'              ),
      'A'   : ('Ampere',  'Electrical Current'  ),
      'K'   : ('Kelvin',  'Temperature'         ),
      'cd'  : ('Candela', 'Luminous Intensity'  ),
      'g'   : ('gram',    'Mass'                ),
      }
    _DERIVED_ = {
      # Symbol Mult                                     Base-Symbol                                     Function                    Text                  Dimension       
      'Hz'  : ( Decimal(1),                             (('s',-1),),                                    None,                       'Hertz',              'Frequency'             ),
      'rad' : ( Decimal(1),                             (('m',1),('m',-1)),                             None,                       'Radians',            'Angle'                 ),
      'sr'  : ( Decimal(1),                             (('m',2),('m',-2)),                             None,                       'Steradian',          'Solid Angle'           ),
      'N'   : ( Decimal(1),                             (('kg',1),('m',1),('s',-2)),                    None,                       'Newton',             'Force'                 ),
      'Pa'  : ( Decimal(1),                             (('kg',1),('m',-1),('s',-2)),                   None,                       'Pascal',             'Pressure'              ),
      'J'   : ( Decimal(1),                             (('kg',1),('m',2),('s',-2)),                    None,                       'Joule',              'Energy'                ),
      'W'   : ( Decimal(1),                             (('kg',1),('m',2),('s',-3)),                    None,                       'Watt',               'Power'                 ),
      'C'   : ( Decimal(1),                             (('s',1),('A',1)),                              None,                       'Coulomb',            'Electric Charge'       ),
      'V'   : ( Decimal(1),                             (('kg',1),('m',2),('s',-3),('A',-1)),           None,                       'Volt',               'Potential Energy'      ),
      'F'   : ( Decimal(1),                             (('s',4),('A',2),('kg',-1),('m',-2)),           None,                       'Farad',              'Electric Capacitance'  ),
      'Ω'   : ( Decimal(1),                             (('kg',1),('m',2),('s',-3),('A',-2)),           None,                       'Ohm',                'Electric Resistance'   ),
      'S'   : ( Decimal(1),                             (('s',3),('A',2),('kg',-1),('m',-2)),           None,                       'Siemens',            'Electric Conductance'  ),
      'Wb'  : ( Decimal(1),                             (('kg',1),('m',2),('s',-2),('A',-1)),           None,                       'Weber',              'Magnetic Flux'         ),
      'T'   : ( Decimal(1),                             (('kg',1),('s',-2),('A',-1)),                   None,                       'Tesla',              'Magnetic Inductance'   ),
      'G'   : ( Decimal('1e-4'),                        (('kg',1),('s',-2),('A',-1)),                   None,                       'Gauss',              'Magnetic Inductance'   ),
      'H'   : ( Decimal(1),                             (('kg',1),('m',2),('s',-2),('A',-2)),           None,                       'Henry',              'Electric Inductance'   ),
      'lm'  : ( Decimal(1),                             (('cd',1),),                                    None,                       'Lumen',              'Luminous Flux'         ),
      'lx'  : ( Decimal(1),                             (('cd',1),('m',-2)),                            None,                       'Lux',                'Irradiance'            ),
      'Bq'  : ( Decimal(1),                             (('s',-1),),                                    None,                       'Becquerel',          'Radioactivity'         ),
      'Gy'  : ( Decimal(1),                             (('m',2),('s',-2)),                             None,                       'Gray',               'Radiation Dose'        ),
      'rad' : ( Decimal('0.01'),                        (('m',2),('s',-2)),                             None,                       'Rad',                'Radiation Dose'        ),
      'Sv'  : ( Decimal(1),                             (('m',2),('s',-2)),                             None,                       'Sievert',            'Radiation Dose'        ),
      'kat' : ( Decimal(1),                             (('mol',1),('s',-1)),                           None,                       'Katal',              'Catalytic Activity'    ),
      'sec' : ( Decimal(1),                             (('s',1),),                                     None,                       'Second',             'Time'                  ),
      'U'   : ( Decimal(1)/Decimal(60)*Decimal('1e-6'), (('mol',1),('s',-1)),                           None,                       'Enzyme Unit',        'Catalytic Activity'    ),
      'ha'  : ( Decimal('1e4'),                         (('m',2),),                                     None,                       'Hectare',            'Area'                  ),
      'M'   : ( Decimal('1e3'),                         (('mol',1),('m',-3)),                           None,                       'Molar',              'Concentration'         ),
      'L'   : ( Decimal('1e-3'),                        (('m',3),),                                     None,                       'Liter',              'Volume'                ),
      'l'   : ( Decimal('1e-3'),                        (('m',3),),                                     None,                       'Liter',              'Volume'                ),
      't'   : ( Decimal('1e3'),                         (('kg',1),),                                    None,                       'Tonne',              'Mass'                  ),
      'Da'  : ( Decimal('1.6605390666050e-27'),         (('kg',1),),                                    None,                       'Dalton',             'Mass'                  ),
      'eV'  : ( Decimal('1.602176634e-19'),             (('kg',1),('m',2),('s',-2)),                    None,                       'Electronvolt',       'Energy'                ),
      "\u00B0"  : (_pi_()/Decimal('180'),               (),                                             None,                       'Degrees',            'Angle' ),
      "deg"     : (_pi_()/Decimal('180'),               (),                                             None,                       'Degrees',            'Angle' ),
      "\u00B0C" : (Decimal(1),                          (('K',1),),                                     DEGREES_CELSIUS_SELECTOR,   'Celsius',            'Temperature' ),
      "degC"    : (Decimal(1),                          (('K',1),),                                     DEGREES_CELSIUS_SELECTOR,   'Celsius',            'Temperature' ),
      "\u2103"  : (Decimal(1),                          (('K',1),),                                     DEGREES_CELSIUS_SELECTOR,   'Celsius',            'Temperature' ),
      }
    _DERIVED_NO_PREFIX_={
      # Symbol Mult                                     Base-Symbol                                     Function                    Text                  Dimension       
      'au'      : (Decimal(149597870700),               (('m',1),),                                     None,                       'Astronomical Unit',  'Distance'    ),
      'Å'       : (Decimal('1e-10'),                    (('m',1),),                                     None,                       'Ångstrom',           'Distance'    ),
      'y'       : ( Decimal('31556952'),                (('s',1),),                                     None,                       'Year',               'Time'        ),
      'w'       : ( Decimal(604800),                    (('s',1),),                                     None,                       'Week',               'Time'        ),
      'hr'      : ( Decimal(3600),                      (('s',1),),                                     None,                       'Hour',               'Time'        ),
      'h'       : ( Decimal(3600),                      (('s',1),),                                     None,                       'Hour',               'Time'        ),
      'day'     : ( Decimal(86400),                     (('s',1),),                                     None,                       'Day',                'Time'        ),
      'd'       : ( Decimal(86400),                     (('s',1),),                                     None,                       'Day',                'Time'        ),
      'amu'     : ( Decimal('1.6605390666050e-27'),     (('kg',1),),                                    None,                       'Atomic Mass Unit',   'Mass'        ),
      'min'     : (Decimal('60'),                       (('s',1),),                                     None,                       'Minutes',            'Time'        ),
      'cm'      : (Decimal('0.01'),                     (('m',1),),                                     None,                       'Centimeter',         'Distance'    ),
      # dm decimeter
      }
    
    METRIC = {}
    # Define Prefix-Derived Units
    for u,t in _DERIVED_.items():
      METRIC[u] = (t[0],t[1],t[2],t[3],t[4])
      for p,m in _PREFIXES_.items():
        METRIC[p+u] = (t[0]*m[0],t[1],t[2],f"{m[1]}-{t[3]}",t[4])
    # Define Prefix-Base-Metric
    for u in _METRICBASE_.keys():
      if(u != "g"):
        METRIC[u] = (Decimal(1),((u,Decimal(1)),),None,_METRICBASE_[u][0],_METRICBASE_[u][1])
        for p,m in _PREFIXES_.items():
          METRIC[p+u] = (1*m[0],((u,1),),None,f"{m[1]}-{_METRICBASE_[u][0]}",_METRICBASE_[u][1])
      else: 
        METRIC[u] = (Decimal("1e-3"),(("kg",1),),None,_METRICBASE_[u][0],_METRICBASE_[u][1])
        for p,m in _PREFIXES_.items():
          METRIC[p+u] = (Decimal("1e-3")*m[0],(("kg",1),),None,f"{m[1]}-{_METRICBASE_[u][0]}",_METRICBASE_[u][1])
    # Define Non-Prefixed-Derived
    for u,t in _DERIVED_NO_PREFIX_.items():
      METRIC[u] = (t[0],t[1],t[2],t[3],t[4])
    
    # Alternative or Uncommon Definitions
    PRESSURE_UNITS = {
      # Symbol Mult                                     Base-Symbol                                     Function                    Text                       Dimension       
      'Pa'      : ( Decimal('1'),                       (('kg',1),('m',-1),('s',-2)),                   None,                       'Pascal',                  'Pressure'              ),
      'bar'     : ( Decimal('1e5'),                     (('kg',1),('m',-1),('s',-2)),                   None,                       'Bar',                     'Pressure'              ),
      'atm'     : ( Decimal('98066.5'),                 (('kg',1),('m',-1),('s',-2)),                   None,                       'Standard Atmosphere',     'Pressure'              ),
      'at'      : ( Decimal('101325'),                  (('kg',1),('m',-1),('s',-2)),                   None,                       'Technical Atmosphere',    'Pressure'              ),
      'psi'     : ( Decimal('6894.72971416676769245'),  (('kg',1),('m',-1),('s',-2)),                   None,                       'Pressure Per Square Inch','Pressure'              ),
      
      'torr'    : ( Decimal('0.0075006'),               (('kg',1),('m',-1),('s',-2)),                   None,                       'Torr',                    'Pressure'              ),
      'mmHg'    : ( Decimal('133.333'),                 (('kg',1),('m',-1),('s',-2)),                   None,                       'mmHg',                    'Pressure'              ),
      'inHg'    : ( Decimal('3386.400'),                (('kg',1),('m',-1),('s',-2)),                   None,                       'inHg',                    'Pressure'              ),
      }
    
    IMPERIAL_UNITS = {
      # Symbol Mult                                     Base-Symbol                                     Function                    Text                  Dimension       
      "cups"    : (Decimal("2.365882365e-4"),           (('m',3),),                                     None,                        'cups',              'Volume'      ),
      "cup"     : (Decimal("2.365882365e-4"),           (('m',3),),                                     None,                        'cup',               'Volume'      ),
      "Tb"      : (Decimal("14.7867647821e-6"),         (('m',3),),                                     None,                        'Tablespoon',        'Volume'      ),
      "Tbls"    : (Decimal("14.7867647821e-6"),         (('m',3),),                                     None,                        'Tablespoon',        'Volume'      ),
      "tbsp"    : (Decimal("14.7867647821e-6"),         (('m',3),),                                     None,                        'Tablespoon',        'Volume'      ),
      "tsp"     : (Decimal("4.9289215940186E-6"),       (('m',3),),                                     None,                        'Teaspoons',         'Volume'      ),
      "gal"     : (Decimal("0.0037854117840007"),       (('m',3),),                                     None,                        'Gallon',            'Volume'      ),
      
      'lbf'     : ( Decimal("4.4482216152605"),         (('kg',1),('m',1),('s',-2)),                    None,                        'Pound Force',       'Force'       ),
      
      "oz"      : (Decimal("0.028349523125"),           (('kg',1),),                                    None,                        'Ounce',             'Mass'        ),
      "lb"      : (Decimal("0.45359237"),               (('kg',1),),                                    None,                        'Pound',             'Mass'        ),
      "t"       : (Decimal("1016.0469088"),             (('kg',1),),                                    None,                        'ton',               'Mass'        ),
      
      "qt"      : (Decimal("9.46352946e-4"),            (('m',3),),                                     None,                        'Quart',             'Volume'      ),
      "pt"      : (Decimal("4.73176473e-4"),            (('m',3),),                                     None,                        'Pint',              'Volume'      ),
      "fl oz"   : (Decimal("2.95735e-5"),               (('m',3),),                                     None,                        'Fluid Ounces',      'Volume'      ),
      
      "sq mi"   : (Decimal("2589988.110336"),           (('m',2),),                                     None,                        'Square Mile',       'Distance'    ),
      
      "mil"     : (Decimal("1609.344"),                 (('m',1),),                                     None,                        'Mile',              'Distance'    ),
      "mi"      : (Decimal("1609.344"),                 (('m',1),),                                     None,                        'Mile',              'Distance'    ),
      "yd"      : (Decimal("0.9144"),                   (('m',1),),                                     None,                        'Yard',              'Distance'    ),
      "ft"      : (Decimal("1200")/Decimal("3937"),     (('m',1),),                                     None,                        'Feet',              'Distance'    ),
      "in"      : (Decimal("100")/Decimal("3937"),      (('m',1),),                                     None,                        'Inch',              'Distance'    ),
      
      
      "degF"    : (Decimal(1),                          (('K',1),),                                     DEGREES_FAHRENHEIT_SELECTOR, 'Fahrenheit',        'Temperature' ),
      "\u00B0F" : (Decimal(1),                          (('K',1),),                                     DEGREES_FAHRENHEIT_SELECTOR, 'Fahrenheit',        'Temperature' ),
      }
    
    CONCENTRATION_UNITS ={
      # Symbol Mult                                     Base-Symbol                                     Function                    Text                  Dimension       
      "pH"      : (Decimal('1'),                      (('mol',1),('m',-3)),                           PH_SELECTOR,                'pH',                 'Concentration'),
      
      #"% (w/v)" == g/100mL
      }
    
    
  
  # Initialization 
  __slots__ = ("_symbols_","_magnitude_","_conversion_","_definitions_","_decomposed_")
  def __new__(cls,*args,numerators=(),denominators=(),symbols=(),magnitude=1,definitions=None,defs=None,**kargs):
    # Create all None Instance 
    self = super().__new__(cls)
    for slot in self.__slots__: setattr(self,slot,None)
    
    # Load Unit
    # Initialize Symbol Associated Variables
    numerators     = Unit._fix_sym_(numerators)
    denominators   = Unit._fix_sym_(denominators)
    self._symbols_ = Unit._exponent_form_(numerators,denominators)
    if(symbols != ()): self._symbols_ = Unit._fix_sym_(symbols)
    
    # Initialize Magnitude Associated Variables
    self._magnitude_  = self._fix_mag_(magnitude)
    self._conversion_ = None
    
    # Optional Implicit Arguments
    if(len(args)!=0):
      # Organize Inputs
      args = [Decimal(_) if Unit._is_number_(_) else _ for _ in args]
      list_args = [_ for _ in args if(isinstance(_,(list,tuple)))]
      str_arg   = [_ for _ in args if isinstance(_,str)]
      dict_args = [_ for _ in args if isinstance(_,dict)]
      dec_args  = [_ for _ in args if isinstance(_,Decimal)] # To-Do change to non-measure Numbers
      unit_args = [_ for _ in args if isinstance(_,self.__class__)]
      meas_args = [_ for _ in args if isinstance(_,Measure)]
      
      # Error Out
      if(len(args)-len(dict_args)        > 3): raise TypeError("Unexpected Input (1): Ambiguous or Conflicting Arguments.")
      if(len(list_args)                  > 2): raise TypeError("Unexpected Input (2): Ambiguous or Conflicting Arguments.")
      if(len(dec_args)                   > 1): raise TypeError("Unexpected Input (3): Ambiguous or Conflicting Arguments.")
      if(len(str_arg)                    > 1): raise TypeError("Unexpected Input (4): Ambiguous or Conflicting Arguments.")
      if(len(unit_args) + len(meas_args) > 1): raise TypeError("Unexpected Input (5): Ambiguous or Conflicting Arguments.")
      
      # String Input
      if(len(str_arg) > 0): 
        if(self._symbols_ != ()): raise TypeError("Unexpected Input (6): Ambiguous or Conflicting Arguments.")
        self._parse_(str_arg[0])
      
      # List Input
      if(len(list_args) > 0):
        if(self._symbols_ != ()): raise TypeError("Unexpected Input (7): Ambiguous or Conflicting Arguments.")
        if(len(list_args) == 1):
          self._symbols_ = Unit._fix_sym_(list_args[0])
        elif(len(list_args) == 2):
          numerators     = Unit._fix_sym_(list_args[0])
          denominators   = Unit._fix_sym_(list_args[1])
          self._symbols_ = Unit._exponent_form_(numerators,denominators)
      
      # Decimal Input
      if(len(dec_args) > 0):
        if(self._magnitude_ != 1): raise TypeError("Unexpected Input (8): Ambiguous or Conflicting Arguments.")
        self._magnitude_ = self._fix_mag_(dec_args[0])
      
      # Unit Input
      if(len(unit_args) > 0):
        if(self._symbols_ != () or self._magnitude_ != 1): raise TypeError("Unexpected Input (9): Ambiguous or Conflicting Arguments.")
        self._symbols_     = args[0]._symbols_
        self._magnitude_   = args[0]._magnitude_
        self._definitions_ = args[0]._definitions_
        #for slot in self.__slots__: setattr(self, slot,getattr(args[0], slot))
      
      # Measure Input
      if(len(meas_args) > 0):
        self = args[0].value * args[0].unit
      
      # Cast Fail
      if(len(args)-len(dict_args) == 1):
        arg = [_ for _ in args if not isinstance(_,dict)][0]
        invalid_type = not isinstance(arg,(list,tuple,str,self.__class__,type(None),Number))
        if(invalid_type): raise ValueError("Could not cast as Unit: "+repr(arg))
    
    # Optional Explicits (All Protected)
    if(len(kargs)!=0):
      for key in kargs.keys():
        if(key in self.__slots__):
          setattr(self,key,kargs[key]) 
    
    # After Unit Load
    # Set Unit Definitions (Note: Default Metric. Note: Adds new defs to nested unit.)
    def_args     = [ _ for _ in args if isinstance(_,dict)]+[definitions,defs,self._definitions_]
    self._definitions_ = self._fix_def_(*def_args)
    # Decompose (Note: _base_units_ prevents recursion.)
    if("_base_units_" not in kargs.keys() or not kargs["_base_units_"]):
      self._decomposed_ = self.decompose()
    else:
      self._decomposed_ = self
    # Return Instance
    return self
    
  # Immutable Copies
  def __copy__(self): return self
  def __deepcopy__(self, memo): return self
  
  # Unit Converter Tools
  if(True):
    # Unit Decomposition
    def decompose(self,*args,allow_conversion=True,_base_units_=False,definitions=None,defs=None):
      '''
      DESCRIPTION:
        Converts units to their base units with magnitudes and conversion factors as defined by the definitions property.
      ARGUMENTS:
        None.
      KNOWN ERRORS:
        N/A
      RETURN:
        Unit
      '''
      
      # No New Info? -> Quick Exit
      if(self._decomposed_ != None and definitions==None and defs==None): return self._decomposed_
      # Utility Function
      def eq_func(f1,f2): return f1.__code__.co_code == f2.__code__.co_code
      # Initialization
      magnitude_modifier = 1
      units,exponents = [],[]
      conversion = self._conversion_
      # Get Definitions
      def_args     = [ _ for _ in args if isinstance(_,dict)]+[definitions,defs,self._definitions_]
      _definitions_ = self._fix_def_(*def_args)
      _definitions_ = _definitions_ if(_definitions_!=None) else self.METRIC
      # Convert Symbols
      for derived_symbol,derived_exponent in self.symbols:
        # Skip Canceling Units
        if(derived_exponent == 0): continue
        # Decompose into Base-Units
        if(derived_symbol in _definitions_.keys()): base_magnitude, base_symbols, base_conversion, *_ = _definitions_[derived_symbol]
        else:                                       base_magnitude, base_symbols, base_conversion     = (1,[(derived_symbol,1)],None)
        # If Disallowed, Stop Conversions.
        if(not allow_conversion and base_conversion!=None): base_magnitude, base_symbols, base_conversion = (1,[(derived_symbol,1)],None)
        # Distribute Derived Exponents into Base-Symbols.
        for base_numerator,base_exponent in base_symbols:
          units,exponents = Unit._add_to_unit_exponent_lists_(units,exponents,base_numerator,base_exponent,derived_exponent)
        # Modify Magnitude for Base Unit Conversion
        magnitude_modifier,base_magnitude,derived_exponent =_type_corrections_(magnitude_modifier,base_magnitude,derived_exponent)
        magnitude_modifier = magnitude_modifier*(base_magnitude**derived_exponent)
        # Add Function for Base Unit Conversion, Error on Multiple Conversions
        if(base_conversion != None):
          if(conversion == None): conversion = base_conversion(derived_exponent)
          else: raise ValueError(f"Failed to Decompose: Cannot Deconvolute Multiple Conversions.")
      # Fail Any Conversion with Multiple Symbols
      is_identity = conversion==None or all([eq_func(lambda x:x,f) for f in conversion])
      if(len(self.symbols)>1 and not is_identity and not _base_units_): 
        raise AmbiguousUnitException(f"Failed to Decompose: Ambiguous Decomposition. Cannot Deconvolute Multiple Conversions: {self.symbols}")
      # Set New Unit
      symbols=tuple(zip(units,exponents))
      magnitude_modifier,self_magnitude =_type_corrections_(magnitude_modifier,self.magnitude)
      magnitude = self_magnitude * magnitude_modifier
      # Returns Unit in base form and without definitions
      return Unit(symbols=symbols, magnitude = magnitude,_base_units_=True,_conversion_=conversion)
    def get_base(self,*args,definitions=None,defs=None):
      '''
      DESCRIPTION:
        Gets the base units without conversion factors or magnitudes as defined by the definitions property.
      ARGUMENTS:
        None.
      KNOWN ERRORS:
        N/A
      RETURN:
        Unit
      '''
      # Unit Definitions
      def_args     = [ _ for _ in args if isinstance(_,dict)]+[definitions,defs,self._definitions_]
      _definitions_ = self._fix_def_(*def_args)
      # Decompose Unit
      base_unit = self.decompose(definitions=_definitions_)
      # Return Base Unit
      return Unit(symbols=base_unit.symbols, magnitude = 1)
      
    # Type Checkers 
    @staticmethod
    def is_unit(u):
      try:
        Unit(u)
        return True
      except:
        return False
    @staticmethod
    def is_metric(arg):
      # Checks
      if(Unit.is_unit(arg)): arg = Unit(arg)
      else: raise TypeError("Cannot be cast as Unit")
      # Get Strings Lists
      unit_strs   = [u for u,e in arg.numerators] + [u for u,e in arg.denominators]
      # Attempt to decompose each unit string
      for unit_str in unit_strs:
        if(unit_str not in Unit.METRIC.keys()): 
          return False
      # If no failures, return true
      return True 
  
  # Get/Set Properties, Internal-Form Converter Functions 
  if(True):
    # Symbol Associated Functions
    @property
    def symbols(self):
      return self._symbols_
    @property
    def numerators(self):
      _numerators_,_denominators_ = Unit._numerator_denominator_form_(self._symbols_)
      return _numerators_
    @property
    def denominators(self):
      _numerators_,_denominators_ = Unit._numerator_denominator_form_(self._symbols_)
      return _denominators_
    
    # Symbol Associated Sub-Functions
    @classmethod
    def _fix_sym_(cls,symbols):
      if( symbols == None ): symbols = ()
      # Re-Structure Symbols
      val_sym,val_exp = [],[]
      for val in symbols:
        # Accept Tuple Form: ("unit",exp)
        if(isinstance(val,tuple)):
          sym,exp = val[0],val[1]
        # Accept String From: "unit"
        elif(isinstance(val,str)):
          if("^" in val): raise ValueError("Invalid Character: '^' ")
          if( any([ _ in val for _ in Unit.MULTIPLIERS ]) ): raise ValueError("Invalid Character.")
          if( any([ _ in val for _ in "0123456789" ] ) ): log.warning("Symbol contains a number.")
          
          sym,exp = val,Decimal("1")
        else:
          raise TypeError("Non-String Symbol: "+repr(val))
        # Append Symbol
        if(sym in val_sym): 
          i = val_sym.index(sym)
          val_exp[i] = val_exp[i] + exp
        else:
          val_sym.append(sym)
          val_exp.append(exp)
      # Recompose, Filter, and Sort (for consistent order)
      symbols = tuple(zip(val_sym,val_exp))
      symbols = [(symbol,exponent) for symbol,exponent in symbols if(symbol !="" and exponent!=0)]
      symbols.sort()
      symbols = tuple(symbols)
      # Return
      return symbols
    @staticmethod
    def _exponent_form_(numerators,denominators):
      units,exponents = [],[]
      # Convert Numerators
      if(numerators != () and numerators != None):
        for numerator,exponent in numerators:
          units,exponents = Unit._add_to_unit_exponent_lists_(units,exponents,numerator,exponent)
      # Convert Denominators
      if(denominators != [] and denominators != None):
        for denominator,exponent in denominators:
          units,exponents = Unit._add_to_unit_exponent_lists_(units,exponents,denominator,exponent,-1)
      # Return List Tuple
      symbols = tuple(zip(units,exponents))
      symbols = [(symbol,exponent) for symbol,exponent in symbols if(symbol !="" and exponent!=0)]
      symbols.sort()
      symbols = tuple(symbols)
      return symbols
    @staticmethod
    def _numerator_denominator_form_(symbols):
      numerators   = tuple([(unit,   exponent) for unit,exponent in symbols if(exponent>0)])
      denominators = tuple([(unit,-1*exponent) for unit,exponent in symbols if(exponent<0)])
      return numerators,denominators
    @staticmethod
    def _add_to_unit_exponent_lists_(unit_list,exponent_list,unit,exponent,exponent_multiplier=1):
      # Add to Pre-Existing Exponents 
      if(unit in unit_list): 
        index = unit_list.index(unit)
        exponent_list[index] = exponent_list[index] + exponent_multiplier*exponent
      # Append New Exponents
      else:
        unit_list.append(unit)
        exponent_list.append(exponent_multiplier*exponent)
      # Return Lists
      return unit_list,exponent_list
    
    # Definition
    @classmethod
    def _fix_def_(cls,*defs):
      # Units to Definitions
      defs = [_._definitions_ if isinstance(_,cls) else _ for _ in defs]
      # Remove Non-Definitions
      defs = [_ for _ in defs if isinstance(_,dict)]
      # Simple Returns 
      if(len(defs)==0): return None
      if(len(defs)==1): new_def = defs[0]
      # Combine Dictionaries
      if(len(defs)>=2):
        new_def = defs[0]
        defs    = defs[1:]
        for d in defs:
          new_def=dict(new_def,**d)
      # Return
      return new_def
    
    # Magnitude Associated Functions
    @property
    def magnitude(self):
      return self._magnitude_
    @classmethod
    def _fix_mag_(cls,magnitude):
      try:
        if( magnitude == None ): return 1
        if(isinstance(magnitude,Measure)):
          log.warning("Magnitude is a Measure.")
          if(magnitude.value < 0):  log.warning("Negative Magnitude on Unit.")
          if(magnitude.value == 0): log.warning("Magnitude of Zero.")
        elif(isinstance(magnitude,Number)):
          if(magnitude < 0):  log.warning("Negative Magnitude on Unit.")
          if(magnitude == 0): log.warning("Magnitude of Zero.")
        else: 
          magnitude = Decimal(magnitude)
          if(magnitude < 0):  log.warning("Negative Magnitude on Unit.")
          if(magnitude == 0): log.warning("Magnitude of Zero.")
        return magnitude
      except:
        raise TypeError(f"Magnitude ({magnitude}) is not a Number: "+str(type(magnitude)))
    
    @property
    def conversion(self):
      # Conversion = (TO_BASE, FROM_BASE)
      if(self._conversion_ != None):
        return self._conversion_
      else:
        # Return Identity Functions
        return (lambda x:x,lambda x:x)
  
  # Container-Like Operators
  if(True):
    def __contains__(self,value):
      if(isinstance(value,str)): value = Unit(value)
      if(isinstance(value,Unit)): return all([v[0] in [_[0] for _ in self._symbols_] for v in value._symbols_])
      else: raise TypeError("Invalid Type.")
    def __getitem__(self,value):
      if(isinstance(value,str)): return [(unit,exponent) for unit,exponent in self._symbols_ if(value==unit)][0]
      if(isinstance(value,int)): return self._symbols_[value]
      else: raise TypeError("Invalid Type.")
    #def __iter__(self):
    
  # String Converters
  if(True):
    MULTIPLIERS = ["*","\u00B7","\u00D7","\u22C5"]
    
    # Parsing Associated Functions
    def _parse_(self,parsable_str):
      # Clean String 
      parsable_str = parsable_str.strip()
      parsable_str = parsable_str.replace("**","^")
      parsable_str = parsable_str.replace("\u2212","-")
      # Handle Empty Strings
      if(parsable_str==""): return self
      # Find Magnitude Cut Index 
      magnitude_end_index = len(parsable_str)
      while( not Unit._parse_magnitude_(parsable_str[:magnitude_end_index])):
        magnitude_end_index = magnitude_end_index - 1
        if(magnitude_end_index==0): break
      # Assign Magnitude
      if(magnitude_end_index!=0):
        self._magnitude_ = self._fix_mag_(self._magnitude_ * Unit._parse_magnitude_(parsable_str[:magnitude_end_index]))
      # Separate Units from Magnitude
      unit_str  = parsable_str[magnitude_end_index:]
      # Initialize Lists for Outputs
      numerators   = []
      denominators = []
      # Parse out Numerators & Denominators via Multipliers(*) and Dividers(/)
      numerator_list,denominator_list = Unit._parse_by_multdiv_(unit_str)
      # Parse out Numerator's Exponents
      for numerator in numerator_list:
        numerator_numerators,numerator_denominators = Unit._parse_by_exponents_(numerator)
        numerators.extend(numerator_numerators)
        denominators.extend(numerator_denominators)
      # Parse out Denominators's Exponents
      for denominator in denominator_list:
        denominator_numerators,denominator_denominators = Unit._parse_by_exponents_(denominator)
        numerators.extend(denominator_denominators)
        denominators.extend(denominator_numerators)
      # Warnings 
      if(any([f=="" and e!=1 for f,e in numerators   ])): log.debug("There is an Empty Unit with an exponent: "+str(numerators))
      if(any([f!="" and e==0 for f,e in denominators ])): log.debug("There is a unit with a zero exponent: "   +str(denominators))
      # Assign Numerators & Denominators (Remove Empty String and Zero Exponent Units)
      numerators   = [(numerator,exponent)   for numerator,exponent   in numerators   if(numerator  !="" and exponent!=0)]
      denominators = [(denominator,exponent) for denominator,exponent in denominators if(denominator!="" and exponent!=0)]
      # Check For Non-Units
      punctuation = "!\"#&'()*+, -./:;<=>?@[]^_`{|}~\u00B1\u2213\u00B7\u00D7\u22C5\u2212"
      bad_numerators   = any([numerator   in punctuation for numerator  ,exponent in numerators])
      bad_denominators = any([denominator in punctuation for denominator,exponent in denominators])
      if(bad_numerators or bad_denominators): raise ValueError("Cannot Parse Unit.")
      # Set Symbol
      self._symbols_ = Unit._exponent_form_(numerators,denominators)
      # Return Self
      return self
    @staticmethod
    def _parse_magnitude_(mag_str):
      """
      This function attempts to convert a string to a magnitude. 
      If it fails, it returns zero (an invalid magnitude). 
      """
      # Strip Leading Multipliers
      mag_str = mag_str.lstrip("".join(Unit.MULTIPLIERS+["x"]))
      # Replace Abnormal Multipliers with *
      for m in Unit.MULTIPLIERS: mag_str = mag_str.replace(m,"*")
      # Possible x as Multiplier in Magnitude (e.g: "3.14x10^5 U")
      if("x" in mag_str):
        # Limit Number of x in mag_str
        number_of_x = len([None for chr in mag_str if(chr=="x")])
        if(number_of_x != 1): return 0
        # Limit Order: x then *
        x_index          = mag_str.find("x")
        multiplier_index = mag_str.find("*")
        if(multiplier_index != -1 and multiplier_index < x_index): return 0
        # Replace first x
        mag_str=mag_str.replace("x","*",1)
      # Assign Magnitude's Value and Exponential
      if("*" in mag_str): value,exponent = mag_str.split("*",1)
      else:
        if("^" in mag_str): value,exponent = "1",mag_str
        else:               value,exponent = mag_str,"1"
      # Attempt Decimal Conversions
      try:
        # Convert Value to Decimal
        value = Decimal(value)
        # Convert Exponent to Decimal
        if("^" in exponent):
          b,e = exponent.split("^",1)
          b,e = Decimal(b),Decimal(e)
          exponent = Decimal(b)**Decimal(e)
        else:
          exponent = Decimal(exponent)
        # Return Successful Decimal Conversion
        return value*exponent
      # Failed Decimal Conversions
      except:
        return 0
    @staticmethod
    def _parse_by_multdiv_(unit_str):
      '''
      DESCRIPTION:
        Organizes factors into numerators and denominators based on mutlipliers and dividers.
        Factors separated by spaces are assumed to be on the same numerator/denominator level.
      TESTS:
        assert ["abc","de","fg"],["hi","jk","l","mn"] == Unit.decompose_multdiv("abc / hi * de / jk * fg / l / mn")
        assert ["abc","de","fg"],["hi","jk","l","mn"] == Unit.decompose_multdiv("abc de fg / hi jk l mn")
      ARGUMENTS:
        unit =  string: with * and /
      KNOWN ERRORS:
        
      RETURN:
        (numerator_list,denominator_list)
        numerator_list      = list: 
        denominator_list    = list: 
      '''
      # Sanitize Input
      unit_str = str(unit_str)
      unit_str = unit_str.strip()
      # Early Exit
      if(unit_str == ""): return [],[]
      # Format
      for m in Unit.MULTIPLIERS: unit_str = unit_str.replace(m,"*")
      # Initialize Lists for Outputs
      numerator_list   = []
      denominator_list = []
      # Separate Units by  Multipliers and Dividers
      i=0
      while(True):
        # Get Indices of Multiplier or Divider
        index_slash    = unit_str.find("/",i+1)
        index_asterisk = unit_str.find("*",i+1)
        # Get Individual-Unit or Space-Separated-Units (Lead with Multiplier or Divider)
        if(  index_slash != -1 and index_asterisk != -1): unit = unit_str[i:index_slash] if(index_slash < index_asterisk) else unit_str[i:index_asterisk]
        elif(index_slash == -1 and index_asterisk != -1): unit = unit_str[i:index_asterisk]
        elif(index_slash != -1 and index_asterisk == -1): unit = unit_str[i:index_slash]
        else:                                             unit = unit_str[i:]
        # Track Numoratror vs Denominator
        is_denominator = unit[0] == "/"
        # Strip Unit
        if(is_denominator): unit = unit.strip("/ ")
        else:               unit = unit.strip("* ")
        # Split Unit
        unit_list = unit.split()
        # Append Unit List
        if(is_denominator): denominator_list.extend(unit_list)
        else:               numerator_list.extend(unit_list)
        # Get Next Multiplier/Divider Index
        if(  index_slash != -1 and index_asterisk != -1): i = index_slash if(index_slash < index_asterisk) else index_asterisk
        elif(index_slash == -1 and index_asterisk != -1): i = index_asterisk
        elif(index_slash != -1 and index_asterisk == -1): i = index_slash
        else:                                             break
      # Remove Dummy/Holder Numerator
      numerator_list = [i for i in numerator_list if i!="1"]
      # Return Lists as Numerators/Denominators
      return (numerator_list,denominator_list)
    @staticmethod
    def _parse_by_exponents_(unit_str):
      '''
      DESCRIPTION:
        Organizes factors into numerators and denominators based on exponents.
        It is assumed there are no spaces or division. 
      TESTS:
        assert ([("cm",Decimal(3))],[])                    == Unit._parse_by_exponents_("cm3")
        assert ([("cm",Decimal(3)),("mol",Decimal(1))],[]) == Unit._parse_by_exponents_("cm3mol")
        assert ([("cm",Decimal(3))],[("mol",Decimal(1))])  == Unit._parse_by_exponents_("cm3mol-1")
      ARGUMENTS:
        unit =  string: with unit(s) and exponent(s) in the form "U2" or "U^2" ("U2n2" or U^2n^2)
      KNOWN ERRORS:
        
      RETURN:
        (numerator_list,denominator_list)
        numerator_list      = list: 
        denominator_list    = list: 
      '''
      # Constants
      EXPONENT_CHARACTERS="-0123456789."
      # Format
      unit_str = str(unit_str)
      unit_str = unit_str.replace("-","-")
      unit_str = unit_str.strip()
      # Initialize Lists for Outputs
      numerator_list   = []
      denominator_list = []
      # Initialize Indices
      i=0
      unit_start_index = 0
      # Iterate over Given Unit String
      while(i<len(unit_str)):
        chr = unit_str[i]
        if(chr in EXPONENT_CHARACTERS):
          # Save Exponent-Start-Index
          exponent_start_index = i
          # Find Exponent-End-Index
          while(unit_str[i] in EXPONENT_CHARACTERS):
            i=i+1
            if(i>=len(unit_str)):break
          exponent_end_index = i
          # Cut-Out Paired Unit and Exponent
          unit     = unit_str[unit_start_index:exponent_start_index].rstrip("^")
          exponent = Decimal(unit_str[exponent_start_index:exponent_end_index])
          # Append Unit & Exponent
          if(exponent<0): denominator_list.append( (unit,abs(exponent)) )
          else:           numerator_list.append(   (unit,abs(exponent)) )
          # Save Next Unit-Start-Index
          unit_start_index = exponent_end_index
        else:
          i=i+1
      # Append Units without exponents
      if(unit_start_index<len(unit_str)):
        unit = unit_str[unit_start_index:]
        numerator_list.append((unit,Decimal(1)))
      # Return Numerator and Denominator Lists
      return (numerator_list,denominator_list)
    
    # String Associated Functions
    def __str__(self):
      return self.to_string()
    def to_string(self,explicit_exponents=True,explicit_mult=True,negative_exponents=False):
      """
      explicit_exponents = bool: Default True.  Uses exponent character ("^") when printed.
      explicit_mult      = bool: Default True.  Uses spaces instead of multiplier  character ("*") when printed.
      negative_exponents = bool: Default False. Uses negative exponents instead of division when printed. 
      """
      self_magnitude = Decimal(str(self.magnitude))
      # Handle None/Empty Values
      if(self.unitless()):    return ""
      if(self.symbols == ()): return str(Unit.scientific_form(self_magnitude))
      # Magnitude
      if(self_magnitude != Decimal(1)):
        scientific_magnitude = Unit.scientific_form(self_magnitude)
        has_units = self.symbols != ()
        use_multiplier = explicit_mult and has_units
        if(use_multiplier): magnitude_string = f"{scientific_magnitude} * "
        else:               magnitude_string = f"{scientific_magnitude} "
      else: 
        magnitude_string = ""
      # Load Numerator/Denominator
      numerators,denominators = Unit._numerator_denominator_form_(self.symbols)
      # Format Numerators
      numerator_factors =[]
      # Add Each Numerator
      for numerator,exponent in numerators:
        # Convert to Strings
        numerator = str(numerator)
        exponent  = str(exponent)
        # Make Exponented Numerator String
        if(exponent=="1"):        numerator_factor = numerator
        else:
          if(explicit_exponents): numerator_factor = f"{numerator}^{exponent}"
          else:                   numerator_factor = f"{numerator}{exponent}"
        # Append Exponented Numerator String
        numerator_factors.append(numerator_factor)
      # Format Denominators
      denominator_factors = []
      # Add Each Denominator
      for denominator,exponent in denominators:
        # Adjust & Convert to Strings
        if(negative_exponents): exponent = Decimal(-1)*exponent
        denominator = str(denominator)
        exponent    = str(exponent)
        # Make Exponented Denominator String
        if(exponent=="1"):        denominator_factor = denominator
        else:
          if(explicit_exponents): denominator_factor = f"{denominator}^{exponent}"
          else:                   denominator_factor = f"{denominator}{exponent}"
        # Append Exponented Denominator String
        denominator_factors.append(denominator_factor)
      # Positive Exponents and Implicit Multiplication: s A / N m 
      if(  not negative_exponents and not explicit_mult):
        # Format Numerators
        if(numerator_factors == []): numerator = "1"
        else:                        numerator = " ".join(numerator_factors)
        # Format Denominators
        denominator = " ".join(denominator_factors)
        # Combine
        if(denominator == ""): unit_string = f"{numerator}"
        else:                  unit_string = f"{numerator} / {denominator}"
      # Positive Exponents and Explicit Multiplication: s * A / N / m 
      elif(not negative_exponents and     explicit_mult):
        # Format Numerators
        if(numerator_factors == []): numerator = "1"
        else:                        numerator = " * ".join(numerator_factors)
        # Format Denominators
        denominator = " / ".join(denominator_factors)
        # Combine
        if(denominator == ""): unit_string = f"{numerator}"
        else:                  unit_string = f"{numerator} / {denominator}"
      # Negative Exponents and Implicit Multiplication: s A N-1 m-1 
      elif(    negative_exponents and not explicit_mult):
        # Format Numerators & Denominators
        numerator   = " ".join(numerator_factors)
        denominator = " ".join(denominator_factors)
        # Combine
        unit_string = f"{numerator} {denominator}"
      # Negative Exponents and Explicit Multiplication: s * A * N-1 * m-1
      elif(    negative_exponents and     explicit_mult):
        # Format Numerators & Denominators
        numerator   = " * ".join(numerator_factors)
        denominator = " * ".join(denominator_factors)
        # Combine
        unit_string = f"{numerator} * {denominator}"
      # Return
      return magnitude_string + unit_string 
    @staticmethod
    def scientific_form(dec,mult_symbol="\u00B7"):
      # Check & Normalize Decimal
      if(not isinstance(dec,Decimal)): raise TypeError("Given Improper Type")
      dec = dec.normalize()
      # Get Sign & Digit Strings
      sign, digits, _ = dec.as_tuple()
      sign_symbol = '-' if sign else ''
      digits = [str(i) for i in digits]
      first_digit,trail_digits = digits[0],''.join(digits[1:])
      # Get Exponent String
      exponent = dec.adjusted()
      exponent = "" if(exponent == 0) else f"10^{exponent}"
      # Format 
      if(  first_digit == "1" and trail_digits == "" and exponent == ""): sci_form = f"{sign_symbol}{first_digit}"
      elif(first_digit == "1" and trail_digits == "" and exponent != ""): sci_form = f"{sign_symbol}{exponent}"
      elif(first_digit != "1" and trail_digits == "" and exponent == ""): sci_form = f"{sign_symbol}{first_digit}"
      elif(first_digit != "1" and trail_digits == "" and exponent != ""): sci_form = f"{sign_symbol}{first_digit}{mult_symbol}{exponent}"
      elif(                       trail_digits != "" and exponent == ""): sci_form = f"{sign_symbol}{first_digit}.{trail_digits}"
      elif(                       trail_digits != "" and exponent != ""): sci_form = f"{sign_symbol}{first_digit}.{trail_digits}{mult_symbol}{exponent}"
      # Return
      return sci_form
    # Representation
    def __repr__(self):
      class_name = str(self.__class__.__name__)
      str_repr   = str(self)
      return f"{class_name}('{str_repr}')"
  
  # Math-like Operators
  if(True):
    
    # To-do order these so that more specific cases are handled first: Unit, Measure, then Decimal? Should just handle number in forward Also do all this for measure 
    # To-Do Order these so that abstract base classes are only handle in reverse functions - if handled at all
    # To-Do make sure all these have not implemented
    
    # Utility Function
    @staticmethod
    def _is_number_(x):
      """ Private Function. Used for Checking things can be cast as Decimals. """
      if(isinstance(x,Unit)):    return False
      if(isinstance(x,Measure)): return False
      if(isinstance(x,Number)):  return True
      try:
        Decimal(x)
        return True
      except:
        return False
    
    # Relation Operators
    if(True):
      # Hash 
      def __hash__(self):
        return hash((self._decomposed_._symbols_,self._decomposed_._magnitude_))
      # Equality-Like Relation Operators
      def dimensionless(self):
        return self._decomposed_.symbols == ()
      def unitless(self):
        return self._decomposed_.symbols == () and self._decomposed_.magnitude == 1
      def __eq__(self,other):
        # Compare Units 
        if(isinstance(other,Unit)):
          # Get Equality
          eq_symbols   = self._decomposed_.symbols   == other._decomposed_.symbols
          eq_magnitude = self._decomposed_.magnitude == other._decomposed_.magnitude
          # Return Equality
          return eq_symbols and eq_magnitude
        # Compare Tuples
        if(isinstance(other,tuple)):
          # Get Equality
          eq_symbols   = self._decomposed_.symbols   == other
          eq_magnitude = self._decomposed_.magnitude == 1
          # Return Equality
          return eq_symbols and eq_magnitude
        # Non-Units Not Equal.
        return False
      def __ne__(self,other):
        eq = self.__eq__(other)
        if(eq is NotImplemented): return NotImplemented
        else: return not self.__eq__(other)
      # Relative Relation Operators
      def  __lt__(self,other):
        return Measure(self) <  Measure(other)
      def  __le__(self,other):
        return Measure(self) <= Measure(other)
      def  __gt__(self,other):
        return Measure(self) >  Measure(other)
      def  __ge__(self,other):
        return Measure(self) >= Measure(other)
      
      
    
    
    # Addition & Subtraction Operators
    def __add__(self,other):
      # Try Convert to Measures
      self  = Measure._to_measure_(self)
      other = Measure._to_measure_(other)
      # Check Measures
      if(isinstance(self,Measure) and isinstance(other,Measure)):
        log.warning("Unit Addition casted to Measures.")
        return self+other
      # Failed Types
      return NotImplemented
    __radd__ = __add__
    def __sub__(self,other):
      # Try Convert to Measures
      self  = Measure._to_measure_(self)
      other = Measure._to_measure_(other)
      # Check Measures
      if(isinstance(self,Measure) and isinstance(other,Measure)):
        log.warning("Unit Subtraction casted to Measures.")
        return self-other
      # Failed Types
      return NotImplemented
    def __rsub__(self, other):
      # Try Convert to Measures
      self  = Measure._to_measure_(self)
      other = Measure._to_measure_(other)
      # Check Measures
      if(isinstance(self,Measure) and isinstance(other,Measure)):
        return other - self
      # Failed Types
      return NotImplemented
    # Lesser Addition & Subtraction
    def __neg__(self):
      return -1*self
    def __pos__(self):
      return self
    def __abs__(self):
      new_symbols     = self.symbols
      new_definitions = self._definitions_
      new_magnitude   = abs(self.magnitude)
      return Unit(symbols = new_symbols, magnitude = new_magnitude, definitions = new_definitions)
      
    # Multiplication & Division Operators
    def __mul__(self,other):
      # Default Functions
      is_number = Unit._is_number_
      is_unit   = lambda x: isinstance(x,Unit)
      # Defaults Values
      new_symbols,new_magnitude,new_definitions = [None]*3
      # Type: Unit * Unit = Unit
      if(is_unit(other)):
        # Simplify Input
        other = Unit(other)
        self_magnitude,other_magnitude=_type_corrections_(self.magnitude,other.magnitude)
        # Initialize Unit and Exponent Lists
        units,exponents = [],[]
        # Add Units & Exponents from Self
        for unit,exponent in self.symbols:
          units,exponents = Unit._add_to_unit_exponent_lists_(units,exponents,unit,exponent)
        # Add Units & Exponents from Other
        for unit,exponent in other.symbols:
          units,exponents = Unit._add_to_unit_exponent_lists_(units,exponents,unit,exponent)
        # Assign Values
        new_symbols     = tuple(zip(units,exponents))
        new_definitions = self._fix_def_(self._definitions_,other._definitions_)
        new_magnitude   = self_magnitude*other_magnitude
      # Type: Unit * Number = Unit
      if(is_number(other)):
        # Type Input
        other = other if(isinstance(other,Number)) else Decimal(other)
        self_magnitude,other_magnitude=_type_corrections_(self.magnitude,other)
        # Assign Values
        new_symbols     = self.symbols
        new_definitions = self._definitions_
        new_magnitude   = self_magnitude*other_magnitude
      # Improve Type Preservation
      if(isinstance(new_magnitude,float)): new_magnitude = int(new_magnitude) if(new_magnitude.is_integer()) else new_magnitude
      # Returns
      inputs = [new_symbols,new_magnitude,new_definitions]
      if(any([i!=None for i in inputs])):
        _unit_ = Unit(symbols = new_symbols, magnitude = new_magnitude, definitions = new_definitions)
        return _unit_
      # Failed Types
      return NotImplemented
    __rmul__ = __mul__
    def __truediv__(self,other):
      # Default Functions
      is_number = Unit._is_number_
      is_unit    = lambda x: isinstance(x,Unit)
      # Defaults Values
      new_symbols,new_magnitude,new_definitions = [None]*3
      # Types: Unit / Number = Unit
      if(is_number(other)): 
        # Simplify Input
        other = other if(isinstance(other,Number)) else Decimal(other)
        self_magnitude,other_magnitude=_type_corrections_(self.magnitude,other)
        # Assign Values
        new_symbols     = self.symbols
        new_definitions = self._definitions_
        new_magnitude   = self_magnitude/other_magnitude
      # Types: Unit / Unit = Unit
      if(is_unit(other)):
        # Simplify Input
        other = Unit(other)
        self_magnitude,other_magnitude=_type_corrections_(self.magnitude,other.magnitude)
        # Initialize Unit and Exponent Lists
        units,exponents = [],[]
        # Add Units & Exponents from Self
        for unit,exponent in self.symbols:
          units,exponents = Unit._add_to_unit_exponent_lists_(units,exponents,unit,exponent)
        # Add Inverted Units & Exponents from Other
        for unit,exponent in other.symbols:
          units,exponents = Unit._add_to_unit_exponent_lists_(units,exponents,unit,exponent,-1)
        # Assign Values
        new_symbols     = tuple(zip(units,exponents))
        new_definitions = self._fix_def_(self._definitions_,other._definitions_)
        new_magnitude   = self_magnitude/other_magnitude
      # Improve Type Preservation
      if(isinstance(new_magnitude,float)): new_magnitude = int(new_magnitude) if(new_magnitude.is_integer()) else new_magnitude
      # Returns
      inputs = [new_symbols,new_magnitude,new_definitions]
      if(any([i!=None for i in inputs])):
        _unit_ = Unit(symbols = new_symbols, magnitude = new_magnitude, definitions = new_definitions)
        return _unit_
      # Failed Types
      return NotImplemented
    def __rtruediv__(self,other):
      # Default Functions
      is_number = Unit._is_number_
      is_unit    = lambda x: isinstance(x,Unit)
      # Defaults Values
      new_symbols,new_magnitude,new_definitions = [None]*3
      # Type: Number / Unit = Unit
      if(is_number(other)):
        # Simplify Input
        other = other if(isinstance(other,Number)) else Decimal(other)
        self_magnitude,other_magnitude=_type_corrections_(self.magnitude,other)
        # Initialize Unit and Exponent Lists
        units,exponents = [],[]
        # Add Inverted Units & Exponents from Self
        for unit,exponent in self.symbols:
          units,exponents = Unit._add_to_unit_exponent_lists_(units,exponents,unit,exponent,-1)
        # Assign Values
        new_symbols     = tuple(zip(units,exponents))
        new_definitions = self._definitions_
        new_magnitude   = other_magnitude/self_magnitude
      # Improve Type Preservation
      if(isinstance(new_magnitude,float)): new_magnitude = int(new_magnitude) if(new_magnitude.is_integer()) else new_magnitude
      # Returns
      inputs = [new_symbols,new_magnitude,new_definitions]
      if(any([i!=None for i in inputs])):
        _unit_ = Unit(symbols = new_symbols, magnitude = new_magnitude, definitions = new_definitions)
        return _unit_
      # Failed Types
      return NotImplemented
    
    # To-Do todo TODO Fix this
    #def _divide(self, other):
    # Lesser Multiplication & Division
    #__floordiv__  = __truediv__
    #__rfloordiv__ = __rtruediv__
    # Modulous too
    # Not exactly sure how to implement these
    # Can't use taylor series on discontinuous functions
    
    # Exponents
    def __pow__(self,other):
      # Default Functions
      is_number = Unit._is_number_
      is_unit    = lambda x: isinstance(x,Unit)
      is_measure = lambda x: isinstance(x,Measure)
      # Get Exponent
      if(is_number(other)):    exp = other if(isinstance(other,Number)) else Decimal(other)
      elif(is_unit(other)):    exp = Unit(other).magnitude if Unit(other).dimensionless() else None
      elif(is_measure(other)): exp = other.simplify().value if other.simplify().unit.dimensionless() else None
      else: return NotImplemented
      if(exp == None): raise ValueError(f"Exponent of the Unit is not a Number: {other}")
      # Unzip, Multiply, & Re-Zip Exponents
      if(self.symbols != ()):
        _self_units,_self_exponents = zip(*self.symbols)
        exp,*_self_exponents=_type_corrections_(exp,*_self_exponents)
        _self_exponents = [_*exp for _ in _self_exponents]
        new_symbols = tuple(zip(_self_units,_self_exponents))
      else:
        new_symbols = ()
      # Exponent on Magnitude 
      self_magnitude,exp=_type_corrections_(self.magnitude,exp)
      new_magnitude = self_magnitude**exp
      new_definitions = self._definitions_
      # Improve Type Preservation
      if(isinstance(new_magnitude,float)): new_magnitude = int(new_magnitude) if(new_magnitude.is_integer()) else new_magnitude
      # Return Unit
      _unit_ = Unit(symbols = new_symbols, magnitude = new_magnitude, definitions = new_definitions)
      return _unit_
    def __rpow__(self,other):
      return other ** Measure(value=1,units=self)
    def sqrt(self):
      return self**(Decimal("0.5"))

@log_this
class Measure:
  '''
    DESCRIPTION:
      This class helps define a measurement in terms of other the value, error, and units.
      Note: For propagation of error, the operators associated with this class assume measurements are mutually independent and amenable to local linearization in taylor series expansions. 
    ARGUMENTS/PROPERTIES:
      value =  Number: The value of the measure.  
      error ?= Number: Defined as the positive square root of the variance. 
      units =  Unit:   The unit of the measure.
    NOTABLE ERRORS:
      
    EXAMPLE:
      Measure()
  '''
  
  # Initialization
  __slots__ = ("_val_","_units_","_variance_","_implied_","_simplified_")
  def __new__(cls,*args,value=None,error=None,units=None,unit=None,imply=None,definitions=None,defs=None,**kargs):
    # Create Instance
    self = super().__new__(cls)
    for slot in self.__slots__: setattr(self,slot,None) 
    
    # Initialize Number Inputs
    if(value != None): self._value_    = value
    if(error != None): self._error_    = error
    if(imply != None): self._implied_  = imply
    
    # Initialize Unit Input
    if(units!=None and unit!=None): raise TypeError("Unexpected Input (0): Ambiguous or Conflicting Arguments.")
    if(units!=None): self._units_ = units
    if(unit !=None): self._units_ = unit
    
    # Optional Implicit Arguments
    if(len(args)!=0):
      # Utility Functions
      def _is_number_(val):
        if(isinstance(val,Unit)):    return False
        if(isinstance(val,Measure)): return False
        if(isinstance(val,Number)):  return True
        try:
          Decimal(val)
          return True
        except:
          return False
      def _is_unit_(val):
        if(isinstance(val,Number)):  return False
        if(isinstance(val,dict)):    return False
        try:
          Unit(val)
          return True
        except:
          return False
      
      # Organize Inputs
      args      = [Decimal(_) if _is_number_(_) and isinstance(_,str) else _ for _ in args]
      dec_args  = [_ for _ in args if _is_number_(_)]
      meas_arg  = [_ for _ in args if isinstance(_,self.__class__)]
      unit_arg  = [_ for _ in args if isinstance(_,(str,Unit))]
      dict_args = [_ for _ in args if isinstance(_,dict)]
      
      # Error Out: Number of Inputs
      if(len(args)-len(dict_args)>2):                  raise TypeError("Unexpected Input (1): Ambiguous or Conflicting Arguments.")
      if(len(dec_args)>1):                             raise TypeError("Unexpected Input (2): Ambiguous or Conflicting Arguments.")
      if(len(meas_arg)>1):                             raise TypeError("Unexpected Input (3): Ambiguous or Conflicting Arguments.")
      if(len(unit_arg)>1):                             raise TypeError("Unexpected Input (4): Ambiguous or Conflicting Arguments.")
      if(self._units_ != None and len(unit_arg)  > 0): raise TypeError("Unexpected Input (5): Ambiguous or Conflicting Arguments.") 
      if(self._value_ != None and len(dec_args)  > 0): raise TypeError("Unexpected Input (6): Ambiguous or Conflicting Arguments.") 
      
      # Single Argument Forms
      if(len(args)-len(dict_args) == 1):
        arg = [_ for _ in args if not isinstance(_,dict)][0]
        # Error Out: Invalid Type
        invalid_type = not isinstance(arg,(str,Number,Measure,Unit))
        if(invalid_type): raise ValueError(f"Could not cast as Measure: {repr(arg)}")
        # Integrate Nested Class
        if(isinstance(arg,Measure)):
          for slot in self.__slots__:
            setattr(self, slot,getattr(arg, slot))
        # Parse to Class
        elif(isinstance(arg,Unit)):   self._units_ = arg
        elif(isinstance(arg,Number)): self._value_ = arg
        else: self._parse_(arg)
      # Multi Argument Forms
      else:
        if(len(dec_args)>0): self._value_ = dec_args[0]
        if(len(unit_arg)>0): self._units_ = unit_arg[0]
      
    # Optional Explicits (All Protected)
    if(len(kargs)!=0):
      for key in kargs.keys():
        if(key in self.__slots__):
          setattr(self,key,kargs[key]) 
    
    # Invalid Keywords
    valid_keys= list(self.__slots__)+["_base_units_"]
    for key in kargs.keys():
      if(key not in valid_keys):
        raise TypeError("Unexpected Input (): Unexpected kwarg: "+key) 
    
    # Initialize Unit Definition
    def_args = [ _ for _ in args if isinstance(_,dict)]+[self._units_,definitions,defs]
    unit_def = Unit._fix_def_(*def_args)
    
    # Save Units
    self._units_ = Unit(self._units_, defs=unit_def)
    
    # Fail if No Value and No Unit
    if(self.value == None and self.units!=Unit(None)): self._value_ = 1
    if(self.value == None): raise TypeError("Unexpected Input: No Value.") 
    
    # Simplify On Load. For Speed.
    if("_base_units_" not in kargs.keys() or not kargs["_base_units_"]):
      self._simplified_ = self.simplify()
    else:
      self._simplified_ = self
    
    # Return 
    return self
  
  # Copies of Immutable Objects can be themselves.
  def __copy__(self): return self
  def __deepcopy__(self, memo): return self
  
  # Simplification Functions 
  if(True):
    def convert(self,*args,defs=None,definitions=None,_base_units_=False):
      """
      Converts a measure in one unit to a measure in another unit.
      Conversions do not (and should not) propagate unit definitions, so conversions to non-metric require the definition in the conversion function.
      """
      # WARNING: This function is hard to understand.
      # I've done my best to make it easy, but...
      # Do not mess with it until you understand the whole of the module.
      # See Section "Convert Self to Base Units" below for more.
      # 
      
      # Allow dictionary as arbitrary arguments.
      dict_args = [_ for _ in args if isinstance(_,dict)]
      non_dict  = [_ for _ in args if _ not in dict_args]
      if(len(non_dict)!=1): 
        if(len(non_dict)>1): raise ValueError("Too many non-dictionary arguments.")
        if(len(non_dict)<1): raise ValueError("No Unit argument.")
      new_unit = non_dict[0]
      
      # Cast New Unit as Unit
      if(Unit.is_unit(new_unit)):
        new_unit = Unit(new_unit,*dict_args,defs=defs,definitions=definitions)
        new_base_unit  = new_unit._decomposed_
        self_base_unit = self._units_._decomposed_
      else: raise TypeError("Cannot be cast as Unit")
      if(self_base_unit.symbols != new_base_unit.symbols): raise IncompatibleUnitException(f"Incompatible Units: {self._units_}  =/=  {new_unit} ({self_base_unit}  =/=  {new_base_unit})")
      
      # Convert Self to Base Units
      if(True):
        # This section is actually conceptually simple. 
        #   1: Separate the      value and error  from the unit
        #   2: Scale the         value and error  with the base-unit magnitude
        #   3: Deconvoluted the  value and error  with the base-unit conversion function
        # 
        # The next section does the reverse. 
        #
        # Despite the conceptual simplicity, technical details in this section make it tough to understand.
        # It requires understanding three things, roughly corresponding to the three above:
        #   1: Recursion in initializing Measures.
        #   2: How the decompose function in Unit creates base units.
        #   3: The conversion system for non-standard units. 
        # 
        # I've separated it from the rest of the code by indentation and add comments to try to help.
        # 
        # 
        
        # Measure-Unit to Measure-Unitless
        _self_value_error_ = self.value if(self.error == 0) else Measure(value=self.value, error = self.error,_base_units_=True)
        # Note: Keep type == Measure for propagation of error.
        # Caution: error==0 condition prevents recursion in Unit & Decimal Conversions.
        
        # Type Correct and Scale
        _self_value_error_,_self_units_magnitude_ =_type_corrections_(_self_value_error_,self_base_unit.magnitude)
        _self_scaled_value_error_ = _self_value_error_*_self_units_magnitude_
        # Use Unit Conversion Function to Convert Unitless to Base Unit
        measure_in_base_units  = self_base_unit.conversion[0](_self_scaled_value_error_) 
        # Note: Self._units_ decomposes on assignment, so conversion is not the standard identity function.
        # Note: conversion[0] Converts values to base from the previous units
      
      # Measure in Base Units to Measure in New Units
      if(True):
        # This is just the reverse of the last section. 
        # It should be easy if you could follow the last section.
        # 
        measure_with_new_conversion = new_base_unit.conversion[1](measure_in_base_units) 
        
        # Note: conversion[1] Converts values from base to the new units
        measure_with_new_conversion,new_base_conversion_magnitude =_type_corrections_(measure_with_new_conversion,new_base_unit.magnitude)
        measure_in_new_units = measure_with_new_conversion / new_base_conversion_magnitude
        
      # Return New Units Measure with preserved implied.
      if(isinstance(measure_in_new_units,Measure)):
        return Measure(value=measure_in_new_units.value , error=measure_in_new_units.error,units=new_unit,imply = self.implied,_base_units_=_base_units_)
      if(isinstance(measure_in_new_units,Number)):
        return Measure(value=measure_in_new_units , error=0 , units=new_unit , imply = self.implied , _base_units_=_base_units_)
    
    def simplify(self): 
      # No New Info? -> Quick Exit
      if(self._simplified_ != None): return self._simplified_
      # Simplify
      return self.convert(self._units_.get_base(),_base_units_=True)
  
  # Getters/(setters) Properties
  if(True):
    # Value
    @property
    def value(self):
      return self._val_
    @property
    def _value_(self):
      return self._val_
    @_value_.setter
    def _value_(self,val):
      # Error
      if(isinstance(val,Measure)): raise TypeError("Nested Measure cannot be value.")
      if(isinstance(val,Unit)):    raise TypeError("Nested Unit cannot be value.")
      # Corrections 
      if(isinstance(val,str) and _is_(Decimal,val)): val = Decimal(val)
      if(self._variance_ != None): 
        val,self._variance_ = _type_corrections_(val,self._variance_)
      # Assign 
      if(isinstance(val,Number)):  self._val_ = val
      else: raise TypeError(f"Type {type(val)} cannot be value.")
      
    
    # Unit
    @property
    def unit(self):
      return self._units_
    @property
    def units(self):
      return self._units_
    
    # Error
    @property
    def error(self):
      '''
      Error is the positive square root of variance. 
      This is absolute, not relative, uncertainty.
      Note: Error Propagation is calculated via a Taylor Series Expansion. 
      '''
      if(self._variance_ == None and self.value != None):
        error_decimal = Measure._uncertain_digit_magnitude_(self.value)*Decimal("5")/Decimal("10")
        _,error = _type_corrections_(self.value,error_decimal)
        return error
      return _sqrt_(self._variance_)
    @property
    def _error_(self):
      return self.error()
    @_error_.setter
    def _error_(self,err):
      # Error or Exit
      if(isinstance(err,Measure)): raise TypeError("Nested Measure cannot be Error.")
      if(isinstance(err,Unit)):    raise TypeError("Nested Unit cannot be Error.")
      # Implied
      self._implied_ = err==None
      # Corrections
      if(isinstance(err,str)): err = Decimal(err)
      if(self.value != None): 
        if(self._implied_): err = Measure._uncertain_digit_magnitude_(self.value)*Decimal("5")/Decimal("10")
        self._val_,err = _type_corrections_(self._val_,err)
      # Assign
      self._variance_ = err**2
      
    
    @property
    def implied(self):
      if(self._implied_ == None): return True
      return self._implied_
    
  # String Converters
  if(True):
    PRE_UNITS = ["pH","$"]
    @staticmethod
    def _parse_number_with_exponents_(d):
      d = d.replace("**","^")
      exponent_decimals = [Decimal(_) for _ in d.split("^")]
      if(len(exponent_decimals)>2): log.warning("Parser reading exponents of exponents.")
      value = exponent_decimals.pop(0)
      for exp in exponent_decimals:
        value = value**exp
      return value
    @staticmethod
    def _parse_value_error_(d,notation):
      d = d.replace("**","^")
      if(notation == 1):
        value_str = d[:d.index("(")] + d[d.index(")"):].strip(")")
        error_str = d[d.index("("):d.index(")")].strip("(")
        value = Measure._parse_number_with_exponents_(value_str)
        error = Measure._parse_number_with_exponents_(error_str)
      elif(notation == 0): 
        value_str = d.split("\u00B1")[0].strip()
        error_str = d.split("\u00B1")[1].strip()
        value = Measure._parse_number_with_exponents_(value_str)
        error = Measure._parse_number_with_exponents_(error_str)
        
        #value,error = [Measure._parse_number_with_exponents_(i.strip()) for i in d.split("\u00B1")]
      else:
        value_str =d
        error_str =""
        value = Measure._parse_number_with_exponents_(d)
        error = None
      # Return
      return value,error,value_str,error_str
    def _parse_(self,measure_str):  
      
      # Format Input
      original_measure_str = measure_str[:]
      measure_str = measure_str.strip()
      
      # Default Values
      units       = None 
      value_error = None
      
      # Identify Notation 
      has_parenthetical = "(" in measure_str and ")" in measure_str and measure_str.find("(") < measure_str.find(")")
      has_plusminus     = measure_str.count("\u00B1") == 1
      if(has_parenthetical and has_plusminus): raise ValueError("Cannot Parse Measure: "+original_measure_str)
      
      notation = None
      if(has_plusminus):     notation = 0
      if(has_parenthetical): notation = 1 
      
      # Parse Preceding Units
      defs = None
      for pu in self.PRE_UNITS:
        if(measure_str.startswith(pu)):
          if(pu == "pH"): defs = Unit.CONCENTRATION_UNITS
          units = Unit(pu,defs)
          measure_str = measure_str.lstrip(pu)
          value_error = measure_str.strip()
          break
      
      # Parse Non-Preceding Units
      if(units==None and value_error==None):
        # Get Value
        i=len(measure_str)
        while( not _is_(Measure._parse_value_error_,measure_str[:i],notation) ):
          i=i-1
          if(i<=0): 
            break
        
        value_error = measure_str[:i]
        units = Unit(measure_str[i:])
        
      # Split Value & Error
      if(has_parenthetical):
        value,error,value_str,error_str = Measure._parse_value_error_(value_error,notation)
        error = Measure._uncertain_digit_magnitude_(value_str)*error
        #value = Decimal(value_error[:value_error.index("(")] + value_error[value_error.index(")"):].strip(")"))
        #error = Measure._uncertain_digit_magnitude_(value)*Decimal(value_error[value_error.index("("):value_error.index(")")].strip("("))
      elif(has_plusminus): 
        value,error,value_str,error_str = Measure._parse_value_error_(value_error,notation)
      else:
        if(value_error==""): 
          value = None
          error = None
        else:
          value,error,value_str,error_str = Measure._parse_value_error_(value_error,notation)
      
      # Set Self Values & Units 
      magnitude = value if(self.value!=None and value!=None) else 1
      if(self.value == None and value != None): self._value_    = value
      if(self._units_ == None):                 self._units_    = magnitude*units
      if(self.implied and error != None ):      self._error_    = error
    
    def __str__(self):
      return self.to_string()
    def to_string(self,uncertain_places=True,notation=0):
      ################
      # Value String #
      ################
      # Type Value
      value = Decimal(str(self.value))
      # Rounded Value
      if(uncertain_places!=True):
        place_magnitude = Decimal("1"+(uncertain_places-1)*"0")
        value_magnitude = Measure._certain_digit_magnitude_(value)
        error_magnitude = Measure._certain_digit_magnitude_(self.error)
        if(value_magnitude<=error_magnitude): log.debug("Value and Error_magnitude are very close.")
        if(value_magnitude<place_magnitude/error_magnitude): log.debug("Rounds Non-Decimal Digit.")
        value = round(value/error_magnitude*place_magnitude)*error_magnitude/place_magnitude
      # To String
      value_str = str(Measure._pretty_decimal_(value))
      
      ################
      # Error String #
      ################
      error_str = ""
      # 
      if(not self.implied):
        # Type Error (Needed for Floats?)
        error = Decimal(str(self.error))
        
        # Round error
        if(uncertain_places!=True):
          place_magnitude = Decimal("1"+(uncertain_places-1)*"0")
          error_magnitude = Measure._certain_digit_magnitude_(error)
          error           = round(error / error_magnitude * place_magnitude) * error_magnitude / place_magnitude
        
        #Plus Minus Format
        if(notation == 0):
          error_str = " \u00B1 "+str(Measure._pretty_decimal_(error))
        #Parenthetic Format
        elif(notation == 1):
          if(uncertain_places!=True):
            error_str = "("+str(Measure._pretty_decimal_(error / Measure._uncertain_digit_magnitude_(self.value)))[:uncertain_places]+")"
          else:
            error_str = "("+str(Measure._pretty_decimal_(error / Measure._uncertain_digit_magnitude_(self.value)))+")"
      
      # Assemble Value with error
      measure_str = value_str + error_str
      
      ###############
      # Unit String #
      ###############
      # Unit Order
      unit_ = self._units_
      if(unit_ == Unit() or unit_ == None):
        pass
      elif(str(unit_) in self.PRE_UNITS):
        if(str(unit_) == "pH"): measure_str = str(unit_)+" "+measure_str
        else:                   measure_str = str(unit_)+measure_str
      else:
        if(str(unit_).startswith("1 /")): measure_str = measure_str + str(unit_).lstrip("1")
        elif(str(unit_).startswith( ("1","2","3","4","5","6","7","8","9") )): measure_str = measure_str +" * "+ str(unit_)
        else: measure_str = measure_str +" "+ str(unit_)
      
      # Return
      return measure_str
    def __repr__(self):
      if(Measure(str(self)) == self): return f"Measure('{str(self)}')"
      input_eval_str = ",".join([f"{slot}={repr(getattr(self,slot))}" for slot in self.__slots__[:-1]])
      return str(self.__class__.__name__)+"("+input_eval_str+")"
    
    # String Sub-Functions
    @staticmethod
    def _pretty_decimal_(dec):
      # Simplify
      norm_dec = dec.normalize()
      # Decompose
      sign, digit, exponent = norm_dec.as_tuple()
      # Keep decimals without trailing zeros (Normalized) or keep trailing zeros without decimal (Quantized)
      return norm_dec if exponent <= 0 else norm_dec.quantize(1)
    @staticmethod
    def _uncertain_digit_magnitude_(dec):
      # Decimal
      if(isinstance(dec,Decimal)): return Decimal((0,(1,),dec.normalize().as_tuple()[-1]))
      
      # Str, Float, etc.
      
      # Format
      val_str = str(dec).lower()
      # Strip Sign
      val_str = val_str.strip("-")
      
      # Error On Special Numbers
      if("nan" in val_str):
        raise ValueError("No error in NaN.")
      if("infinity" in val_str):
        raise ValueError("No error in Infinity.")
      if("0" == val_str):
        return Decimal("1")
      
      # All Digits in exponent notation are significant
      if("e" in val_str):
        # Decompose Exponent Notation
        num,exp = val_str.split("e")
        # Convert to Zeros
        new_num = ""
        for i in num:
          if(i in "1234567890"):
            new_num=new_num+"0"
          else:
            new_num=new_num+i
        # Replace last Digit with a One
        new_num = new_num[:-1]+"1"
        # Multiply appropriately
        return Decimal(new_num+"e"+str(exp))
      # Sig.Fig. Rules to Determine Last Sig.Fig.
      else:
        # decimal: 34.9045 -> 0.0001
        if("." in val_str):
          if(val_str[-1]=="."): 
            return Decimal("1")
          else:
            whole,fractional = val_str.split(".")
            return Decimal("."+"0"*(len(fractional)-1)+"1")
        # No decimal: e.g. 45000 -> 1000
        else:
          insig_trailing_zeros = "0"*(len(val_str)-len(val_str.strip("0")))
          return Decimal("1"+insig_trailing_zeros)
    @staticmethod
    def _certain_digit_magnitude_(dec):
      # Format
      val_str = str(dec).lower()
      # Strip Sign
      val_str = val_str.strip("-")
      
      # Error On Special Numbers
      if("nan" in val_str):
        raise ValueError("No error in NaN.")
      if("infinity" in val_str):
        raise ValueError("No error in Infinity.")
      if("0" == val_str):
        return Decimal("1")
      
      # First Sig Fig is one the rest are zeros
      new_val = ""
      first_sig_fig = True
      for i in val_str:
        if(i in "123456789" and first_sig_fig):
          new_val = new_val+"1"
          first_sig_fig = False
        elif(i in "123456789" and not first_sig_fig):
          new_val = new_val+"0"
        else: 
          new_val = new_val+i
      # Return as decimal
      return Decimal(new_val)
  
  # Operators
  if(True):
    # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
    #
    # To-Do: Ctrl+F each of these make sure there is a version for unit.
    # Checked: 
    #
    # To-Do make sure all these have not implemented 
    # Checked: eq, ne,lt,le,gt,ge,add,radd,sub,rsub,mul,rmul,truediv,rtruediv,
    
    # To-Do make sure all of these convert units properly
    # Checked: mul, div, add
    
    # Utility Function
    @staticmethod
    def _to_measure_(other):
      """Internal Function that assists in Type-Handling for Operators.
      Note: Convert to Measures is Slower than doing each operation long form, but Easier to Read and Maintain. 
      Note: Order is More Specific to Less Specific
      Measure as a Vector-Container
      - Abstract Base Classes are handled immediately, rather than only in reverse functions, because Measure contains numbers.
      - Conversion occures immediately, rather than as last resort, because Measure contains numbers.
      - While Measure is registered as a number, it's also sorta a well-designed vector. 
      - If parent vectors are registered as numbers, this design may break down depending on use. 
      """
      # Try Convert to Measures (Cannot use _base_units_ becuase they need to be simplified)
      if(isinstance(other,Measure)): return other
      if(isinstance(other,Unit)):    return Measure(value=1, units=other , error=0)
      if(isinstance(other,Number)):  
        # Default Values
        unit  = Unit()
        error = 0
        value = other
        # Parse Number attribute list
        if('__dict__' in dir(other)):
          other_attributes = [i for i in other.__dict__.keys() if i[:1] != '_']
          other_attributes = [i for i in other_attributes if not callable(i)] # What about @property
          # Check Attributes for Units and Error 
          for attribute in other_attributes:
            if(attribute in ["error","variance","stddev","sigma"]):
              log.warning("Number type has some form of error: Assigning to Error, but probably not done correctly.")
              error = getattr(other,attribute)
            if("unit" in attribute):
              log.warning("Number type has some form of unit: Converting to Unit, but probably not done correctly.")
              unit = Unit(getattr(other,attribute))
        # Built-in Type Corrections
        else:
          if(isinstance(other,bool)): value = int(other)
        # Return
        return Measure(value=value, units=unit, error=error,_base_units_=True)
      # Last Resort Use Parser
      if(_is_(Measure,other)): 
        # Parse to Measure
        other = Measure(other)
        # Pure Numbers or Units
        if(other.unit == Unit() and other.implied): other._error_ = 0
        if(other.value == 1 and other.implied):     other._error_ = 0
        # To-Do: "1 * 5 cm" is a measure. "cm" is a Unit Fix this.
        # Update Simplified For Error: None required to prevent redirect in simplify()
        other._simplified_ = None
        other._simplified_ = other.simplify()
        # Return Measure
        return other
      # Return
      return other
    
    # Relation Operators
    if(True):
      # Hash 
      def __hash__(self):
        return hash((self._simplified_._val_,self._simplified_._units_,self._simplified_._variance_,self._simplified_._implied_))
      # Equality Relation Operators
      def approx(self,other):
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Convert to Measure
        other = Measure._to_measure_(other)
        # Add Measures
        if(isinstance(other,Measure)):
          # Simplify Inputs
          _self_,_other_  = self._simplified_,other._simplified_
          # Check Same Dimensions
          if(_self_._units_.symbols != _other_._units_.symbols): raise IncompatibleUnitException("Incompatible Units: "+str(self._units_)+";"+str(_other_._units_))
          # Input Values
          x,dx = _self_.value  , _self_.error
          y,dy = _other_.value , _other_.error
          # Type Corrections
          x,dx,y,dy = _type_corrections_(x,dx,y,dy)
          # Min max values
          _self_add  = (x + dx) 
          _self_sub  = (x - dx) 
          _other_add = (y + dy)
          _other_sub = (y - dy)
          # Compare Mins to Maxes
          return _self_sub <= _other_add and _other_sub <= _self_add
        # Failed Types
        return NotImplemented
      @staticmethod
      def _dec_isclose_(x,y):
        # Even for Decimals, isclose is necessary   as even propogation of error functions change magnitude before back calculating.
        # i = Decimal("256.25").sqrt()
        # assert i/Decimal(5) == ((i/Decimal(5))**2).sqrt()
        
        if(x==y): return x ==y
        
        # This only works if number of digits is fully utilizing precision
        if( len(x.as_tuple()[1]) >= decimal.getcontext().prec-1 and len(y.as_tuple()[1]) >= decimal.getcontext().prec-1  ):
          # To-To: Choose [uncertain or normalize] line of code (directly below), if both lines of code are actually equivelent.
          return abs(x-y) <= min( Decimal((0,(2,),Measure._uncertain_digit_magnitude_(x).as_tuple()[-1])) , Decimal((0,(2,),Measure._uncertain_digit_magnitude_(y).as_tuple()[-1])) )
          #return abs(x-y) <= min( Decimal((0,(1,),x.normalize().as_tuple()[-1])) , Decimal((0,(1,),y.normalize().as_tuple()[-1])) )
          
          # To-Do: Check if this needs to be changed to shift off uncertain digit entirely.
          
        else: return False
        
      def __eq__(self,other):
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Convert to Measure
        other = Measure._to_measure_(other)
        # Add Measures
        if(isinstance(other,Measure)):
          # Simplify Inputs
          _self_,_other_  = self._simplified_,other._simplified_
          
          # Check Same Dimensions
          self_is_zero  = _self_.value == 0 and (_self_.error == 0 or self.implied)
          other_is_zero = _other_.value == 0 and (_other_.error == 0 or other.implied)
          if(not (self_is_zero or other_is_zero)):
            if(_self_._units_.symbols != _other_._units_.symbols): return False
          
          # Type Corrections
          x , y = _type_corrections_(_self_.value,_other_.value)
          dx,dy = _type_corrections_(_self_.error,_other_.error)
          
          # Check Value & Error
          eq_value  = Measure._dec_isclose_( x, y) if(isinstance ( x, Decimal) ) else cmath.isclose( x, y)
          eq_error  = Measure._dec_isclose_(dx,dy) if(isinstance (dx, Decimal) ) else cmath.isclose(dx,dy)
          
          # Implied Error
          imp_error = self.implied or other.implied
          if(imp_error): return eq_value
          else:          return eq_value and eq_error
        # Failed Types
        return NotImplemented
      def __ne__(self,other):
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        eq = self.__eq__(other)
        if(eq is NotImplemented): return NotImplemented
        else: return not self.__eq__(other)
      # Relative Relation Operators
      def  __lt__(self,other):
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Convert to Measure
        other = Measure._to_measure_(other)
        # Add Measures
        if(isinstance(other,Measure)):
          # Simplify Inputs
          _self_,_other_  = self._simplified_,other._simplified_
          # Check Dimensions
          self_is_zero = _self_.value == 0 and (_self_.error == 0 or self.implied)
          other_is_zero = _other_.value == 0 and (_other_.error == 0 or other.implied)
          if(not (self_is_zero or other_is_zero)):
            if(_self_._units_.symbols != _other_._units_.symbols): raise IncompatibleUnitException("Incompatible Units: "+str(self._units_)+";"+str(_other_._units_))
          # Input Values
          x,dx = _self_.value  , _self_.error
          y,dy = _other_.value , _other_.error
          # Type Corrections
          x,dx,y,dy = _type_corrections_(x,dx,y,dy)
          # Implied Error
          if(self.implied or other.implied):
            return x < y
          # Explicit Error
          else:
            # Min max values
            _self_add  = (x + dx)
            _self_sub  = (x - dx)
            _other_add = (y + dy)
            _other_sub = (y - dy)
            # Less Than with Error
            return _self_add < _other_sub
        # Failed Types
        return NotImplemented
      def  __le__(self,other):
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Convert to Measure
        other = Measure._to_measure_(other)
        # Add Measures
        if(isinstance(other,Measure)):
          # Simplify Inputs
          _self_,_other_  = self._simplified_,other._simplified_
          # Check Dimensions
          self_is_zero = _self_.value == 0 and (_self_.error == 0 or self.implied)
          other_is_zero = _other_.value == 0 and (_other_.error == 0 or other.implied)
          if(not (self_is_zero or other_is_zero)):
            if(_self_._units_.symbols != _other_._units_.symbols): raise IncompatibleUnitException("Incompatible Units: "+str(self._units_)+";"+str(_other_._units_))
          # Input Values
          x,dx = _self_.value  , _self_.error
          y,dy = _other_.value , _other_.error
          # Type Corrections
          x,dx,y,dy = _type_corrections_(x,dx,y,dy)
          # Implied Error
          if(self.implied or other.implied):
            return x <= y
          # Explicit Error
          else:
            # Min max values
            _self_add  = (x + dx) 
            _self_sub  = (x - dx) 
            _other_add = (y + dy)
            _other_sub = (y - dy)
            # Less Than Eq with Error
            return _self_sub <= _other_sub
        # Failed Types
        return NotImplemented
      def  __gt__(self,other):
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Convert to Measure
        other = Measure._to_measure_(other)
        # Add Measures
        if(isinstance(other,Measure)):
          # Simplify Inputs
          _self_,_other_  = self._simplified_,other._simplified_
          # Check Dimensions
          self_is_zero = _self_.value == 0 and (_self_.error == 0 or self.implied)
          other_is_zero = _other_.value == 0 and (_other_.error == 0 or other.implied)
          if(not (self_is_zero or other_is_zero)):
            if(_self_._units_.symbols != _other_._units_.symbols): raise IncompatibleUnitException("Incompatible Units: "+str(self._units_)+";"+str(_other_._units_))
          # Input Values
          x,dx = _self_.value  , _self_.error
          y,dy = _other_.value , _other_.error
          # Type Corrections
          x,dx,y,dy = _type_corrections_(x,dx,y,dy)
          # Implied Error
          if(self.implied or other.implied):
            return x > y
          # Explicit Error
          else:
            # Min max values
            _self_add  = (x + dx) 
            _self_sub  = (x - dx) 
            _other_add = (y + dy)
            _other_sub = (y - dy)
            # Greater Than with Error
            return _self_sub > _other_add
        # Failed Types
        return NotImplemented
      def  __ge__(self,other):
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Convert to Measure
        other = Measure._to_measure_(other)
        # Add Measures
        if(isinstance(other,Measure)):
          # Simplify Inputs
          _self_,_other_  = self._simplified_,other._simplified_
          # Check Dimensions
          self_is_zero = _self_.value == 0 and (_self_.error == 0 or self.implied)
          other_is_zero = _other_.value == 0 and (_other_.error == 0 or other.implied)
          if(not (self_is_zero or other_is_zero)):
            if(_self_._units_.symbols != _other_._units_.symbols): raise IncompatibleUnitException("Incompatible Units: "+str(self._units_)+";"+str(_other_._units_))
          # Input Values
          x,dx = _self_.value  , _self_.error
          y,dy = _other_.value , _other_.error
          # Type Corrections
          x,dx,y,dy = _type_corrections_(x,dx,y,dy)
          # Implied Error
          if(self.implied or other.implied):
            return x >= y
          # Explicit Error
          else:
            # Min max values
            _self_add  = (x + dx) 
            _self_sub  = (x - dx) 
            _other_add = (y + dy)
            _other_sub = (y - dy)
            # Greater Than Eq with Error
            return _self_add >= _other_add
        # Failed Types
        return NotImplemented
      
      def is_simplified(self):
        if(self._simplified_ == None): return True
        if(self._simplified_._units_.symbols == self._units_.symbols): return True
        return False
    
    # Unary Operators
    if(True):
      def __abs__(self):
        # Simplify Inputs
        _self_  = self._simplified_
        # Assign Public Values
        new_value = abs(_self_.value)
        new_error = _self_.error
        new_units = _self_._units_
        # Assign Private Values
        new_imply = self.implied 
        new_base_units = self._simplified_ == None 
        
        # Returns
        _measure_ = Measure(value=new_value,error=new_error,units=new_units,imply=new_imply,_base_units_=new_base_units)
        # Return Inner-Measures Unconverted (prevents recursion)
        if(new_base_units): return _measure_
        # Return in Preferred Units
        try:
          new_pref  = self._units_
          return _measure_.convert(new_pref)
        except: return _measure_
      def __neg__(self):
        return Measure(value=-1*self.value,error=self.error,units=self.units,imply=self.implied, _base_units_ = self._simplified_ == None )
      def __pos__(self): 
        return self
      #  Measure( value=pos(self.value),  )
      
      def sin(self):
        """ Returns sine of the number. Accepts Unitless and Degrees. Bad types return NotImplemented.
        Propagation of Error
          Function: f = sin(x)
          Variance: sigma_f^2 = ( cos(x) sigma_x )^2 
        """
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Simplify Inputs
        _self_  = self._simplified_
        # Check No Dimensions
        if(not self._units_.dimensionless()): 
          if(self._units_ == Unit("rad")): log.error("The unit 'rad' is processed as units of radiation. Radians are generally unitless or m/m.")
          raise IncompatibleUnitException("Non-Degree, Non-Dimensionless Units in Trigonometry")
        # Input Value
        x,dx = _self_.value,_self_.error
        # Type Corrections
        x,dx = _type_corrections_(x,dx)
        # Assign Public Values
        new_value = _sin_(x)
        new_error = _sqrt_(_cos_(x)**2 * dx**2)
        new_units = None
        # Assign Private Values
        new_imply = self.implied
        # Returns
        _measure_ = Measure(value=new_value,error=new_error,units=new_units,imply=new_imply,_base_units_=True)
        # Return (No Preferred Units)
        return _measure_
      def cos(self):
        """ Returns sine of the number. Accepts Unitless and Degrees. Bad types return NotImplemented.
        Propagation of Error
          Function: f = cos(x)
          Variance: sigma_f^2 = ( -sin(x) sigma_x )^2 
        """
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Simplify Inputs
        _self_  = self._simplified_
        # Check No Dimensions
        if(not self._units_.dimensionless()): 
          if(self._units_ == Unit("rad")): log.error("The unit 'rad' is processed as units of radiation. Radians are generally unitless or m/m.")
          raise IncompatibleUnitException("Non-Degree, Non-Dimensionless Units in Trigonometry")
        # Input Value
        x,dx = _self_.value,_self_.error
        # Type Corrections
        x,dx = _type_corrections_(x,dx)
        # Assign Public Values
        new_value = _cos_(x)
        new_error = _sqrt_(_sin_(x)**2 * dx**2)
        new_units = None
        # Assign Private Values
        new_imply = self.implied 
        # Returns
        _measure_ = Measure(value=new_value,error=new_error,units=new_units,imply=new_imply,_base_units_=True)
        # Return (No Preferred Units)
        return _measure_
      
      def __round__(self, n=None):
        """ Returns the rounded number in the current units. 
        The functions round the value and ceil the error for rounding place.
        Caution: Not valid for Propagation of Error.
        Caution: No Conversion to Base Units.
        Bad types return NotImplemented.
        """
        # Set Rounding Place
        if(n!=None):
          if(not isinstance(n, int)): raise TypeError('Second argument should be int.')
        else:
          n = 0
        # Assign Public Values
        new_value = round(self.value,n)
        new_error = _ceil_(self.error*10**n)/(10**n)
        new_units = self.units
        # Assign Private Values
        new_imply = self.implied 
        # Returns
        _measure_ = Measure(value=new_value,error=new_error,units=new_units,imply=new_imply)
        return _measure_
      
      def __floor__(self):
        """ Returns the floor in the current units. 
        The standard python floor function applies as floor(value) and ceil(error).
        Caution: Not valid for Propagation of Error.
        Caution: No Conversion to Base Units.
        Bad types return NotImplemented.
        """
        # Assign Public Values
        new_value = _floor_(self.value)
        new_error = _ceil_(self.error)
        new_units = self.units
        # Assign Private Values
        new_imply = self.implied 
        # Returns
        _measure_ = Measure(value=new_value,error=new_error,units=new_units,imply=new_imply)
        return _measure_
      def __ceil__(self):
        """ Returns the floor in the current units. 
        The standard python floor function applies as ceil(value) and ceil(error).
        Caution: Not valid for Propagation of Error.
        Caution: No Conversion to Base Units.
        Bad types return NotImplemented.
        """
        # Assign Public Values
        new_value = _ceil_(self.value)
        new_error = _ceil_(self.error)
        new_units = self.units
        # Assign Private Values
        new_imply = self.implied 
        # Returns
        _measure_ = Measure(value=new_value,error=new_error,units=new_units,imply=new_imply)
        return _measure_
    
    # Binary Operators
    if(True):
      
      # Addition & Subtraction Operators
      def __add__(self,other):
        """Returns Addition for compatible units. Bad types return NotImplemented.
        Propagation of Error
          Function: f = x + y
          Variance: sigma_f^2 = sigma_x^2 + sigma_y^2
        """
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Convert to Measure
        other = Measure._to_measure_(other)
        # Add Measures
        if(isinstance(other,Measure)):
          # Simplify Inputs
          _self_,_other_  = self._simplified_,other._simplified_
          # Check Dimensions
          if( _self_.value==0 and   _self_.error==0): return other
          if(_other_.value==0 and  _other_.error==0): return self
          if(_self_._units_.symbols != _other_._units_.symbols): raise IncompatibleUnitException("Incompatible Units: "+str(self._units_)+";"+str(_other_._units_))
          # Input Values
          x,dx = _self_.value  , _self_.error
          y,dy = _other_.value , _other_.error
          # Type Corrections
          x,dx,y,dy = _type_corrections_(x,dx,y,dy)
          # Assign Public Values
          new_value = x+y
          new_error = _sqrt_(dx**2 + dy**2)
          new_units = _self_._units_
          # Assign Private Values
          new_imply = self.implied or other.implied
          # Construct Measure
          _measure_ = Measure(value=new_value,error=new_error,units=new_units,imply=new_imply,_base_units_=True)
          
          # If not simple units, Convert
          # If not identical units, simplify 
          non_simple_self  =  _self_._units_._symbols_ != self._units_._symbols_  or  _self_._units_._magnitude_ !=  self._units_._magnitude_
          #non_simple_other = _other_._units_._symbols_ != other._units_._symbols_ or _other_._units_._magnitude_ != other._units_._magnitude_
          identical_units = self._units_._symbols_ == other._units_._symbols_ and self._units_._magnitude_ == other._units_._magnitude_
          #if(identical_units and (non_simple_self or non_simple_other)):
          if(identical_units and non_simple_self):
            try:    return _measure_.convert(self._units_)
            except: return _measure_
          else: return _measure_
        # Failed Types
        return NotImplemented
      __radd__ = __add__
      def __sub__(self,other):
        """Returns Subtraction for compatible units. Bad types return NotImplemented.
        Propagation of Error
          Function: f = x - y
          Variance: sigma_f^2 = sigma_x^2 + sigma_y^2
        """
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Convert to Measure
        other = Measure._to_measure_(other)
        # Subtract Measures
        if(isinstance(other,Measure)):
          # Simplify Inputs
          _self_,_other_  = self._simplified_,other._simplified_
          # Check Dimensions
          if( _self_.value==0 and   _self_.error==0): return other.__neg__()
          if(_other_.value==0 and  _other_.error==0): return self
          if(_self_._units_.symbols != _other_._units_.symbols): raise IncompatibleUnitException("Incompatible Units: "+str(self._units_)+";"+str(_other_._units_))
          # Input Values
          x,dx = _self_.value  , _self_.error
          y,dy = _other_.value , _other_.error
          # Type Corrections
          x,dx,y,dy = _type_corrections_(x,dx,y,dy)
          # Assign Public Values
          new_value = x-y
          new_error = _sqrt_(dx**2 + dy**2)
          new_units = _self_._units_
          # Assign Private Values
          new_imply = self.implied or other.implied
          # Construct Measure
          _measure_ = Measure(value=new_value,error=new_error,units=new_units,imply=new_imply,_base_units_=True)
          # If not simple units, Convert
          # If not identical units, simplify 
          non_simple_self  =  _self_._units_._symbols_ != self._units_._symbols_  or  _self_._units_._magnitude_ !=  self._units_._magnitude_
          #non_simple_other = _other_._units_._symbols_ != other._units_._symbols_ or _other_._units_._magnitude_ != other._units_._magnitude_
          identical_units = self._units_._symbols_ == other._units_._symbols_ and self._units_._magnitude_ == other._units_._magnitude_
          #if(identical_units and (non_simple_self or non_simple_other)):
          if(identical_units and non_simple_self):
            try:    return _measure_.convert(self._units_)
            except: return _measure_
          else: return _measure_
        # Failed Types
        return NotImplemented
      def __rsub__(self, other):
        """Returns Subtraction for compatible units. Bad types return NotImplemented."""
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Convert to Measure
        other = Measure._to_measure_(other)
        # Subtract Measures
        if(isinstance(other,Measure)):
          return other.__sub__(self)
        # Failed Types
        return NotImplemented
      
      # Multiplication & Division Operators
      def __mul__(self,other):
        """Returns Multiplication for compatible units. Bad types return NotImplemented.
        Propagation of Error
          Function: f = x * y
          Variance: sigma_f^2 = y^2 sigma_x^2 + x^2 sigma_y^2
        """
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Convert to Measure
        other = Measure._to_measure_(other)
        # Multiply Measures
        if(isinstance(other,Measure)):
          # Simplify Inputs
          _self_,_other_  = self._simplified_,other._simplified_
          # Input Values
          x,dx = _self_.value  , _self_.error
          y,dy = _other_.value , _other_.error
          # Type Corrections
          x,dx,y,dy = _type_corrections_(x,dx,y,dy)
          # Assign Public Values
          new_value = x*y
          new_error = _sqrt_(y**2 * dx**2 + x**2 * dy**2)
          new_units = _self_._units_ * _other_._units_
          # Assign Private Values
          new_imply = self.implied or other.implied
          # Construct Measure
          _measure_ = Measure(value=new_value,error=new_error,units=new_units,imply=new_imply,_base_units_=True)
          # If simplified units != unsimplified units, Convert
          non_simple_self  =  _self_._units_._symbols_ != self._units_._symbols_  or  _self_._units_._magnitude_ !=  self._units_._magnitude_
          non_simple_other = _other_._units_._symbols_ != other._units_._symbols_ or _other_._units_._magnitude_ != other._units_._magnitude_
          if(non_simple_self or non_simple_other): 
            try:    return _measure_.convert(self._units_*other._units_)
            except: return _measure_
          else: return _measure_
        # Failed Types
        return NotImplemented
      __rmul__ = __mul__
      def __truediv__(self,other):
        """Returns Division for compatible units. Bad types return NotImplemented.
        Propagation of Error
          Function: f = x / y
          Variance: sigma_f^2 = (y^-1 * sigma_x)^2 + ( -x * y^-2 sigma_y )^2
        """
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Convert to Measure
        other = Measure._to_measure_(other)
        # Divide Measures
        if(isinstance(other,Measure)):
          # Simplify Inputs
          _self_,_other_  = self._simplified_,other._simplified_
          # Input Values
          x,dx = _self_.value  , _self_.error
          y,dy = _other_.value , _other_.error
          # Type Corrections
          x,dx,y,dy = _type_corrections_(x,dx,y,dy)
          # Assign Public Values
          new_value = x/y
          new_error = _sqrt_((1/y)**2 * dx**2 + (y**-2 *x)**2 * dy**2)
          new_units = _self_._units_ / _other_._units_
          # Assign Private Values
          new_imply = self.implied or other.implied
          # Construct Measure
          _measure_ = Measure(value=new_value,error=new_error,units=new_units,imply=new_imply,_base_units_=True)
          # If simplified units != unsimplified units, Convert
          non_simple_self  =  _self_._units_._symbols_ != self._units_._symbols_  or  _self_._units_._magnitude_ !=  self._units_._magnitude_
          non_simple_other = _other_._units_._symbols_ != other._units_._symbols_ or _other_._units_._magnitude_ != other._units_._magnitude_
          if(non_simple_self or non_simple_other): 
            try:    return _measure_.convert(self._units_/other._units_)
            except: return _measure_
          else: return _measure_
        # Failed Types
        return NotImplemented
      def __rtruediv__(self,other):
        """Returns Measure / Measure, Unit / Measure, or Decimal / Measure for compatible units. Bad types return NotImplemented.
        Propagation of Error
          Function: f = x / y
          Variance: sigma_f^2 = (y^-1 * sigma_x)^2 + ( -x * y^-2 sigma_y )^2
        """
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Convert to Measure
        other = Measure._to_measure_(other)
        # Divide Measures
        if(isinstance(other,Measure)):
          return other.__truediv__(self)
        # Failed Types
        return NotImplemented
      # def _divide(self,other):
      #def divmod
      def __floordiv__(self,other):
        """ Returns remainder of the of the division. Bad types return NotImplemented.
        Propagation of Error
          Function: f = floor(x / y)
          df/dx = 0 -> _ceil_()
          df/dy = 0 -> _ceil_()
          Variance: sigma_f^2 = ( 0 sigma_x )^2 + ( 0 * sigma_y )^2 = 0 
          Units: 
        """
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Convert to Measure
        other = Measure._to_measure_(other)
        # Divide Measures
        if(isinstance(other,Measure)):
          # Simplify Inputs
          _self_,_other_  = self._simplified_,other._simplified_
          # Input Values
          x,dx = _self_.value  , _self_.error
          y,dy = _other_.value , _other_.error
          # Type Corrections
          x,dx,y,dy = _type_corrections_(x,dx,y,dy)
          # Assign Public Values
          new_value = _floor_(x/y)
          new_error = _sqrt_(_ceil_(dx)**2 + _ceil_(dy)**2)
          new_units = _self_._units_ / _other_._units_
          # Assign Private Values
          new_imply = self.implied or other.implied
          # Construct Measure
          _measure_ = Measure(value=new_value,error=new_error,units=new_units,imply=new_imply,_base_units_=True)
          # If simplified units != unsimplified units, Convert
          if(_self_._units_ != self._units_ or _other_._units_ != other._units_): 
            try:    return _measure_.convert(self._units_/other._units_)
            except: return _measure_
          else: return _measure_
        # Failed Types
        return NotImplemented
        
        
        pass
      def __rfloordiv__(self,other):
        """ Returns remainder of the of the division. Bad types return NotImplemented.
        Propagation of Error
          Function: f = floor(x / y)
          df/dx = 0 -> _ceil_()
          df/dy = 0 -> _ceil_()
          Variance: sigma_f^2 = ( 0 sigma_x )^2 + ( 0 * sigma_y )^2 = 0 
          Units: 
        """
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Convert to Measure
        other = Measure._to_measure_(other)
        # Divide Measures
        if(isinstance(other,Measure)):
          return other.__floordiv__(self)
        # Failed Types
        return NotImplemented
        
      #def __ifloordiv__():
      def __mod__(self,other):
        """ Returns remainder of the of the division. Bad types return NotImplemented.
        Propagation of Error
          Function: f = x % y = x-y*floor(x/y)
          df/dx = 1 - y * d/dx floor(x/y) = 1 - y * 0 * d/dx(x/y)  = 1 - y * 0 * d/dx(x)/y = 1 - y * 0 * 1/y = 1
          df/dy = 0 - ( y * d/dy(floor(x/y)) + floor(x/y) d/dy(y) ) = 0 - ( y*0 + floor(x/y) ) = - floor(x/y)
          Variance: sigma_f^2 = ( 1 sigma_x )^2 + ( -floor(x/y) * sigma_y )^2
          Units: 
        """
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Convert to Measure
        other = Measure._to_measure_(other)
        # Modulo Measures
        if(isinstance(other,Measure)):
          # Simplify Inputs
          _self_,_other_  = self._simplified_,other._simplified_
          # Input Values
          x,dx = _self_.value  , _self_.error
          y,dy = _other_.value , _other_.error
          # Type Corrections
          x,dx,y,dy = _type_corrections_(x,dx,y,dy)
          # Assign Public Values
          new_value = x-y*_floor_(x/y)
          new_error = _sqrt_(dx**2 - _floor_(x/y)**2 * dy**2)
          new_units = _self_._units_
          # Assign Private Values
          new_imply = self.implied or other.implied
          # Construct Measure
          _measure_ = Measure(value=new_value,error=new_error,units=new_units,imply=new_imply,_base_units_=True)
          # If simplified units != unsimplified units, Convert
          if(self._units_ != self._units_): 
            try:    return _measure_.convert(self._units_)
            except: return _measure_
          else: return _measure_
        # Failed Types
        return NotImplemented
        
        pass 
      def __rmod__(self,other):
        """ Returns remainder of the of the division. Bad types return NotImplemented.
        Propagation of Error
          Function: f = x % y = x-y*floor(x/y)
          df/dx = 1 - y * d/dx floor(x/y) = 1 - y * 0 * d/dx(x/y)  = 1 - y * 0 * d/dx(x)/y = 1 - y * 0 * 1/y = 1
          df/dy = 0 - ( y * d/dy(floor(x/y)) + floor(x/y) d/dy(y) ) = 0 - ( y*0 + floor(x/y) ) = - floor(x/y)
          Variance: sigma_f^2 = ( 1 sigma_x )^2 + ( -floor(x/y) * sigma_y )^2
          Units: 
        """
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Convert to Measure
        other = Measure._to_measure_(other)
        # Divide Measures
        if(isinstance(other,Measure)):
          return other.__mod__(self)
        # Failed Types
        return NotImplemented
      
      # Exponent Operators
      def __pow__(self,other):
        """Returns Exponential for compatible units. Bad types return NotImplemented.
        Propagation of Error
          Function: f = x^y
          Variance: sigma_f^2 = (y x^(y-1) * sigma_x)^2 + ( x^y ln(x) sigma_y )^2
        """
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Convert to Measure
        other = Measure._to_measure_(other)
        # Exponent Measures
        if(isinstance(other,Measure)):
          # Simplify Inputs
          _self_,_other_  = self._simplified_,other._simplified_
          # Check Dimensions
          #if(not _other_._units_.dimensionless()): raise IncompatibleUnitException("Exponent not Dimensionless")
          # Input Values
          x,dx = _self_.value  , _self_.error
          y,dy = _other_.value , _other_.error
          # Type Corrections
          x,dx,y,dy = _type_corrections_(x,dx,y,dy)
          # Assign Public Values
          new_value = x**y
          new_error = _sqrt_((y * x**(y-1) )**2 * dx**2 + (x**y * _ln_(x))**2 * dy**2)
          new_units = _self_._units_ ** y
          # Assign Private Values
          new_imply = self.implied or other.implied
          # Construct Measure
          _measure_ = Measure(value=new_value,error=new_error,units=new_units,imply=new_imply,_base_units_=True)
          # If simplified units != unsimplified units, Convert
          non_simple_self  =  _self_._units_._symbols_ != self._units_._symbols_  or  _self_._units_._magnitude_ !=  self._units_._magnitude_
          if(non_simple_self): 
            try:    return _measure_.convert(self._units_**y)
            except: return _measure_
          else: return _measure_
        # Failed Types
        return NotImplemented
      def __rpow__(self,other):
        """Returns Exponential for compatible units. Bad types return NotImplemented.
        Propagation of Error
          Function: f = x^y
          Variance: sigma_f^2 = (y x^(y-1) * sigma_x)^2 + ( x^y ln(x) sigma_y )^2
        """
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Convert to Measure
        other = Measure._to_measure_(other)
        # Exponent Measures
        if(isinstance(other,Measure)):
          return other.__pow__(self)
        # Failed Types
        return NotImplemented
      def exp(self):
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Note: This Decimal is handled in __pow__ and required if self.value is Decimal
        return Decimal(math.e) ** self
      def root(self):
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Note: This Decimal is handled in __pow__ and required if self.value is Decimal
        return self ** Decimal("0.5")
      def sqrt(self):
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Note: This Decimal is handled in __pow__ and required if self.value is Decimal
        return self ** Decimal("0.5")
      
      # 
      @staticmethod
      def log(argument,base=10):
        """ Returns logarithm of the argument with respect to the base for compatible units. Bad types return NotImplemented.
        Propagation of Error
          Function: f = log_y(x) = ln(x)/ln(y)
          Variance: sigma_f^2 = ( (x ln(y))^-1 sigma_x)^2 + ( -ln(x) / (y ln(y)^2) sigma_y)^2
        """
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Convert to Measure
        argument = Measure._to_measure_(argument)
        base     = Measure._to_measure_(base)
        # Logarithm of Measure
        if(isinstance(base,Measure) and isinstance(argument,Measure)):
          # Simplify Inputs
          _arg_,_base_  = argument._simplified_,base._simplified_
          # Input Value
          x,dx = _arg_.value , _arg_.error
          y,dy = _base_.value, _base_.error
          # Type Corrections
          x,dx,y,dy = _type_corrections_(x,dx,y,dy)
          # Output Value
          df = _sqrt_((_ln_(y)**-1 * x**-1)**2 * dx**2 + (_ln_(x) * y**-1 * _ln_(y)**-2)**2 * dy**2)
          f  = _ln_(x) / _ln_(y)
          # Check Dimensions
          if(not _base_._units_.dimensionless() or not _arg_._units_.dimensionless() ): 
            if(_base_._units_**f != _arg_._units_): raise IncompatibleUnitException("The base and argument of the logarithm have Incompatible Units")
          # Assign Public Values
          new_value = f
          new_error = df
          new_units = None
          # Assign Private Values
          new_imply = argument.implied or base.implied
          # Construct Measure
          _measure_ = Measure(value=new_value,error=new_error,units=new_units,imply=new_imply,_base_units_=True)
          # Return Measure
          return _measure_
        # Failed Types
        return NotImplemented
      def ln(self):
        """ Returns logarithm of the argument with respect to Euler's constant for compatible units. Bad types return NotImplemented."""
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Note: This Decimal is handled in log and required if self.value is Decimal
        return Measure.log(self,base=Decimal(math.e))
      def log10(self):
        """ Returns logarithm of the argument with respect to ten for compatible units. Bad types return NotImplemented."""
        # Note: Number Type-Handling is all preformed in Measure._to_measure_(other), not in the individual operator function. 
        # Note: This Decimal is handled in log and required if self.value is Decimal
        return Measure.log(Decimal("10"),self)
      
    # remainder_near
    # ToDo TODO to-do todo
    # Do I want to handle complex numbers and if so, what's that gonna come along with?
    # Given that they're basically just units that are kept separate until they aren't is this an issue?
    @property
    def real(self):
      pass
      #return self
    @property
    def imag(self):
      pass
      #return 
    #def conjugate(self):
    
    #def __complex__(self):
    #def max(self, other):
    #def min(self, other):
    #_isinteger
    #_iseven
    #def compare(self, other):
    #def _cmp(self, other):
    
    def __bool__(self):
      return bool(self.value)
    def __float__(self):
      return float(self.value)
    def __int__(self):
      return int(self.value)
    
Number.register(Measure)

if (__name__ == "__main__"):
  if(main_args.test):
    pass