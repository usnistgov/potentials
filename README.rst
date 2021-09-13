==========
potentials
==========

Introduction
------------

The potentials package provides a Python-based interface to the content hosted
on the `NIST Interatomic Potentials Repository`_. The package directly
interacts with the underlying database hosted at `https://potentials.nist.gov/`_
allowing for the metadata for all hosted interatomic potentials to be searched
and explored.

This package is integrated into `atomman`_ and `iprPy`_, which both extend the
database interactions provided here.  For example, atomman adds the ability to
interact with atomic structure records in the NIST database, and iprPy further
adds the ability to interact with property calculation results.  See the
documentation for those packages if you are interested in exploring more than
just interatomic potential information.

Installation
------------

The potentials package can easily be installed using pip or conda-forge

    pip install potentials

or 
    conda install -c conda-forge potentials

Documentation
-------------

The documentation for the potentials package consists of Jupyter Notebooks
contained in the doc directory.  These describe the different components
of the package and provide working examples.

Basic Search Tools
``````````````````

- `0. Search Potential Entries.ipynb`_ |colab1| provides a user-friendly interface
  for searching and exploring the known interatomic potentials.

- `0. Search LAMMPS Potentials.ipynb`_ |colab2| provides a user-friendly interface
  for searching and exploring the known LAMMPS interatomic potentials.
  Parameter files can be downloaded, and the associated LAMMPS command lines
  shown.

In-depth Documentation
``````````````````````

More in-depth documentation can be found in the doc subfolder.  The Notebooks
located there provide information as to the design of the potentials package,
how to change default settings, and options that are specific to the supported
record styles.

Scripts
```````

The scripts subfolder contains additional Notebooks that relate to managing
the NIST database using the potentials package.  These are provided as examples
of using the potentials package for various tasks to help more advanced users
get started.  WARNING: The Notebooks in scripts are working documents and are not
guaranteed to have 100% current code or data, and may have poor descriptions.   


.. _NIST Interatomic Potentials Repository: https://www.ctcms.nist.gov/potentials/
.. _https://potentials.nist.gov/: https://potentials.nist.gov/

.. _atomman: https://www.ctcms.nist.gov/potentials/atomman/
.. _iprPy: https://www.ctcms.nist.gov/potentials/iprPy/

.. _0. Search Potential Entries.ipynb: https://colab.research.google.com/github/usnistgov/potentials/blob/master/doc/0.%20Search%20Potential%20Entries.ipynb
.. |colab1| image:: https://colab.research.google.com/assets/colab-badge.svg
 #
 :alt: colab logo
 :target: https://colab.research.google.com/github/usnistgov/potentials/blob/master/0.%20Search%20Potential%20Entries.ipynb

.. _0. Search LAMMPS Potentials.ipynb: https://colab.research.google.com/github/usnistgov/potentials/blob/master/doc/0.%20Search%20LAMMPS%20Potentials.ipynb
.. |colab2| image:: https://colab.research.google.com/assets/colab-badge.svg
 #
 :alt: colab logo
 :target: https://colab.research.google.com/github/usnistgov/potentials/blob/master/0.%20Search%20LAMMPS%20Potentials.ipynb
