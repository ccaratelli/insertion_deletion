#!/usr/bin/python
from molmod.io.xyz import XYZFile
from molmod.unit_cells import UnitCell
import numpy as np

def main(file_name)

    xyz_file = XYZFile(file_name)
    frames = xyz_file.geometries
    n_atoms = xyz_file.geometries.shape[1]
    n_steps = xyz_file.geometries.shape[0]
    titles = xyz_file.titles
    # Unit cell, decide how to make this general 
    matrix=np.array([\
         [1.4731497044857509E+01, 3.2189795740722255E-02, 4.5577626559295564E-02],\
         [4.2775481701113616E-02, 2.1087874593411915E+01, -2.8531114198383896E-02],\
         [6.4054385616337750E-02, 1.3315840416191497E-02, 1.4683043045316882E+01]])
    cell = UnitCell(matrix) 
    frac = UnitCell.to_fractional(cell, frames)
    decimals = np.modf(frac)[0]
    frac_wrapped = np.where(frac < 0, 1 + frac, frac)
    cart_wrapped = molmod.unit_cells.UnitCell.to_cartesian(cell, frac_wrapped)

    xyz_file.geometries = cart_wrapped
    xyz_file.write_to_file(file_name.rsplit(".",1)[0]+"_wrapped.xyz")

if __name__ == "__main__":
    msg = " wrap_cell -p <path/to/trajectory>"
    parser = argparse.ArgumentParser(description=msg)
    parser.add_argument('-p', required=True, help='path to the xyz trajectory')
    args = parser.parse_args()
    main(args.p)