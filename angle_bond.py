import numpy as np
import molmod as md
import argparse
from functools import partial
from molmod.io.xyz import XYZFile
from molmod.ic import bend_angle
from molmod.ic import bond_length
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def main(file_name):

    xyz_file = XYZFile(file_name)
    outputName = "bond_angles.dat"
    outFilenameGraph = "bond_anglesGraph"
    frames = xyz_file.geometries
    atomsi = [[170,70,9],[170,70,167],[70,170]]  #add this in the command line
#    atomsi = [[165,68,5],[165,68,267],[165,68]]  #add this in the command line
    atoms = [ list(np.array(a)-1) for a in atomsi ]

    bonds  = map(partial(get_bonds, frames), filter(lambda at: len(at) == 2, atoms))
    angles = map(partial(get_angles, frames), filter(lambda at: len(at) == 3, atoms))

    numbers = [np.arange(frames.shape[0])+1]

    allThing = np.concatenate((numbers, bonds, angles))
    np.savetxt(outputName,np.transpose(allThing))
    plotBonds_Angles(outFilenameGraph,allThing,atomsi)

def plotBonds_Angles(outFilename,allThing,atomsi):
    (num,steps) = allThing.shape
    for i in range(num)[1:]:
        histogram = zip(*np.histogram(allThing[i], bins=50))
        name = convertLabel(atomsi[i-1])
        np.savetxt(name, histogram)

def convertLabel(xs):
    if len(xs) == 3:
       label = "Angle_"
    else:
       label = "Bond_"
    lab = '_'.join(str(x) for x in xs)
    return label+lab+".hist"

def get_bonds(frames,atoms): 
    """
    This functions wants an array with the frames, and a list with a pair of atoms
    """
    number_of_steps = frames.shape[0]
    number_of_atoms = frames.shape[1]
    distance = np.empty(number_of_steps)
    for frame in range(number_of_steps):
        distance[frame] = bond_length(frames[frame,atoms])[0]
    return distance

def get_angles(frames,atoms): 
    """
    This functions wants an array with the frames, and a list with a triple of atoms
    """
    number_of_steps = frames.shape[0]
    number_of_atoms = frames.shape[1]
    angle = np.empty(number_of_steps)
    for frame in range(number_of_steps):
        angle[frame] = bend_angle(frames[frame,atoms])[0]
    return angle

def fit_gaussian(data, p0=[2,1]):
    hist, bin_edges = data[:,0],data[:,1]  
    bin_centres = (bin_edges[:-1] + bin_edges[1:])/2
    coeff, var_matrix = curve_fit(gauss, bin_centres, hist, p0=p0)
    # Get the fitted curve
    hist_fit = gauss(bin_centres, *coeff)



def gauss(x, mu, sigma):
    return (1/np.sqrt(2*np.pi*sigma**2))*numpy.exp(-(x-mu)**2/(2.*sigma**2))
    




    
if __name__ == "__main__":
    msg = " angle_bond -p <path/to/trajectory>"
    parser = argparse.ArgumentParser(description=msg)
    parser.add_argument('-p', required=True, help='path to the xyz trajectory')
#    parser.add_argument('-a', required=False, help='give three values for an angle')
#    parser.add_argument('-c', required=False, help='give two values for a bond length')
    args = parser.parse_args()
    main(args.p)
