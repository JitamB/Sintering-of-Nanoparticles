# ATOMISTIC MODELLING OF MATERIALS (MT41028)

**Instructor:** Sankha Mukherjee  
**Project 7:** Sintering of Nanoparticles  
**Software:** Atomsk + LAMMPS + OVITO  
**Type:** UG Group Project  
**Version:** 2.0 (August 2026)

---

## 1 Objective

Sintering is an important materials-processing technique used in powder metallurgy, ceramics, additive manufacturing, and many other technologies.

During sintering, neighbouring particles come into contact and gradually form a larger, more compact structure. At the atomic scale, this process is driven mainly by the reduction of surface energy.

In this project, you will use molecular dynamics to watch two aluminium nanoparticles coalesce at elevated temperature.

**The main question is:**  
How does temperature affect the coalescence of two nanoparticles?

You will use:
1. **Atomsk** to construct the nanoparticles;
2. **LAMMPS** to perform molecular dynamics;
3. **OVITO** to visualize the atomic motion.

**The workflow is:**
$$\text{Construct particles} \rightarrow \text{Heat} \rightarrow \text{MD} \rightarrow \text{Visualize coalescence}$$

> The emphasis is on seeing and understanding atomic-scale materials behaviour rather than performing a large numerical study.

---

## 2 Material and Simulation

The recommended material is aluminium.

| Parameter | Value |
| :--- | :--- |
| **Material** | Aluminium (Al) |
| **Crystal structure** | fcc |
| **Lattice constant** | $a_{0} \approx 4.05\text{ \AA}$ |
| **Potential** | `Al99.eam.alloy` |
| **LAMMPS units** | metal |
| **Simulation** | Molecular dynamics |
| **Ensemble** | NVT |
| **Time step** | $1\text{ fs}$ |
| **Particle radius** | approximately $2\text{--}3\text{ nm}$ |

Each group will construct two approximately equal spherical nanoparticles.

The particles should be placed close enough that they can interact and form a neck during the simulation.

Use periodic boundary conditions with sufficient vacuum around the particles so that the nanoparticles do not interact with their own periodic images.

---

## 3 Part 1: Construct Two Nanoparticles

Use Atomsk to construct two spherical aluminium nanoparticles.

* **Atomsk Website:** https://atomsk.univ-lille.fr/

The two particles should have approximately the same radius. A particle radius of approximately $R \approx 2\text{--}3\text{ nm}$ is recommended.

The particles may have the same crystallographic orientation.

Place the particles along one direction with a small initial gap. The surfaces should be close enough that thermal motion can bring them into contact.

The final system should contain approximately a few thousand atoms and should run comfortably on a personal computer.

Save the structure as a LAMMPS data file.

Check the structure in OVITO before starting the MD simulation.

---

## 4 Part 2: Molecular Dynamics

Perform an NVT molecular-dynamics simulation.

A typical simulation can use:
* **Temperature:** $700\text{--}800\text{ K}$
* **Time step:** $1\text{ fs}$
* **Simulation time:** approximately $0.5\text{--}1\text{ ns}$
* **Thermostat:** Nosé-Hoover thermostat

### Basic LAMMPS Input Script

```lammps
units           metal
dimension       3
boundary        p p p
atom_style      atomic

read_data       Al_nanoparticles.data

pair_style      eam/alloy
pair_coeff      * * Al99.eam.alloy Al

velocity        all create 750.0 12345 mom yes rot yes

timestep        0.001

fix             1 all nvt temp 750.0 750.0 0.1

thermo          1000
thermo_style    custom step temp pe ke etotal

dump            1 all custom 1000 trajectory.lammpstrj id type x y z

run             500000

unfix           1
write_data      final.data
```

Here, with `metal` units, $0.001\text{ ps} = 1\text{ fs}$.

The exact simulation length may be adjusted depending on how quickly the particles coalesce.

---

## 5 Part 3: Visualize the Sintering Process

Open the trajectory in OVITO.

Look at the simulation at several times:
* $t = 0$
* $t = t_{1}$
* $t = t_{2}$
* $t = t_{\text{final}}$

Create a sequence of approximately four snapshots showing the evolution from two separate particles to a connected structure.

Pay particular attention to the region where the two particles meet. You should observe the formation and growth of a neck between the particles.

**The important physical process is:**
$$\text{surface atoms move} \rightarrow \text{particles contact} \rightarrow \text{neck forms} \rightarrow \text{neck grows}$$

---

## 6 Part 4: Temperature Comparison

Repeat the simulation at a second temperature.

For example, if the first simulation was performed at $T_{1} = 700\text{ K}$, perform a second simulation at $T_{2} = 800\text{ K}$.

**Use the same:**
* nanoparticle structure
* simulation box
* potential
* time step
* simulation duration

Only the temperature should be changed.

Compare the two trajectories in OVITO. **Which simulation shows faster particle coalescence?**

---

## 7 Part 5: Simple Analysis

You do not need to perform a detailed kinetic analysis.

For each temperature, record approximately:
* the time when the particles first make contact;
* the time when a clear neck is formed;
* the final appearance of the particles.

Prepare a simple table:

| Temperature | Contact time | Neck formation time | Final structure |
| :--- | :--- | :--- | :--- |
| $T_{1}$ | | | |
| $T_{2}$ | | | |

The times do not need to be extremely precise. The purpose is to compare the qualitative kinetics of the two simulations.

---

## 8 What to Submit

Each group should submit:

1. The Atomsk commands/script used to construct the particles.
2. The LAMMPS input files.
3. The LAMMPS trajectory files.
4. Four representative OVITO snapshots showing the coalescence process.
5. The corresponding snapshots for the second temperature.
6. A small table comparing the two temperatures.
7. A short explanation of why increasing temperature changes the sintering behaviour.

> There is no formal report and no requirement for an extensive literature review.

---

## 9 Questions to Think About

Discuss briefly with your group:

1. Why do the nanoparticles tend to join together?
2. Why does a neck form between them?
3. Why does increasing temperature accelerate the process?
4. Where do the atoms in the neck come from?
5. Why is sintering particularly important for nanoparticles?

You do not need lengthy written answers. The purpose is to connect what you see in OVITO with the physical picture of sintering.

---

## Useful Resources

* **Atomsk:** [https://atomsk.univ-lille.fr/](https://atomsk.univ-lille.fr/)
* **LAMMPS:** [https://docs.lammps.org/](https://docs.lammps.org/)
* **OVITO:** [https://www.ovito.org/](https://www.ovito.org/)

---

> **The goal of this project is simple:**  
> Watch a macroscopic materials-processing phenomenon happen through the motion of individual atoms.

Good luck and happy simulating!  
*Sankha Mukherjee*