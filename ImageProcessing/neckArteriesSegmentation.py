# Author: Gustavo Solcia
# E-mail: gustavo.solcia@usp.br

"""Neck arteries atropos segmentation with otsu masking and gamma correction.

"""

import os 
import ants
import numpy as np
import SimpleITK as sitk
from skimage import exposure

def createMask(image):
    """Create a simple threshold mask just to use as input in the segmentation.
    
    Parameters
    ----------
    image: sitkImage
        We expect a sitkImage from sitkReadImage.

    Returns
    -------
    mask: sitkImage
        Threshold mask.

    """
    
    otsuFilter = sitk.OtsuThresholdImageFilter()
    otsuFilter.SetInsideValue(0)
    otsuFilter.SetOutsideValue(1)
    mask = otsuFilter.Execute(image)

    return mask

def adjustGamma(image):

    """ Gamma constrast transformation with scikit-image.

    Parameters
    ----------
    image: sitkImage
        We expect a sitkImage.

    Returns
    -------
    imageGamma: sitkImage
        Image with new contrast.

    """
    
    imageArray = sitk.GetArrayFromImage(image)
    
    gammaArray = exposure.adjust_gamma(imageArray,1.9)

    gammaImage = copySITKInfo2NewImage(image, gammaArray)

    return gammaImage


def convertSitkToAnts(sitkImage):

    """Conversor of sitkImage to antsImage.
    Parameters
    -----------
    sitkImage: sitkImage
        Image desired to convert.
    Returns
    --------
    antsImage: antsImage
        Converted image.
    """

    array = sitk.GetArrayFromImage(sitkImage)
    antsImage = ants.from_numpy(array.astype('float32'))

    return antsImage

def getSegmentationArray(antsImage, antsMask):

    """Atropos segmentation from Advanced Normalization Tools returned as a numpy array.
    Parameters
    ----------
    antsImage: antsImage
        Image you want to apply segmentation.
    antsMask: antsImage
        Mask used on atropos segmentation.
    Returns
    -------
    segmentationArray: array
        Segmented image on array with corrected axis.
    """

    segmentationAnts = ants.atropos(a=antsImage, m='[0.1, 1x1x1]', c='[50, 0.0001]',
                                i='kmeans[2]', p='Socrates[1]', x=antsMask)

    segmentationArray = segmentationAnts['segmentation'].numpy()

    return segmentationArray

def copySITKInfo2NewImage(sitkImage, array):
    """Function to copy sitkImage info to new sitk image based on array.

    Parameters
    ----------
    sitkImage: sitkImage
        sitkImage (usually the input) that we use to copy information.
    array: array
        Numpy array you want to convert.

    """

    newSitkImage = sitk.GetImageFromArray(array)
    newSitkImage.CopyInformation(sitkImage)

    return newSitkImage

def writeArrayImage(dataPath, sitkImage, array):

    """Image writing operation with array conversion.
    Parameters
    ----------
    dataPath: string
        String containing a path to the directory + the data name.
    sitkImage: sitkImage
        sitkImage (usually the input) that we use to copy information.
    array: array
        Numpy array you want to save.
    """

    newSitkImage = copySITKInfo2NewImage(sitkImage, array)

    standard_writer = sitk.ImageFileWriter()
    standard_writer.SetFileName(dataPath)
    standard_writer.Execute(newSitkImage)

if __name__ == "__main__":

    path = os.path.abspath("...")
    inputName = '...'
    outputName = '...' #The forward slash is necessary to path+*Name work!

    sitkImage = sitk.ReadImage(path+inputName)
   
    maskImage = createMask(sitkImage)
    
    gammaImage = adjustGamma(sitkImage)

    gammaArray = sitk.GetArrayFromImage(gammaImage)

    antsMask = convertSitkToAnts(maskImage)
    antsImage = convertSitkToAnts(gammaImage)

    segmentationArray = getSegmentationArray(antsImage, antsMask)

    writeArrayImage(path+outputName, sitkImage, segmentationArray)
