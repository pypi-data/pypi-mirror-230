#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 14:25:38 2023

@author: Mikhail Glagolev

This script can create different simple initial configurations
for molecular dynamics simulations, which are used to check the
assessment of the ordering parameters by the mouse2 routines.

Currently, it can create a cubic cell with a choice of the following:
    - randomly distributed random walk polymer chains
    - randomly distributed polymer rods (all bonds of the macromolecule
      are parallel to each other)
    - randomly distributed polymer rods, each rod oriented randomly
    - randomly distributed helical fragments
    
In case of rods and helices, they can be oriented either along one common
director, generated randomly for all the system, or, if the --type is used
with the "disorder-" prefix, each be oriented along its own random director.
     
"""

import MDAnalysis as mda
import numpy as np
import random
import math
import argparse
from scipy.spatial.transform import Rotation

RANDOM_SEED = 42
# System parameters
LBOND = 1.
# Helical structure parameters
RTUBE = 0.53
PITCH = 1.66
PER_TURN = 3.3

def main():
    """
    Read the input, create MDAnalysis universe,
    populate it with atoms, write the output

    """

    parser = argparse.ArgumentParser(
        description = 'Create test systems for mouse2 library')

    parser.add_argument(
        '--type', metavar = 'TYPE', nargs = 1, type = str,
        help = "system type: [disordered-]rods, [disordered-]helices," +
        " random")

    parser.add_argument(
        '--npoly', metavar = 'N', nargs = 1, type = int,
        help = "degree of polymerization")

    parser.add_argument(
        '--nmol', metavar = 'n', nargs = 1, type = int,
        help = "number of macromolecules")

    parser.add_argument(
        '--box', metavar = 'SIZE', nargs = 1, type = float,
        help = "rectangular simulation cell size")

    parser.add_argument(
        'output', metavar = 'FILE', action = "store",
        help = "output file, the format is determined by MDAnalysis based" +
        " on the file extension")
    
    parser.add_argument(
        '--angles', action = "store_true", help = "Add bond angles")

    parser.add_argument(
        '--dihedrals', action = "store_true", help = "Add dihedral angles")

    args = parser.parse_args()

    system_type = args.type[0]

    CELL = args.box * 3 + [90, 90, 90]
    NMOL = args.nmol[0]
    NPOLY = args.npoly[0]

    random.seed(RANDOM_SEED)

    u = mda.Universe.empty(NMOL * NPOLY, trajectory = True,
                           atom_resindex = [0,] * NMOL * NPOLY)

    u.add_TopologyAttr('type')
    u.add_TopologyAttr('mass') #, values = [1.,] * NMOL * NPOLY)
    u.add_TopologyAttr('resids')
    u.add_TopologyAttr('resnums')
    u.add_TopologyAttr('angles', values = [])
    u.add_TopologyAttr('dihedrals', values = [])
    u.add_TopologyAttr('impropers', values = [])

    #Set the simulation cell size
    u.dimensions = CELL

    ix = 0
    bonds = []
    bond_types = []
    if args.angles:
        angles = []
        angle_types = []
    if args.dihedrals:
        dihedrals = []
        dihedral_types = []
    resids = []
    all_molecules = mda.AtomGroup([],u)

    # If the system is not "disordered", all of the molecules will have
    # the same (random) orientation
    if system_type[:10] != "disordered":
        molecule_rotation = Rotation.random()

    for imol in range(NMOL):
        #Generate molecule:
        current_residue = u.add_Residue(resid = imol + 1, resnum = imol + 1)
        molecule_atoms = []
        molecule_atomtypes = []
        molecule_atom_masses = []
        x, y, z = 0., 0., 0.
        for iatom in range(NPOLY):
            #Creating an atom with the current coordinates:
            atom = mda.core.groups.Atom(u = u, ix = ix)
            atom.position = np.array([x, y, z])
            atom.residue = current_residue
            molecule_atoms.append(atom)
            if iatom > 0:
                bonds.append([ix - 1, ix])
                bond_types.append('1')
            if args.angles and iatom > 1:
                angles.append([ix - 2, ix - 1, ix])
                angle_types.append('1')
            if args.dihedrals and iatom > 2:
                dihedrals.append([ix - 3, ix - 2, ix - 1, ix])
                dihedral_types.append('1')
            molecule_atomtypes.append('1')
            molecule_atom_masses.append(1.)
            ix += 1
            #Calculating coordinates for the next atom:
            #Random walk
            if system_type[:6] == "random":
                bond_vector = [0., 0., LBOND]
                rotation = Rotation.random()
                rotated_bond = Rotation.apply(rotation, bond_vector)
                x += rotated_bond[0]
                y += rotated_bond[1]
                z += rotated_bond[2]
            #Rod
            if system_type[-4:] == "rods":
                bond_vector = [0., 0., LBOND]
                x += bond_vector[0]
                y += bond_vector[1]
                z += bond_vector[2]
            #Helix
            if system_type[-7:] == "helices":
                x = RTUBE * math.cos((iatom + 1) * 2. * math.pi / PER_TURN)
                y = RTUBE * math.sin((iatom + 1) * 2. * math.pi / PER_TURN)
                z = PITCH * (iatom + 1) / PER_TURN
        molecule_group = mda.AtomGroup(molecule_atoms)
        # Place the first monomer unit randomly in the simulation cell
        translation_vector = np.array(CELL[:3]) * \
                np.array([random.random(), random.random(), random.random()])
        if system_type[:10] == "disordered":
            molecule_rotation = Rotation.random()
        molecule_group.atoms.positions = Rotation.apply(molecule_rotation,
                                        molecule_group.atoms.positions)
        molecule_group.atoms.positions += translation_vector
        molecule_group.atoms.types = molecule_atomtypes
        molecule_group.atoms.masses = molecule_atom_masses
        all_molecules += molecule_group
    u.add_bonds(bonds, types = bond_types)
    if args.angles:
        u.add_angles(angles, types = angle_types)
    if args.dihedrals:
        u.add_dihedrals(dihedrals, types = dihedral_types)
    all_molecules.write(args.output)
    
if __name__ == "__main__":
    main()