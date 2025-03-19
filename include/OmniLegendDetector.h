#ifndef OmniLegendDetector_h
#define OmniLegendDetector_h 1

#include "G4VPhysicalVolume.hh"
#include "G4SystemOfUnits.hh"

class EnergyCounter;

class OmniLegendDetector
{
public:
    static G4VPhysicalVolume* Construct(std::string Name, G4LogicalVolume* worldLV, std::string Mode, EnergyCounter* Counter = nullptr, G4double LengthMM = 1280, std::string Material = "BGO");
    static G4int NRingsInLength(G4double const Length);
    static G4double LengthForNRings(G4int const NRings);

private:
    // Single crystal (square prism)
    static G4double constexpr crystalWidth = 4.1 * mm / 2.0; // half because it's measured from middle to face
    static G4double constexpr crystalLength = 30 * mm / 2.0;

    // 6x7 mini-blocks of crystals, 14x5 blocks
    static G4double constexpr blockAxial = crystalWidth * 12.0;
    static G4double constexpr blockTrans = crystalWidth * 24.0;

    // Space between rings
    static G4double constexpr blockOffset = 4.96 * mm; // this is between blocks, unsure if needed
};

#endif