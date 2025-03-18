import sys
sys.path.append('../analysis/')
import SiemensQuadraProperties as sqp
import ExplorerProperties as ep
import UmiPanoramaProperties as pp
from ActivityTools import *
from SimulationDataset import *

import multiprocessing as mp
mp.set_start_method('fork')
from multiprocessing import Pool
import numpy as np

import matplotlib.pyplot as mpl
params = {'legend.fontsize': 15,
          'legend.title_fontsize': 15,
          'legend.loc': "upper left",
          'axes.labelsize': 15,
          'xtick.labelsize': 15,
          'ytick.labelsize': 15}
mpl.rcParams.update(params)

#Fix random seed for reproducibility, or skip this to allow the results to vary
import random
random.seed( 1234 )

def NECRatTimeF18( tracerData, crystalData, crystalActivity, detectorRadius,
                  phantomLength, simulationWindow=1E-3, coincidenceWindow=4.7E-9, zWindow=325.0,
                  EnergyResolution=0.0, TimeResolution=0.0 ):

    # get volume in cc
    phantomRadius = 20.3 / 2.0
    phantomVolume = phantomRadius * phantomRadius * math.pi * phantomLength / 10.0 # assume length in mm
    
    necrAtTime = []
    truesAtTime = []
    rPlusSAtTime = []
    scattersAtTime = []
    randomsAtTime = []
    # necrStatAtTime = []
    # truesStatAtTime = []
    # rPlusSStatAtTime = []
    activityAtTime = []
    for time in range( 0, 700, 20 ):
        timeSec = float(time) * 60.0
        activity = F18ActivityAtTime( 1100E6, timeSec )

        necr, trues, rPlusS, Scatters, Randoms = DetectedCoincidences( [activity, crystalActivity], [tracerData, crystalData], simulationWindow, coincidenceWindow, detectorRadius, ZMin=-zWindow, ZMax=zWindow, UsePhotonTime=True, EnergyResolution=EnergyResolution, TimeResolution=TimeResolution )
        necrAtTime.append( necr )
        truesAtTime.append( trues )
        rPlusSAtTime.append( rPlusS )
        scattersAtTime.append( Scatters )
        randomsAtTime.append( Randoms )
        activityAtTime.append( activity / phantomVolume )

    return activityAtTime, necrAtTime, truesAtTime, rPlusSAtTime, scattersAtTime, randomsAtTime

# Simulation parameters
phantomLength = 700
datasetSize = 100000
siemensEmin = 435.0
siemensEmax = 585.0
explorerEmin = 430.0
explorerEmax = 645.0
panoramaEmin = 430.0
panoramaEmax = 650.0

# Nominal
detectorMaterial = "LSO"
tracerDataSiemens = CreateDataset( 1024, "Siemens", phantomLength, "LinearF18", datasetSize, siemensEmin, siemensEmax, detectorMaterial )
crystalDataSiemens = CreateDataset( 1024, "Siemens", phantomLength, "Siemens", datasetSize, siemensEmin, siemensEmax, detectorMaterial )
activityAtTimeSiemens, necrAtTimeSiemens, trueAtTimeSiemens, rPlusSAtTimeSiemens, scatterAtTimeSiemens, randomAtTimeSiemens = NECRatTimeF18(
    tracerDataSiemens, crystalDataSiemens, sqp.Lu176decaysInMass( sqp.DetectorMass(detectorMaterial) ), sqp.DetectorRadius(), phantomLength )
mpl.clf()

detectorMaterial = "LYSO"
tracerDataExplorer = CreateDataset( 1850, "Explorer", phantomLength, "LinearF18", datasetSize, explorerEmin, explorerEmax, detectorMaterial )
crystalDataExplorer = CreateDataset( 1850, "Explorer", phantomLength, "Explorer", datasetSize, explorerEmin, explorerEmax, detectorMaterial )
activityAtTimeExplorer, necrAtTimeExplorer, trueAtTimeExplorer, rPlusSAtTimeExplorer, scatterAtTimeExplorer, randomAtTimeExplorer = NECRatTimeF18(
    tracerDataExplorer, crystalDataExplorer, ep.Lu176decaysInMass( ep.DetectorMass(detectorMaterial) ), ep.DetectorRadius(),
    phantomLength )
mpl.clf()
detectorMaterial = "LYSO"
tracerDataPanorama = CreateDataset( 1850, "Panorama", phantomLength, "LinearF18", datasetSize, panoramaEmin, panoramaEmax, detectorMaterial )
crystalDataPanorama = CreateDataset( 1850, "Panorama", phantomLength, "Panorama", datasetSize, panoramaEmin, panoramaEmax, detectorMaterial )
activityAtTimePanorama, necrAtTimePanorama, trueAtTimePanorama, rPlusSAtTimePanorama, scatterAtTimePanorama, randomAtTimePanorama = NECRatTimeF18(
    tracerDataPanorama, crystalDataPanorama, pp.Lu176decaysInMass( pp.DetectorMass(detectorMaterial) ), pp.DetectorRadius(),
    phantomLength )
mpl.clf()

labels = [ "Panorama NECR", "Explorer NECR", "Panorama True", "Explorer True", "Panorama R+S", "Panorama R+S" ]
mpl.plot( activityAtTimePanorama, necrAtTimePanorama, label=labels[0] )
mpl.plot( activityAtTimeExplorer, necrAtTimeExplorer, label=labels[1] )
mpl.plot( activityAtTimePanorama, trueAtTimePanorama, label=labels[2] )
mpl.plot( activityAtTimeExplorer, trueAtTimeExplorer, label=labels[3] )
mpl.plot( activityAtTimePanorama, rPlusSAtTimePanorama, label=labels[4] )
mpl.plot( activityAtTimeExplorer, rPlusSAtTimeExplorer, label=labels[5] )
mpl.legend( labels )
mpl.xlabel( "Activity [Bq/ml]" )
mpl.ylabel( "Counts [/sec]" )
mpl.gcf().set_size_inches(10, 10)
mpl.savefig("PanoramaVsExplorer_woUncert.pdf")

