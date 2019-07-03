==========
potentials
==========

Introduction
------------

This git repository is meant to be a location for migrating and sharing the data and tools associated with the interatomic potentials hosted at the NIST Interatomic Potentials Repository (IPR).

More to come...

Current content
---------------

data is meant to host the potentials parameter files and associated metadata records.  Note that currently this data is copied from other locations and is not guaranteed to be 100% up to date.  The types of data stored here are

- biblib: bibtex files for the citations associated with the potentials.

- Potential: the data records for content generation on the IPR website.

- potential_LAMMPS: the potential parameter files and atomman.lammps.Potential data records associated with all of the LAMMPS-compatible potentials hosted by IPR (copied from iprPy).

iprbuild contains code for generating and interacting with the different data models.

potentials is meant to be the Python package where the iprbuild tools are to be migrated to as they are cleaned up.

