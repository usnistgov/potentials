# Scripts

**Caution**: These notebooks have not yet been tested with the 0.4.0 version update!!

This directory collects various Python scripts and Jupyter Notebooks that are
used to manage the potentials database content.  These scripts are not
intended for people who simply want to find and use potentials already in the
database; see the Notebooks in the doc folder instead.  The scripts here are
included in the git repository to sync the tools across resources and
contributors, and to provide guidance for advanced users wishing to integrate
potentials into other frameworks.

- The __Content Manager__ Notebook provides a single document where records
  associated with potential listings can be added and updated.  The cells in
  the Notebook outline the workflow for constructing new listings and the
  various options available each step of the way.  All cells are *not* meant
  to be executed and fields in many of the cells are meant to be changed as
  the records are generated.

- The __Record consistency checks__ Notebook provides checks for ensuring that
  the records in the different database locations (potentials.nist.gov,
  potentials-library) are the same and that content is consistent across
  records of different styles.  The content checks include both verifying
  that correct reference keys and ids are used, and that shared common
  content that appears in multiple records is the same.

- Others?
