import math

import PhysicsConstants as PC

def DetectorRadius():
  return 362.7

def CrystalVolume():
  return 0.41 * 0.41 * 3.0

def CrystalMass( DetectorMaterial ):
  if DetectorMaterial not in PC.densities:
    raise RuntimeError('No density value for this material in PhysicsConstants. Wrong material name?')
  return CrystalVolume() * PC.densities[DetectorMaterial]

def DetectorVolume():
  return CrystalVolume() * 152064.0

def DetectorMass( DetectorMaterial ):
  return CrystalMass(DetectorMaterial) * 152064.0

def DetectorDiscreteLength( Length ):
  nRings = float( math.ceil( Length / 320.0 ) )
  return nRings * 320.0

def DetectorVolumeLength( Length ):
  nRings = float( math.ceil( Length / 320.0 ) )
  return CrystalVolume() * 38016 * nRings

def DetectorMassLength( Length, DetectorMaterial ):
  nRings = float( math.ceil( Length / 320.0 ) )
  return CrystalMass(DetectorMaterial) * 38016 * nRings


# BGO Molar Mass Calculation: Bi₄Ge₃O₁₂
def BGOunitsInMass(Mass):
  BGOmoleGram = (4 * 208.98) + (3 * 72.63) + (12 * 16.00)  # Bi, Ge, O
  print("In function 1")
  NAvogadro = 6.022E23
  return NAvogadro * Mass / BGOmoleGram  # Number of BGO molecules

# Bi-214 activity estimation in BGO
def Bi214atomsInMass(Mass):
  # Assume 10 ppb U/Th contamination in BGO
  traceFraction = 10E-9  # 10 ppb
  return 0

def Bi214decaysInMass(Mass):
  Bi214halfYears = 19.9 / (60 * 60 * 24 * 365.25)  # 19.9 min -> years
  print("In main decay func")
  Bi214halfSec = Bi214halfYears * 3.154E7
  return 0

# Estimate Decay Rate in BGO Volume
def DecaysInVolume(Volume):
  return 50.0 * Volume

def LSOunitsInMass( Mass ):
  yFraction = 0.2
  LSOmoleGram = ((2.0 - yFraction) * 175.0) + (yFraction * 88.9) + 28.1 + (5.0 * 16.0) #Lu 2-x Y x si 1 O 5
  NAvogadro = 6.022E23
  return NAvogadro * Mass / LSOmoleGram

def Lu176atomsInMass( Mass ):
  yFraction = 0.2
  return LSOunitsInMass( Mass ) * (2.0 - yFraction) * 0.026 #2.6% Lu176

def Lu176decaysInMass( Mass ):
  Lu176halfYears = 3.76E10
  Lu176halfSec = Lu176halfYears * 3.154E7
  return Lu176atomsInMass( Mass ) * math.log(2.0) / Lu176halfSec

# does not give consistent answer with above, might be better
def DecaysInVolume( Volume ):
  return 400.0 * Volume

