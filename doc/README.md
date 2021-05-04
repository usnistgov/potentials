# potentials documentation

This directory contains Jupyter Notebooks that provide documentation on how
to use the potentials package.

- **0. Search Potential Entries** provides a lightweight demonstration of
  using the potentials package to explore the listings of potentials found
  in the NIST Interatomic Potentials Repository.
- **0. Search LAMMPS Potentials** provides a lightweight demonstration of
  using the potentials package to explore the LAMMPS-compatible
  implementations of interatomic potentials found in the NIST Interatomic
  Potentials Repository.
- **1. Initial Setup** details setup options available to help customize
  some of the default behaviors of the potentials package.
- **2. Database class** provides a general overview of the Database class that
  handles the interactions with remote and local databases of potentials.
- **2.1. General record handling** describes the database methods that provide
  a means of interacting with any record in the database in a generalized way.
- **2.2. Citations** details the Citation class for interpreting Citation
  records and the database methods designed specifically for finding and
  exploring citations.
- **2.3. Potentials** details the Potential class for interpreting Potential
  records and the database methods designed specifically for finding and
  exploring potentials.  Note: the Potential records are associated with the
  full listings that appear on the NIST Interatomic Potentials Repository.
  See LAMMPS potentials (below) for using LAMMPS-compatible potentials.
- **2.4. LAMMPS potentials** details the PotentialLAMMPS class for interpreting
  potential_LAMMPS records and the database methods designed specifically for
  finding and exploring the LAMMPS potentials.  
- **2.5. openKIM models** details how potential models from openKIM can be
  interfaced with the potentials package so that installed KIM models are
  listed alongside the native LAMMPS potentials stored in the NIST Interatomic
  Potentials Repository.
- **3. Adding LAMMPS potentials** gives an overview of how new LAMMPS potentials
  can be defined such that they work with the potentials package.  This allows
  for private user-defined potentials to be integrated in with the publicly available NIST-hosted potentials.
