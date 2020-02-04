==========
potentials
==========

Introduction
------------

The potentials package provides a Python-based interface to the content hosted
on the `NIST Interatomic Potentials Repository`_. The package directly
interacts with the underlying database hosted at `https://potentials.nist.gov/`_
allowing for the metadata for the hosted interatomic potentials to be searched
and explored.

Jupyter Notebooks
-----------------

Search Tools
````````````

- `Search Potential Entries.ipynb`_ |colab1| provides a user-friendly interface
  for searching and exploring the known interatomic potentials.

- `Search LAMMPS Potentials.ipynb`_ |colab2| provides a user-friendly interface
  for searching and exploring the known LAMMPS interatomic potentials.
  Parameter files can be downloaded, and the associated LAMMPS command lines
  shown.

- `Database Exploration.ipynb`_ |colab3| provides details for how to
  perform more complicated searches directly in Python.

Adding Content
``````````````

- Add LAMMPS Potentials.ipynb shows how users can integrate their own LAMMPS
  potential implementations with the Python code.

- Content Manager.ipynb provides a working document for those with access to
  add and modify repository content.

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
- BTools supporting the construction of the records used by PotentialLAMMPS for
  different LAMMPS pair styles so that users can integrate their personal
  LAMMPS potentials with the code and database records.
- Classes for interacting with FAQ, Requests, and Action records used by the
  Interatomic Potentials Repository.

Planned
```````

- Tools supporting the construction of parameter files in different LAMMPS
  styles.  (EAM-oriented tools exist, but need to be integrated in.)

Record status
`````````````
- NIST: 100%
- OpenKIM: 0% (75% in local files, to be merged)
- Additional metadata fields to be added to records...

.. _NIST Interatomic Potentials Repository: https://www.ctcms.nist.gov/potentials/
.. _https://potentials.nist.gov/: https://potentials.nist.gov/

.. _Search Potential Entries.ipynb: https://colab.research.google.com/github/usnistgov/potentials/blob/master/Search%20Potential%20Entries.ipynb
.. |colab1| image:: https://colab.research.google.com/assets/colab-badge.svg
 #
 :alt: colab logo
 :target: https://colab.research.google.com/github/usnistgov/potentials/blob/master/Search%20Potential%20Entries.ipynb

.. _Search LAMMPS Potentials.ipynb: https://colab.research.google.com/github/usnistgov/potentials/blob/master/Search%20LAMMPS%20Potentials.ipynb
.. |colab2| image:: https://colab.research.google.com/assets/colab-badge.svg
 #
 :alt: colab logo
 :target: https://colab.research.google.com/github/usnistgov/potentials/blob/master/Search%20LAMMPS%20Potentials.ipynb

.. _Database Exploration.ipynb: https://colab.research.google.com/github/usnistgov/potentials/blob/master/Database%20Exploration.ipynb
.. |colab3| image:: https://colab.research.google.com/assets/colab-badge.svg
 #
 :alt: colab logo
 :target: https://colab.research.google.com/github/usnistgov/potentials/blob/master/Database%20Exploration.ipynb
