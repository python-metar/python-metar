#
#  Python classes to represent dimensioned quantities used in weather reports
#
#  Copyright 2004  Tom Pollard
# 
import re
from math import sin, cos, atan2, sqrt

## exceptions

class UnitsError(Exception):
  """Exception raised when unrecognized units are used."""
  pass

## regexp to match fractions (used by distance class)
## [Note: numerator of fraction must be single digit.]

FRACTION_RE = re.compile(r"^((?P<int>\d+)\s*)?(?P<num>\d)/(?P<den>\d+)$")
  
## classes representing dimensioned values in METAR reports
    
class temperature(object):
  """A class representing a temperature value."""
  legal_units = [ "F", "C", "K" ]
  
  def __init__( self, value, units="C" ):
    if not units.upper() in temperature.legal_units:
      raise UnitsError("unrecognized temperature unit: '"+units+"'")
    self._units = units.upper()
    try:
      self._value = float(value)
    except ValueError:
      if value.startswith('M'):
        self._value = -float(value[1:])
      else:
        raise ValueError("temperature must be integer: '"+str(value)+"'")

  def __str__(self):
    return self.string()
    
  def value( self, units=None ):
    """Return the temperature in the specified units."""
    if units == None:
      return self._value
    else:
      if not units.upper() in temperature.legal_units:
        raise UnitsError("unrecognized temperature unit: '"+units+"'")
      units = units.upper()
    if self._units == "C":
      celsius_value = self._value
    elif self._units == "F":
      celsius_value = (self._value-32.0)/1.8
    elif self._units == "K":
      celsius_value = self._value-273.15
    if units == "C":
        return celsius_value
    elif units == "K":
        return 273.15+celsius_value
    elif units == "F":
      return 32.0+celsius_value*1.8
      
  def string( self, units=None ):
    """Return a string representation of the temperature, using the given units."""
    if units == None:
      units = self._units
    else:
      if not units.upper() in temperature.legal_units:
        raise UnitsError("unrecognized temperature unit: '"+units+"'")
      units = units.upper()
    val = self.value(units)
    if units == "C":
      return "%.1f C" % val
    elif units == "F":
      return "%.1f F" % val
    elif units == "K":
      return "%.1f K" % val

class pressure(object):
  """A class representing a barometric pressure value."""
  legal_units = [ "MB", "HPA", "IN" ]
  
  def __init__( self, value, units="MB" ):
    if not units.upper() in pressure.legal_units:
      raise UnitsError("unrecognized pressure unit: '"+units+"'")
    self._value = float(value)
    self._units = units.upper()

  def __str__(self):
    return self.string()
    
  def value( self, units=None ):
    """Return the pressure in the specified units."""
    if units == None:
      return self._value
    else:
      if not units.upper() in pressure.legal_units:
        raise UnitsError("unrecognized pressure unit: '"+units+"'")
      units = units.upper()
    if units == self._units:
      return self._value
    if self._units == "IN":
      mb_value = self._value*33.86398
    else:
      mb_value = self._value
    if units == "MB" or units == "HPA":
      return mb_value
    elif units == "IN":
        return mb_value/33.86398
    else:
      raise UnitsError("unrecognized pressure unit: '"+units+"'")
      
  def string( self, units=None ):
    """Return a string representation of the pressure, using the given units."""
    if not units:
      units = self._units
    else:
      if not units.upper() in pressure.legal_units:
        raise UnitsError("unrecognized pressure unit: '"+units+"'")
      units = units.upper()
    val = self.value(units)
    if units == "MB":
      return "%.1f mb" % val
    elif units == "HPA":
      return "%.1f hPa" % val
    elif units == "IN":
      return "%.2f inches" % val

