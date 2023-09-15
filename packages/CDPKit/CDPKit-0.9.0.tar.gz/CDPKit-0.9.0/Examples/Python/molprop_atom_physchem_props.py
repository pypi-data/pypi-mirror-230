#!/bin/env python

##
# molprop_atom_physchem_props.py 
#
# This file is part of the Chemical Data Processing Toolkit
#
# Copyright (C) 2003 Thomas Seidel <thomas.seidel@univie.ac.at>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; see the file COPYING. If not, write to
# the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
##


import sys
import os

import CDPL.Chem as Chem
import CDPL.MolProp as MolProp


# outputs the corresponding properties of each atom of the provided molecular graph
def outputProperties(molgraph: Chem.MolecularGraph) -> None:
    Chem.calcImplicitHydrogenCounts(molgraph, False)    # calculate implicit hydrogen counts and set corresponding property for all atoms
    Chem.perceiveHybridizationStates(molgraph, False)   # perceive atom hybridization states and set corresponding property for all atoms
    Chem.perceiveSSSR(molgraph, False)                  # perceive SSSR and store as Chem.MolecularGraph property
    Chem.setRingFlags(molgraph, False)                  # perceive cycles and set corresponding atom and bond properties
    Chem.setAromaticityFlags(molgraph, False)           # perceive aromaticity and set corresponding atom and bond properties
    Chem.calcTopologicalDistanceMatrix(molgraph, False) # calculate topological distance matrix and store as Chem.MolecularGraph property
                                                        # (required for effective polarizability calculations)
    for atom in molgraph.atoms:
        print('- Atom #%s' % str(molgraph.getAtomIndex(atom)))
        print('\tHybrid polarizability: %s' % str(MolProp.getHybridPolarizability(atom, molgraph)))
        print('\tEffective polarizability: %s' % str(MolProp.calcEffectivePolarizability(atom, molgraph)))

def main() -> None:
    if len(sys.argv) < 2:
        sys.exit('Usage: %s <input mol. file>' % sys.argv[0])

    # create reader for input molecules (format specified by file extension)
    reader = Chem.MoleculeReader(sys.argv[1]) 
    
    # create an instance of the default implementation of the Chem.Molecule interface
    mol = Chem.BasicMolecule()
    
    # read and process molecules one after the other until the end of input has been reached
    try:
        while reader.read(mol):
            try:
                outputProperties(mol)
            except Exception as e:
                sys.exit('Error: processing of molecule failed: ' + str(e))
                
    except Exception as e: # handle exception raised in case of severe read errors
        sys.exit('Error: reading molecule failed: ' + str(e))

    sys.exit(0)
        
if __name__ == '__main__':
    main()
