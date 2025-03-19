// Explorer detector (approximate)
// Properties as listed in https://jnm.snmjournals.org/content/early/2020/10/23/jnumed.120.250597

#ifndef UmiDetector_h
#define UmiDetector_h 1

#include "G4VPhysicalVolume.hh"
#include "G4SystemOfUnits.hh"
#include "EnergyCounter.h"

class UmiPanoramaDetector
{
  public:
    static G4VPhysicalVolume* Construct( std::string Name, G4LogicalVolume* worldLV, std::string Mode, EnergyCounter * Counter, G4double LengthMM=1480.0, std::string Material="LYSO" );
    static G4int NRingsInLength( G4double const Length );
    static G4double LengthForNRings( G4int const NRings );

  private:
    // Single crystal (square prism)
    static G4double constexpr crystalWidth = 2.76*mm / 2.0; // half because it's measured from middle to face
    static G4double constexpr crystalLength = 18.1*mm / 2.0;

    // 6x7 mini-blocks of crystals, 14x5 blocks
    static G4double constexpr blockAxial = crystalWidth * 24.0;
    static G4double constexpr blockTrans = crystalWidth * 24.0;

    // Space between rings
    static G4double constexpr blockOffset = 2.2*mm;
};

#endif
