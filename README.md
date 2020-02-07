Pipeline Code
=============

Uses xdsme to control processing of user diffraction data, most commonly for macromolecular crystallography (MX) experiments, at the Australian Synchrotron. The actual processing executed ranges from reprocessing of already-integrated datasets, to the entire pipeline from the beginning for a chemical crystallography (CX) experiment.

Features
--------

 * Processes data collected from ADSC, Eiger, and Eiger2 detectors
 * Can be configured to run jobs with Kubernetes using the Jib library
 * Can trigger autorickshaw runs at the end of processing
 * Reprocess datasets with several possible user inputs, including unit cell/space group, frame number selection, ice-weak-brute-slow flags from xdsme, and a from_start flag to re-do processing from the beginning

Requirements
------------

 * xdsme - used to run XDS underneath. Use my version for best results - https://github.com/JunAishima/xdsme
 * MX beamline library - used at the Australian Synchrotron. includes object setup (databases, detector type)
 * MongoDB and Redis databases for storing experimental information and other data
 * processing.models - classes for storing and retrieving information from a MongoDB
 * custom_parser - a custom library to parse aimless log files
 * CCP4 - for running pointless, aimless, truncate

External Python libraries
----------------

 * matplotlib - for drawing dataset and CX plots
 * smartie - for parsing output from Aimless from the CCP4 software package
 * click
 * logbook
 * jinja2
 * pandas
 * numpy
 * h5py (and associated hdf5/libhdf5 binary)
 * json

Authors
-------

Nathan Mudie developed the pipeline code.

Jun Aishima rolled out the code to the MX beamlines at the Australian Synchrotron and has continued to extend it with new features.

Kate Smith has developed the Xprep graphs for CX experiments and added additional cif parameters.
