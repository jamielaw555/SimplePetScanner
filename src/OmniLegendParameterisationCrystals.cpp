#include "OmniLegendParameterisationCrystals.h"

#include "G4ThreeVector.hh"
#include "G4RotationMatrix.hh"
#include "G4SystemOfUnits.hh"
#include "G4LogicalVolume.hh"
#include "G4VisAttributes.hh"

OmniLegendParameterisationCrystals::OmniLegendParameterisationCrystals( G4int nCopies )
{
  // Precalculating everything avoids a memory leak
  m_positions.reserve( nCopies );
  m_rotations.reserve( nCopies );
  m_visions.reserve( nCopies );

  for ( G4int copyNo = 0; copyNo < nCopies; ++copyNo )
  {
    // 4 rings in the detector
    G4int const crystalsPerRing = 6336;
    // 7 blocks (cells) axially and 34 transaxially
    G4int const blocksPerRing = 22;
    G4int const ring = floor( copyNo / crystalsPerRing ); //indexes the ring that the crystal is in 

    G4int const nRings = ceil( nCopies / crystalsPerRing ); //number of rings total based on crystal no
    G4int const inRing = copyNo % crystalsPerRing; // Position within ring using remainder

    // 38 detector blocks per ring
    G4int const crystalsPerBlock = 288;
    G4int const block = floor( inRing / crystalsPerBlock );
    G4int const inBlock = inRing % crystalsPerBlock;

    // mini-blocks are 5x5 crystals, arranged into 2x4 blocks (2 in the axial direction I think)
    // blocks are therefore 10x20
    G4int const crystalsBlockAxial = 12;
    G4int const crystalsBlockTrans = 24;
    G4int const blockTrans = floor( inBlock / crystalsBlockAxial );
    G4int const blockAxial = inBlock % crystalsBlockAxial;

    // Phi position is block within ring
    G4double const deltaPhi = 360.0 * deg / G4double( blocksPerRing );
    G4double const phi = deltaPhi * G4double( block );

    // Z position is ring itself
    G4double const crystalWidth = 4.1 * mm;
    G4double const ringWidth = crystalWidth * crystalsBlockAxial;
    //G4double const z = ( G4double( ring ) - G4double( nRings - 1 ) / 2.0 ) * ( ringWidth + 1*mm ); // +1mm for easy view
    G4double const z = ( G4double( ring ) - G4double( nRings - 1 ) / 2.0 ) * ringWidth; // offset to get it centred

    // Adjust Z position for the block axial
    //G4double const dZ = ( crystalWidth + 1*mm ) * ( blockAxial - ( crystalsBlockAxial / 2.0 ) ); // +1mm for easy view
    G4double const dZ = crystalWidth * ( blockAxial - ( crystalsBlockAxial / 2.0 ) );

    // Adjust phi position for block transaxial
    G4double const r = 37.77 * cm; // 76cm "Detector ring diameter" "Transaxial FOV"
    //G4double const ta = ( crystalWidth + 1*mm ) * ( blockTrans - ( crystalsBlockTrans / 2.0 ) ); // +1mm for easy view
    G4double const ta = crystalWidth * ( blockTrans - ( crystalsBlockTrans / 2.0 ) );
    G4double const dPhi = atan2( ta, r );

    // The r also adjusts because the detector blocks are flat (I assume)
    G4double const dR = ta * sin( dPhi ) / 2.0;

    // Set the translation
    G4ThreeVector position;
    position.setRhoPhiZ( r + dR, phi + dPhi, z + dZ );
    m_positions.push_back( position );

    // Set the rotation
    G4RotationMatrix * rotation = new G4RotationMatrix();
    rotation->rotateZ( -phi );
    m_rotations.push_back( rotation );

    // Visual properties
    G4VisAttributes* vis = new G4VisAttributes();
    //vis->SetColor( 0.0, G4double( copyNo ) / G4double( nCopies ), 0.0, 1.0 );
    vis->SetColor( 0.0, G4double( rand() % nCopies ) / G4double( nCopies ), 0.0, 1.0 );
    m_visions.push_back( vis );
  }
}

void OmniLegendParameterisationCrystals::ComputeTransformation( const G4int copyNo, G4VPhysicalVolume* physVol ) const
{
  if ( copyNo >= ( G4int )m_positions.size() )
  {
    G4cerr << "Unknown copyNo for OmniLegendParameterisationCrystals: " << copyNo << G4endl;
    return;
  }

  // Return precalculated result
  physVol->SetTranslation( m_positions.at( copyNo ) );
  physVol->SetRotation( m_rotations.at( copyNo ) );
  physVol->GetLogicalVolume()->SetVisAttributes( m_visions.at( copyNo ) );
}
