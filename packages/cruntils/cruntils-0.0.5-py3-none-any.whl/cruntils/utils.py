
# Core Python imports.
from enum import Enum
import math

#------------------------------------------------------------------------------
# Constants.
pi2 = (2 * math.pi)
ft_per_metre = 3.28084

class EUnits(Enum):
    Degrees = 1
    Radians = 2

#------------------------------------------------------------------------------
# Trig identities.

def Cos2(angle):
    return math.pow(math.cos(angle), 2)

def Cos3(angle):
    return math.pow(math.cos(angle), 3)

def Cos4(angle):
    return math.pow(math.cos(angle), 4)

def Cos5(angle):
    return math.pow(math.cos(angle), 5)

def Tan2(angle):
    return math.pow(math.tan(angle), 2)

def Tan3(angle):
    return math.pow(math.tan(angle), 3)

def Tan4(angle):
    return math.pow(math.tan(angle), 4)

def Tan5(angle):
    return math.pow(math.tan(angle), 5)

#------------------------------------------------------------------------------
# Miscellaneous.

def DegToRad(degrees):
    """ Convert degrees to radians.
    """
    return (degrees / 180) * math.pi

def RadToDeg(radians):
    """ Convert radians to degrees.
    """
    return (radians / math.pi) * 180

def Circumference(radius):
    """ Circumference of a circle.
    """
    return 2 * math.pi * radius

def MetresToFeet(metres):
    return metres * ft_per_metre

def FeetToMetres(feet):
    return feet / ft_per_metre