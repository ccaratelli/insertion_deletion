#!/usr/bin/python
import numpy as np
import argparse
from functools import partial
import molmod
from molmod.io.xyz import XYZFile
from molmod.ic import bend_angle
from molmod.ic import bond_length
#import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.constants import physical_constants
import json
#from scipy.stats import norm

def main(file_name, start_step, end_step):
    xyz_file = XYZFile(file_name)
    outputName = "bond_angles.dat"
    outFilenameGraph = "bond_anglesGraph"
    frames = xyz_file.geometries[start_step:end_step]

    #atomsi = [[16,222],[222,16,9],[222,16,11],[222,16,33]]  # oxo-site_A
    #atomsi = [[50,221],[221,50,7],[221,50,5],[221,50,60]]  # oxo-site_B
    #atomsi = [[16,222],[50,221],[56,203],[61,180],[13,193],[26,220],[52,219],[31,216],[222,16,9],[222,16,11]]  # oxo-site_B
    #atomsi = [[70,170],[165,68],[170,70,9],[170,70,167],[165,68,5],[165,68,267]]  # site_A
    #atomsi = [[264,263],[265,263],[264,263,262],[264,263,265]]  # methanol-framework
    #atomsi = [[377,378],[377,379],[378,377,379],[378,377,169]]  # methanol - depr
    #atomsi = [[351,352],[359,360],[57,351,352],[37,359,360]]  # methanol - reference
    #atomsi = [[69,168],[69,285],[168,242],[242,243],[69,168,242]]  # mtd-deprotonation site_A 
    atomsi = json.load(open('atoms.txt','r'))
    atoms = [ list(np.array(a)-1) for a in atomsi ]

    bonds  = map(partial(get_bonds, frames), filter(lambda at: len(at) == 2, atoms))
    angles = map(partial(get_angles, frames), filter(lambda at: len(at) == 3, atoms))
    numbers = [np.arange(frames.shape[0])+1]

    allThing = np.concatenate((numbers, bonds, angles))
    np.savetxt(outputName,np.transpose(allThing))
    plotBonds_Angles(outFilenameGraph, allThing, atomsi)

def plotBonds_Angles(outFilename, allThing, atomsi):
    ''' 
    Save files with data as a function of time and histogram
    '''
    (num,steps) = allThing.shape
    for i in range(1, num):
        # Define the histogram and shift the bins to have data on the centres
        hist, bin_edges = np.histogram(allThing[i], bins=50, density=True)
        bin_centres = (bin_edges[:-1] + bin_edges[1:])/2
        histogram = np.stack((bin_centres, hist))
        name = convertLabel(atomsi[i-1])
        gaussian, probdistr, coefficients = fit_gaussian(histogram)
        
        printall = np.stack((bin_centres, hist, gaussian, probdistr), axis=1 )
        np.savetxt(name+".hist", printall)
        np.savetxt(name+".dat", allThing[i]*0.529177)
        np.savetxt(name+".coeff", coefficients)

def convertLabel(xs):
    ''' 
    generates a label with the list of atoms  [70, 170] --> Bond_70_170
    '''
    if len(xs) == 3:
       label = "Angle_"
    else:
       label = "Bond_"
    lab = '_'.join(str(x) for x in xs)
    return label + lab

def get_bonds(frames,atoms): 
    '''
    This functions wants an array with the frames, and a list with a pair of atoms
    '''
    number_of_steps = frames.shape[0]
    number_of_atoms = frames.shape[1]
    distance = np.empty(number_of_steps)
    for frame in range(number_of_steps):
        distance[frame] = bond_length(frames[frame,atoms])[0]#*0.529177
    return distance

def get_angles(frames,atoms): 
    '''
    This functions wants an array with the frames, and a list with a triplet of atoms
    '''
    number_of_steps = frames.shape[0]
    number_of_atoms = frames.shape[1]
    angle = np.empty(number_of_steps)
    for frame in range(number_of_steps):
        angle[frame] = bend_angle(frames[frame,atoms])[0]#*(180./np.pi)
    return angle

def fit_gaussian(data, p0=[2,0.1]):
    '''
    takes histogram and bins of same shape
    '''
    bins, hist = data[0],data[1] 
    coeff, var_matrix = curve_fit(gauss, bins, hist, p0=p0)
    # Get the fitted curve
    gauss_fit = gauss(bins, *coeff)
    # get k of the oscillator that generates this distribution and append it to the coefficient list
    # sqrt(k/2pi kb T)
    temp = 330
    kb = molmod.constants.boltzmann  #kb in hartree
    k = (temp*kb)/(coeff[1]**2)
    allcoeff = np.append(coeff,k)
    #allcoeff = np.append(allcoeff,k/2)
    #check if k replicates the real distribution
    coeff_distr = k, coeff[0], temp
    distr_fit = distrfun(bins, *coeff_distr)    
    return gauss_fit, distr_fit, allcoeff

def gauss(x, *p):
    '''
    Define a gaussian function to fit data. A = 1/np.sqrt(2*np.pi*sigma**2)
    '''
    mu, sigma = p
    return (1/(np.sqrt(2*np.pi)*sigma))*np.exp(-(x-mu)**2/(2.*sigma**2))

def distrfun(x, *p):
    '''
    Define the probability distribution function given K and T
    '''
    k, x0, temp = p
    kb = molmod.constants.boltzmann
    return(1/(np.sqrt(2*np.pi*kb*temp/k))*np.exp(-(k/(2*kb*temp))*(x-x0)**2))
    
if __name__ == "__main__":
    msg = " angle_bond -p <path/to/trajectory>"
    parser = argparse.ArgumentParser(description=msg)
    parser.add_argument('-p', required=True, help='path to the xyz trajectory')
    parser.add_argument('-st', required=False, default=0, type=int, help='starting time of the simulation (default=0)')
    parser.add_argument('-et', required=False, default=-1, type=int, help='ending time of the simulation')
#    parser.add_argument('-a', required=False, help='give three values for an angle')
#    parser.add_argument('-c', required=False, help='give two values for a bond length')
    args = parser.parse_args()
    main(args.p, args.st, args.et)