mpl.clf()

def CreateErrorEnvelope( tracerData, crystalData, crystalActivity, detectorRadius,
                         phantomLength, simulationWindow=1E-3, coincidenceWindow=4.7E-9, processes=5,
                         EnergyResolution=0.0, TimeResolution=0.0 ):
    
    # Create the arguments for each process
    arguments = []

    for experiment in range(10):
        arguments.append( ( tracerData, crystalData, crystalActivity, detectorRadius,
                            phantomLength, simulationWindow, coincidenceWindow, 325.0,
                            EnergyResolution, TimeResolution ) )
    
    # Launch a separate process for each detector length
    result = None
    with Pool( processes=processes ) as p:
        result = p.starmap( NECRatTimeF18, arguments )
    
    # Unpack the results
    necrEnvelope = []
    trueEnvelope = []
    rPlusSEnvelope = []
    scatterEnvelope = []
    randomEnvelope = []
    for entry in result:
        necrEnvelope.append( entry[1] )
        trueEnvelope.append( entry[2] )
        rPlusSEnvelope.append( entry[3] )
        scatterEnvelope.append( entry[4] )
        randomEnvelope.append( entry[5] )
    return result[0][0], np.transpose( necrEnvelope ), np.transpose( np.array(trueEnvelope) ), np.transpose( np.array(rPlusSEnvelope) ), np.transpose( np.array(scatterEnvelope) ), np.transpose( np.array(randomEnvelope) )

detectorMaterial = "LYSO"
activityAtTimePanorama, necrEnvelopePanorama, trueEnvelopePanorama, rPlusSEnvelopePanorama, scatterEnvelopePanorama, randomEnvelopePanorama = CreateErrorEnvelope(
    tracerDataPanorama, crystalDataPanorama, pp.Lu176decaysInMass( pp.DetectorMass(detectorMaterial) ),
    pp.DetectorRadius(), phantomLength, EnergyResolution=0.1, TimeResolution=0.5 )

detectorMaterial = "LYSO"
activityAtTimeExplorer, necrEnvelopeExplorer, trueEnvelopeExplorer, rPlusSEnvelopeExplorer, scatterEnvelopeExplorer, randomEnvelopeExplorer = CreateErrorEnvelope(
    tracerDataExplorer, crystalDataExplorer, ep.Lu176decaysInMass( ep.DetectorMass(detectorMaterial) ),
    ep.DetectorRadius(), phantomLength, EnergyResolution=0.1, TimeResolution=0.5 )

def GetMinMaxFromEnvelope( envelope ):
    
    allMax = []
    allMin = []
    allMean = []
    for entry in envelope:
        allMax.append( max(entry) )
        allMin.append( min(entry) )
        allMean.append( np.mean(entry) )

    return allMin, allMax, allMean

necrMinPanorama, necrMaxPanorama, necrMeanPanorama = GetMinMaxFromEnvelope( necrEnvelopePanorama )
trueMinPanorama, trueMaxPanorama, trueMeanPanorama = GetMinMaxFromEnvelope( trueEnvelopePanorama )
rPlusSMinPanorama, rPlusSMaxPanorama, rPlusSMeanPanorama = GetMinMaxFromEnvelope( rPlusSEnvelopePanorama )

necrMinExplorer, necrMaxExplorer, necrMeanExplorer = GetMinMaxFromEnvelope( necrEnvelopeExplorer )
trueMinExplorer, trueMaxExplorer, trueMeanExplorer = GetMinMaxFromEnvelope( trueEnvelopeExplorer )
rPlusSMinExplorer, rPlusSMaxExplorer, rPlusSMeanExplorer = GetMinMaxFromEnvelope( rPlusSEnvelopeExplorer )

labels = [ "Panorama NECR", "Explorer NECR", "Panorama True", "Explorer True", "Panorama R+S", "Explorer R+S" ]
mpl.plot( activityAtTimeSiemens, necrMeanPanorama, label=labels[0] )
mpl.plot( activityAtTimeExplorer, necrMeanExplorer, label=labels[1] )
mpl.plot( activityAtTimeSiemens, trueMeanPanorama, label=labels[2] )
mpl.plot( activityAtTimeExplorer, trueMeanExplorer, label=labels[3] )
mpl.plot( activityAtTimeSiemens, rPlusSMeanPanorama, label=labels[4] )
mpl.plot( activityAtTimeExplorer, rPlusSMeanExplorer, label=labels[5] )
mpl.legend( labels )

mpl.fill_between( activityAtTimeSiemens, necrMinPanorama, necrMaxPanorama, alpha=0.3 )
mpl.fill_between( activityAtTimeExplorer, necrMinExplorer, necrMaxExplorer, alpha=0.3 )
mpl.fill_between( activityAtTimeSiemens, trueMinPanorama, trueMaxPanorama, alpha=0.3 )
mpl.fill_between( activityAtTimeExplorer, trueMinExplorer, trueMaxExplorer, alpha=0.3 )
mpl.fill_between( activityAtTimeSiemens, rPlusSMinPanorama, rPlusSMaxPanorama, alpha=0.3 )
mpl.fill_between( activityAtTimeExplorer, rPlusSMinExplorer, rPlusSMaxExplorer, alpha=0.3 )

mpl.xlabel( "Activity [Bq/ml]" )
mpl.ylabel( "Counts [/sec]" )
mpl.gcf().set_size_inches(10, 10)
mpl.savefig("counts_wEnvelope.pdf")