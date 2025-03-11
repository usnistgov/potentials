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
- **1. Quick overview** provides a quick overview to the potentials package
  to explore and access interatomic potentials hosted by the NIST
  Interatomic Potentials Repository.
- **2. Package Design Overview** describes the design of the potentials
  package in more detail for those who wish to know.
- **3. Change Default Settings** outlines how users can set and change
  default settings of potentials and retain the settings across different
  python sessions.
- **4. Database class** provides a general overview of the Database class
  that handles the interactions with remote and local databases of
  potentials.
- **5. Record Classes** gives an overview of the Record classes used by
  potentials (through yabadaba) that allow for interacting and transforming
  database data.
- **5.1. Citation records** details the Citation class for interpreting
  Citation records and the database methods designed specifically for finding
  and exploring citations.
- **5.2. Potential records** details the Potential class for interpreting
  Potential records and the database methods designed specifically for
  finding and exploring potentials.  Note: the Potential records are
  associated with the full listings that appear on the NIST Interatomic
  Potentials Repository.  See LAMMPS potentials (below) for using
  LAMMPS-compatible potentials.
- **5.3. LAMMPS potentials** details the PotentialLAMMPS class for
  interpreting potential_LAMMPS records and the database methods designed
  specifically for finding and exploring the LAMMPS potentials.
- **5.4. OpenKIM models** details how potential models from openKIM can be
  interfaced with the potentials package so that installed KIM models are
  listed alongside the native LAMMPS potentials stored in the NIST Interatomic
  Potentials Repository.
- **5.5 Action records** details the Action class for interpreting
  Action records and the database methods designed specifically for finding
  and exploring the list of updates made to the website in the form of new
  potentials and content updates.
- **5.6 Request records** details the Request class for interpreting
  Request records and the database methods designed specifically for finding
  and exploring the list of user-requested interatomic potentials that at the
  time of the request were not in the NIST Repository.
- **5.7 FAQ records** details the FAQ class for interpreting
  FAQ records and the database methods designed specifically for finding
  and exploring the FAQs of the NIST Interatomic Potentials Repository.
- **6. User-defined LAMMPS potentials** gives an overview of how users can
  create PotentialLAMMPS objects for LAMMPS-compatible potentials that are
  not in the NIST Interatomic Potentials Repository.  This allows for any
  user-defined potential to be integrated with any tools that use the
  potentials package.
- **7 Parameter File Tools** gives a quick preview of some of the tools
  included in the potentials.paramfile module for building, analyzing and
  converting interatomic potential parameter files.