class speed(object):
  """A class representing a wind speed value."""
  legal_units = [ "KT", "MPS", "KMH", "MPH" ]
  legal_gtlt = [ ">", "<" ]
  
  def __init__( self, value, units=None, gtlt=None ):
    if not units:
      self._units = "MPS"
    else:
      if not units.upper() in speed.legal_units:
        raise UnitsError("unrecognized speed unit: '"+units+"'")
      self._units = units.upper()
    if gtlt and not gtlt in speed.legal_gtlt:
      raise ValueError("unrecognized greater-than/less-than symbol: '"+gtlt+"'")
    self._gtlt = gtlt
    self._value = float(value)

  def __str__(self):
    return self.string()
    
  def value( self, units=None ):
    """Return the pressure in the specified units."""
    if not units:
      return self._value
    else:
      if not units.upper() in speed.legal_units:
        raise UnitsError("unrecognized speed unit: '"+units+"'")
      units = units.upper()
    if units == self._units:
      return self._value
    if self._units == "KMH":
      mps_value = self._value/3.6
    elif self._units == "KT":
      mps_value = self._value*0.514444
    elif self._units == "MPH":
      mps_value = self._value*0.447000
    else:
      mps_value = self._value
    if units == "KMH":
      return mps_value*3.6
    elif units == "KT":
      return mps_value/0.514444
    elif units == "MPH":
      return mps_value/0.447000
    elif units == "MPS":
      return mps_value
      
  def string( self, units=None ):
    """Return a string representation of the speed in the given units."""
    if not units:
      units = self._units
    else:
      if not units.upper() in speed.legal_units:
        raise UnitsError("unrecognized speed unit: '"+units+"'")
      units = units.upper()
    val = self.value(units)
    if units == "KMH":
      text = "%.0f km/h" % val
    elif units == "KT":
      text = "%.0f knots" % val
    elif units == "MPH":
      text = "%.0f mph" % val
    elif units == "MPS":
      text = "%.0f mps" % val
    if self._gtlt == ">":
      text = "greater than "+text
    elif self._gtlt == "<":
      text = "less than "+text
    return text


class distance(object):
  """A class representing a distance value."""
  legal_units = [ "SM", "MI", "M", "KM", "FT" ]
  legal_gtlt = [ ">", "<" ]
  
  def __init__( self, value, units=None, gtlt=None ):
    if not units:
      self._units = "M"
    else:
      if not units.upper() in distance.legal_units:
        raise UnitsError("unrecognized distance unit: '"+units+"'")
      self._units = units.upper()
    
    try:
      if value.startswith('M'):
        value = value[1:]
        gtlt = "<"
      elif value.startswith('P'):
        value = value[1:]
        gtlt = ">"
    except:
      pass
    if gtlt and not gtlt in distance.legal_gtlt:
      raise ValueError("unrecognized greater-than/less-than symbol: '"+gtlt+"'")
    self._gtlt = gtlt
    try:
      self._value = float(value)
      self._num = None
      self._den = None
    except ValueError:
      mf = FRACTION_RE.match(value)
      if not mf:
        raise ValueError("distance is not parseable: '"+str(value)+"'")
      df = mf.groupdict()
      self._num = int(df['num'])
      self._den = int(df['den'])
      self._value = float(self._num)/float(self._den)
      if df['int']:
        self._value += float(df['int'])

  def __str__(self):
    return self.string()
    
  def value( self, units=None ):
    """Return the distance in the specified units."""
    if not units:
      return self._value
    else:
      if not units.upper() in distance.legal_units:
        raise UnitsError("unrecognized distance unit: '"+units+"'")
      units = units.upper()
    if units == self._units:
      return self._value
    if self._units == "SM" or self._units == "MI":
      m_value = self._value*1609.344
    elif self._units == "FT":
      m_value = self._value/3.28084
    elif self._units == "KM":
      m_value = self._value*1000
    else:
      m_value = self._value
    if units == "SM" or units == "MI":
      return m_value/1609.344
    elif units == "FT":
      return m_value*3.28084
    elif units == "KM":
      return m_value/1000
    elif units == "M":
      return m_value
      
  def string( self, units=None ):
    """Return a string representation of the distance in the given units."""
    if not units:
      units = self._units
    else:
      if not units.upper() in distance.legal_units:
        raise UnitsError("unrecognized distance unit: '"+units+"'")
      units = units.upper()
    if self._num and self._den and units == self._units:
      val = int(self._value - self._num/self._den)
      if val:
        text = "%d %d/%d" % (val, self._num, self._den)
      else:
        text = "%d/%d" % (self._num, self._den)
    else:
      if units == "KM":
        text = "%.1f" % self.value(units)
      else:
        text = "%.0f" % self.value(units)
    if units == "SM" or units == "MI":
      text += " miles"
    elif units == "M":
      text += " meters"
    elif units == "KM":
      text += " km"
    elif units == "FT":
      text += " feet"
    if self._gtlt == ">":
      text = "greater than "+text
    elif self._gtlt == "<":
      text = "less than "+text
    return text


