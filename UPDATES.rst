Updates
=======

0.3.8
-----

- auto_set_pid_off option added to the record upload options to turn off the
  associated CDCS database setting to avoid database errors.
- Support has been added to the potential_LAMMPS record class and builders for
  the URL fields that become the PID values for the records once uploaded. 
- Depreciation fix for importlib.
- Bug fix related to finding no matching records.
- Bug fix to make int symbol values be str.

0.3.7
-----

- Record objects are updated allowing for each to be assigned a default
  database object from which record methods can retrieve additional database
  content as needed.
- A new parameter file builder tool has been added for ADP potentials.

0.3.6
-----

- Code adjustments related to yabadaba 0.2.0 updates to Query handling.
  The parameters supported by query operations can now be viewed with
  querydoc.

0.3.5
-----

- URL fields added to Potential and BasePotentialLAMMPS records which are
  used as PIDs on potentials.nist.gov, i.e. permanent hyperlinks for the
  records.
- XSL and XSD representations updated to coincide with record structure and
  how the records are viewed on potentials.nist.gov.
- pytests (barely) started.

0.3.4
-----

- Typing hints added throughout the code.
- Random bug fixes and docstring typo fixes.

0.3.3
-----

- The underlying datamodelbase module is now moved to the new separate
  yabadaba package.  Tons of minor updates associated with this and new
  yabadaba features.
- Random bug fixes.

0.3.2
-----

- bad_lammps_potentials list added which lists the LAMMPS potentials entries
  that should always issue errors if used.  This is useful for anyone wishing
  to test both old and new versions of potentials by helping to process
  calculation errors.
- More updates for KIM potentials - now any KIM models associated with multiple
  potential entries will generate separate PotentialLAMMPS records for each.
  This simplifies the handling of these edge cases and helps avoid compositions
  associated with untrained cross-interactions.
- Citation records now treat "journal" as optional when loading.  CrossRef
  bibtex seems to now be missing this value?

0.3.1
-----

- Query methods are no longer static methods to make them consistent with
  other operations.  
- Retrieve methods added that allow for a record to automatically
  be saved as a file after it was queried.
- The list of most stable isotopes added to atomic info to avoid having to
  specify isotope numbers for radioactive elements.
- Improvements to cache handling for local databases.
- The order of parameters for database methods were rearranged for consistency
  and practicality.
- All default query parameter values are now None to avoid unwanted automatic
  filtering of records.
- Additional bug fixes identified during testing

0.3.0
-----
- Major overhaul of the package.  Most of the code was reworked to add 
  functionality and streamline database interactions between the potentials, atomman
  and iprPy packages.  
- Basic database and record handling now in a separate sub-package, which is planned
  on being fully branched off later. 
- A csv-based caching system is added for local style databases to speed up queries.
- Records now specify recognized query parameters allowing for custom "fast" queries
  to be generated for the different database styles.
- Loading of record styles no longer necessary.
- Performance improvements related to how the query actions are performed.
- The handling of openKIM models has been improved.  
- Tools relating to building and analyzing EAM parameter files have been added in.
- Specific database operations now exist for all supported record styles.
