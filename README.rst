==========
potentials
==========

Introduction
------------

*Note: this site is still early alpha and changes are expected based on needs*
*and and suggestions*.

Potentials provides a lightweight database of interatomic potentials and
force fields.  Right now, the database contains listings for the
potentials stored in the NIST Interatomic Potentials Repository, as well as
about 75% of OpenKIM models.

In part, this project came about as a means to foster easier incorporation
of the potentials hosted at NIST into external projects.  It also provides a
means to catalogue interatomic potential content that is otherwise missing from
the various open-source repositories.

- Known published potentials with no known implementations.
- Personal "unauthorized" implementations of potentials that were used for
  publications, which may behave differently than the preferred "authorized"
  files from the potential developers.
- Links to sites that host potentials that are not open-source, so users can
  find the terms of use for said potentials.
- As the git database can be cloned, any proprietary or in-development
  potentials can be added to a personal instance of the database without the
  content being accessible to outsiders.  Thus, the same framework can be used
  for both public and private models.

Jupyter Notebooks
-----------------

Currently, examples and documentation for using potentials is given as Jupyter
Notebooks stored in the main git directory.

- **Database Exploration** |ColabLink|_ provides simple examples of search
  capabilities to easily find interatomic potentials and implementations.

- **Database Description** provides descriptions of the different components
  of potentials to assist others in implementing new features.

- **Add and edit...** Notebooks are meant to be assistant tools to help others
  add and edit the database content.

.. |ColabLink| image:: https://colab.research.google.com/assets/colab-badge.svg
.. _ColabLink: https://colab.research.google.com/github/lmhale99/potentials/blob/master/Database%20Exploration.ipynb
