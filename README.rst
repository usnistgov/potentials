==========
potentials
==========

Introduction
------------

*Note: this package is still in development and substantial changes may*
*occur.*

The potentials package provides a Python-based interface to the content hosted
on the `NIST Interatomic Potentials Repository`_. The package directly
interacts with the underlying database hosted at `https://potentials.nist.gov/`_
allowing for the metadata for the hosted interatomic potentials to be searched
and explored.

Search Tools
------------

**`Potential Search.ipynb`_** |ColabLink1|_ provides a user-friendly interface
for searching and exploring the known interatomic potentials.

**`LAMMPS Search.ipynb`_** |ColabLink2|_ provides a user-friendly interface
for searching and exploring the known LAMMPS interatomic potentials.  Parameter
files can be downloaded, and the associated LAMMPS command lines shown.

**`Database Exploration.ipynb`_** |ColabLink3|_ provides details for how to
perform more complicated searches directly in Python.

Package Features
----------------

Implemented
```````````

- Anyone can use the Database class to explore hosted records.
- Publication citations are handled with the Citation class that can
  read/write citation data as bibtex, JSON, or XML.  New citations can be
  constructed, existing ones updated, and can be rendered as HTML.
- Metadata descriptions of interatomic potentials (citation info, notes, and
  a list of known implementations) are handled with the Potential class. New
  potentials can be constructed, existing ones updated, saved/loaded from XML
  or JSON, and can be rendered as HTML.
- The PotentialLAMMPS class can be used to generate proper LAMMPS input
  commands for the hosted LAMMPS-compatible interatomic potentials.  Any
  LAMMPS parameter files can also be downloaded.
- Any record can be copied, and all records can be downloaded to a local
  directory.  If the path to the local directory is given, the Database class
  can interact with the local copy in a manner comparable to the remote
  database.
- Classes for interacting with FAQ, Requests, and Action records used by the
  Interatomic Potentials Repository.

Planned
```````
- Tools supporting the construction of the records used by PotentialLAMMPS for
  different LAMMPS pair styles. (in iprbuild, needs to be moved over.)
- Tools supporting the construction of parameter files in different LAMMPS
  styles.  (EAM-oriented tools exist, but need to be integrated in.)

Record status
`````````````
- NIST: 100%
- OpenKIM: 0% (75% in local files, to be merged)
- Additional metadata fields to be added to records...

.. _NIST Interatomic Potentials Repository: https://www.ctcms.nist.gov/potentials/
.. _https://potentials.nist.gov/: https://potentials.nist.gov/
.. |ColabLink1| image:: https://colab.research.google.com/assets/colab-badge.svg
.. _ColabLink1: https://colab.research.google.com/github/lmhale99/potentials/blob/master/Potential%20Search.ipynb
.. |ColabLink2| image:: https://colab.research.google.com/assets/colab-badge.svg
.. _ColabLink2: https://colab.research.google.com/github/usnistgov/potentials/blob/master/LAMMPS%20Search.ipynb
.. |ColabLink3| image:: https://colab.research.google.com/assets/colab-badge.svg
.. _ColabLink3: https://colab.research.google.com/github/usnistgov/potentials/blob/master/Database%20Exploration.ipynb