class direction(object):
  """A class representing a compass direction."""
  
  compass_dirs = { "N":  0.0, "NNE": 22.5, "NE": 45.0, "ENE": 67.5, 
                   "E": 90.0, "ESE":112.5, "SE":135.0, "SSE":157.5,
                   "S":180.0, "SSW":202.5, "SW":225.0, "WSW":247.5,
                   "W":270.0, "WNW":292.5, "NW":315.0, "NNW":337.5 }

  def __init__( self, d ):
    if direction.compass_dirs.has_key(d):
      self._compass = d
      self._degrees = direction.compass_dirs[d]
    else:
      self._compass = None
      value = float(d)
      if value < 0.0 or value > 360.0:
        raise ValueError("direction must be 0..360: '"+str(value)+"'")
      self._degrees = value

  def __str__(self):
    return self.string()
      
  def value( self ):
    """Return the numerical direction, in degrees."""
    return self._degrees
    
  def string( self ):
    """Return a string representation of the numerical direction."""
    return "%.0f degrees" % self._degrees
    
  def compass( self ):
    """Return the compass direction, e.g., "N", "ESE", etc.)."""
    if not self._compass:
      degrees = 22.5 * round(self._degrees/22.5)
      if degrees == 360.0:
        self._compass = "N"
      else:
        for name, d in direction.compass_dirs.iteritems():
          if d == degrees:
            self._compass = name
            break
    return self._compass


class precipitation(object):
  """A class representing a precipitation value."""
  legal_units = [ "IN", "CM" ]
  legal_gtlt = [ ">", "<" ]
  
  def __init__( self, value, units=None, gtlt=None ):
    if not units:
      self._units = "IN"
    else:
      if not units.upper() in precipitation.legal_units:
        raise UnitsError("unrecognized precipitation unit: '"+units+"'")
      self._units = units.upper()
    
    try:
      if value.startswith('M'):
        value = value[1:]
        gtlt = "<"
      elif value.startswith('P'):
        value = value[1:]
        gtlt = ">"
    except:
      pass
    if gtlt and not gtlt in precipitation.legal_gtlt:
      raise ValueError("unrecognized greater-than/less-than symbol: '"+gtlt+"'")
    self._gtlt = gtlt
    self._value = float(value)

  def __str__(self):
    return self.string()
    
  def value( self, units=None ):
    """Return the precipitation in the specified units."""
    if not units:
      return self._value
    else:
      if not units.upper() in precipitation.legal_units:
        raise UnitsError("unrecognized precipitation unit: '"+units+"'")
      units = units.upper()
    if units == self._units:
      return self._value
    if self._units == "CM":
      i_value = self._value*2.54
    else:
      i_value = self._value
    if units == "CM":
      return i_value*2.54
    else:
      return i_value
      
  def string( self, units=None ):
    """Return a string representation of the precipitation in the given units."""
    if not units:
      units = self._units
    else:
      if not units.upper() in precipitation.legal_units:
        raise UnitsError("unrecognized precipitation unit: '"+units+"'")
      units = units.upper()
    text = "%.2f" % self.value(units)
    if units == "CM":
      text += "cm"
    else:
      text += "in"
    if self._gtlt == ">":
      text = "greater than "+text
    elif self._gtlt == "<":
      text = "less than "+text
    return text


class position(object):
  """A class representing a location on the earth's surface."""
   
  def __init__( self, latitude=None, longitude=None ):
    self.latitude = latitude
    self.longitude = longitude

  def __str__(self):
    return self.string()
   
  def getdistance( self, position2 ):
    """
    Calculate the great-circle distance to another location using the Haversine
    formula.  See <http://www.movable-type.co.uk/scripts/LatLong.html>
    and <http://mathforum.org/library/drmath/sets/select/dm_lat_long.html>
    """
    earth_radius = 637100.0
    lat1 = self.latitude
    long1 = self.longitude
    lat2 = position2.latitude
    long2 = position2.longitude
    a = sin(0.5(lat2-lat1)) + cos(lat1)*cos(lat2)*sin(0.5*(long2-long1)**2)
    c = 2.0*atan(sqrt(a)*sqrt(1.0-a))
    d = distance(earth_radius*c,"M")
    return d

  def getdirection( self, position2 ):
    """
    Calculate the initial direction to another location.  (The direction
    typically changes as you trace the great circle path to that location.)
    See <http://www.movable-type.co.uk/scripts/LatLong.html>.
    """
    lat1 = self.latitude
    long1 = self.longitude
    lat2 = position2.latitude
    long2 = position2.longitude
    s = -sin(long1-long2)*cos(lat2)
    c = cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(long1-long2)
    d = atan2(s,c)*180.0/math.pi
    if d < 0.0: d += 360.0
    return direction(d)

