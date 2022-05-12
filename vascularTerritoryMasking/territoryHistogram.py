#Author: Gustavo Solcia
#E-mail: gustavo.solcia@usp.br

"""Generates perfusion histograms from territory atlas.

"""
import os
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
import seaborn as sns

def getImageData(filePath):
    """Get numpy array with nibabel tools.

    Parameters
    ----------
    filePath: str

    Returns
    -------
    flattenData: array

    """
    
    image = nib.load(filePath)
    data = image.get_fdata()
    flattenData = data.flatten()
    return flattenData

def plotTerritoryHistogram(perfusion, atlas):
    """

    """

    RACA = perfusion[np.where(np.logical_and(atlas>0.9, atlas<1.1))]
    LACA = perfusion[np.where(np.logical_and(atlas>3.9, atlas<4.1))]
    RMCA = perfusion[np.where(np.logical_and(atlas>1.9, atlas<2.1))]
    LMCA = perfusion[np.where(np.logical_and(atlas>4.9, atlas<5.1))]
    RPCA = perfusion[np.where(np.logical_and(atlas>2.9, atlas<3.1))]
    LPCA = perfusion[np.where(np.logical_and(atlas>5.9, atlas<6.1))]
    RSCA = perfusion[np.where(np.logical_and(atlas>6.9, atlas<7.1))]
    LSCA = perfusion[np.where(np.logical_and(atlas>7.9, atlas<8.1))]

    fig, axs = plt.subplots(2,4, figsize=(16,10))
    sns.set_style('ticks')
    sns.set_context('talk')
    axs[0,0].hist(RACA[RACA>0], color='k', bins=64)
    axs[0,0].set_title('RACA')
    axs[1,0].hist(LACA[LACA>0], color='k', bins=64)
    axs[1,0].set_title('LACA')
    axs[0,1].hist(RMCA[RMCA>0], color='k', bins=64)
    axs[0,1].set_title('RMCA')
    axs[1,1].hist(LMCA[LMCA>0], color='k', bins=64)
    axs[1,1].set_title('LMCA')
    axs[0,2].hist(RPCA[RPCA>0], color='k', bins=64)
    axs[0,2].set_title('RPCA')
    axs[1,2].hist(LPCA[LPCA>0], color='k', bins=64)
    axs[1,2].set_title('LPCA')
    axs[0,3].hist(RSCA[RSCA>0], color='k', bins=64)
    axs[0,3].set_title('RSCA')
    axs[1,3].hist(LSCA[LSCA>0], color='k', bins=64)
    axs[1,3].set_title('LSCA')
    plt.show()

def calculatePerfusionSplit(perfusion, atlas):
    """

    """
    
    RACA = perfusion[np.where(np.logical_and(atlas>0.9, atlas<1.1))]
    LACA = perfusion[np.where(np.logical_and(atlas>3.9, atlas<4.1))]
    RMCA = perfusion[np.where(np.logical_and(atlas>1.9, atlas<2.1))]
    LMCA = perfusion[np.where(np.logical_and(atlas>4.9, atlas<5.1))]
    RPCA = perfusion[np.where(np.logical_and(atlas>2.9, atlas<3.1))]
    LPCA = perfusion[np.where(np.logical_and(atlas>5.9, atlas<6.1))]
    RSCA = perfusion[np.where(np.logical_and(atlas>6.9, atlas<7.1))]
    LSCA = perfusion[np.where(np.logical_and(atlas>7.9, atlas<8.1))]

    entireBrainVolume = perfusion[np.where(np.logical_and(atlas>0.9, atlas<8.1))]
    sumEntireBrain = np.sum(entireBrainVolume)

    pRACA = np.sum(RACA)/sumEntireBrain
    pLACA = np.sum(LACA)/sumEntireBrain
    pRMCA = np.sum(RMCA)/sumEntireBrain
    pLMCA = np.sum(LMCA)/sumEntireBrain
    pRPCA = np.sum(RPCA)/sumEntireBrain
    pLPCA = np.sum(LPCA)/sumEntireBrain
    pRSCA = np.sum(RSCA)/sumEntireBrain
    pLSCA = np.sum(LSCA)/sumEntireBrain

    return pRACA, pLACA, pRMCA, pLMCA, pRPCA, pLPCA, pRSCA, pLSCA

if __name__=='__main__':

    nativeAtlasPath = 'data/native_vascular_territory_atlas.nii.gz'
    structAtlasPath = 'data/mask/Vascular_territory_atlas.nii'
    nativePerfusionPath = 'data/ASL/perfusion_calib.nii.gz'
    structPerfusionPath = 'data/struct_perfusion_calib.nii.gz'

    nativeVascularTerritoryAtlas = getImageData(nativeAtlasPath)
    structVascularTerritoryAtlas = getImageData(structAtlasPath)

    nativePerfusion = getImageData(nativePerfusionPath)
    structPerfusion = getImageData(structPerfusionPath)

    plotTerritoryHistogram(nativePerfusion, nativeVascularTerritoryAtlas)

    plotTerritoryHistogram(structPerfusion, structVascularTerritoryAtlas)

    print(calculatePerfusionSplit(nativePerfusion, nativeVascularTerritoryAtlas))

    print(calculatePerfusionSplit(structPerfusion, structVascularTerritoryAtlas))

