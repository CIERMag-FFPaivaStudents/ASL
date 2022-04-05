# Author: Gustavo Solcia
# E-mail: gustavo.solcia@usp.br

"""Parallel Rician denoising of multiple phases of ASL acquisition.

"""

import sys

sys.path.append('/home/solcia/Documents/phd/CIERMag-FFPaivaStudents/NLM')

import os
import numpy as np
import nibabel as nib
import SimpleITK as sitk
from multiprocessing.pool import ThreadPool
from modifiedNLM.estimate.noise_estimate import rician_estimate
from modifiedNLM.filter.modified_nl_means import rician_denoise_nl_means

def importPARREC(inputName, dataPath):
    """Wrapper of the nibabel solution of PAR/REC data type import. We aim at importing ASL data and returning phase and control images separately.
    Parameters
    ----------
    inputName: str
        String containing the input data name.
    dataPath: str
        String containing the data path name.

    Returns
    -------
    controlPhase: array
        Control images from the ASL aquisition of the PAR/REC file. 
    inflowPhase: array
        Inflow images from the ASL aquisition of the PAR/REC file.
    baseImage: nibImage
        Base input image in nibabel format.
    """

    #By the time we used the nibabel solution it still was under improvements.
    #Atention: look at your data and be carefull.
    baseImage = nib.load(dataPath+inputName+'.PAR', strict_sort=True)

    data = baseImage.get_fdata()

    dataShape = np.shape(data)
    numberOfPhases = int(dataShape[3]/2)

    controlPhase = data[:,:,:,:numberOfPhases]
    inflowPhase = data[:,:,:,numberOfPhases:]

    return controlPhase, inflowPhase, baseImage


def parallelDenoising(imageArray):
    """Apply the denoising algorithm using python multiprocessing.

    Parameters
    ----------
    imageArray: array
        Image array to be denoised.

    Returns
    -------
    reshapedResults: array
        Denoised image with axis in the proper order.

    """

    numThreads = os.cpu_count()
    numberOfAcquisitions = np.shape(imageArray)[3]

    if numThreads > numberOfAcquisitions:
        numThreads = numberOfAcquisitions

    pool = ThreadPool(processes=numThreads)
    repChunks = np.array_split(imageArray, numThreads, axis=3)
    results = pool.map_async(performCalc, repChunks)
    pool.close()
    pool.join()

    parallelResults = results.get()

    resultsShape = np.shape(parallelResults)

    reshapedResults = np.moveaxis(parallelResults, 0, -1)

    return reshapedResults

def performCalc(imageChunk):
    """Routine to perform denoising calculation in each image chunk from multiprocessing.
    
    Parameters
    ----------
    imageChunk: list
        Chunk from stacked 4D array.
    Returns
    -------
    denoisedChunck: list
        Denoised chunk from NLM denoising.
    """

    chunkLen = np.shape(imageChunk)[3]

    denoisedChunk = []
    for image_idx in range(chunkLen):
        denoisedImage = NLM(imageChunk[:,:,:,image_idx])
        [denoisedChunk.append(result) for result in denoisedImage]

    return denoisedChunk

def NLM(imageData):

    """Wrapper of modified NLM imported from https://github.com/CIERMag-FFPaivaStudents/NLM.

    Parameters
    ----------
    imageData: array
        Numpy array from image desired to denoise. Atention: Be shure your image has Rician noise.

    Returns
    -------
    denoisedData: array
        Denoised array from rician_denoise_nl_means.

    """

    ricianSigma = rician_estimate(imageData)
    patch_kw = dict(patch_size=5,      # 5x5 patches
                patch_distance=6,  # 13x13 search area
                multichannel=False,
                preserve_range=True)
    denoisedData = rician_denoise_nl_means(imageData, h=1.15 * ricianSigma, fast_mode=False,
                           **patch_kw)
    return denoisedData

if __name__ == '__main__':

    inputName = '/...' 
    dataPath = '/...'

    controlPhase, inflowPhase, baseImage = importPARREC(inputName, dataPath)
    
    print("Starting denoising control images...")
    
    denoisedControlPhase = parallelDenoising(controlPhase)

    print("Starting denoising inflow images...")

    denoisedInflowPhase = parallelDenoising(inflowPhase)

    subtraction = denoisedControlPhase - denoisedInflowPhase

    meanSubtraction = np.mean(subtraction, axis=3)

    subtractionImage = nib.Nifti1Image(subtraction, baseImage.affine)
    meanSubtractionImage = nib.Nifti1Image(meanSubtraction, baseImage.affine)

    nib.save(subtractionImage, dataPath+inputName+'_subtraction.nii.gz')
    nib.save(meanSubtractionImage, dataPath+inputName+'_meanSubtraction.nii.gz')
