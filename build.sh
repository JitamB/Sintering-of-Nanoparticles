#!/bin/bash
# Build two Al nanoparticles (R = 25 A) with Atomsk.
# Particle 2 is rotated 30 deg about z, so a grain boundary forms in the neck.
# Output: structure/Al_nanoparticles.lmp (LAMMPS data file, ~7900 atoms)

set -e
cd "$(dirname "$0")"
mkdir -p structure
cd structure

A0=4.05      # Al lattice constant (A)
R=25.0       # particle radius (A)
D=56.5       # centre-to-centre distance = 2R + 6.5 A gap (just beyond the 6.29 A cutoff)
ROT=30       # misorientation of particle 2 about z (deg)

rm -f np1.xsf np2.xsf Al_nanoparticles.lmp

# Particle 1: carve a sphere out of a 14x14x14 fcc block (56.7 A cube)
atomsk --create fcc $A0 Al -duplicate 14 14 14 \
       -select out sphere 0.5*box 0.5*box 0.5*box $R -rmatom select \
       np1.xsf

# Particle 2: copy of particle 1, rotated about its own centre, shifted along x
atomsk np1.xsf -select all -rotate com z $ROT -shift $D 0 0 np2.xsf

# Put both in one box with >= 25 A vacuum on every side, centre the pair
atomsk --merge 2 np1.xsf np2.xsf Al_nanoparticles.lmp \
       -cell H1 set 160 -cell H2 set 110 -cell H3 set 110 -center com
