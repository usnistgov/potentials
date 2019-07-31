Zhou04_create_v2.f
==================

The FORTRAN script Zhou04_create_v2.f is an updated version of the create.f
script by X.W. Zhou (Sandia National Laboratories) for generating EAM/alloy
setfl interatomic potential files described in X.W. Zhou, R.A. Johnson, and
H.N.G. Wadley, Phys. Rev. B, 69, 144113 (2004).  This version was updated by
L.M. Hale (National Institute of Standards and Technology) with X.W. Zhou's
advice to fix spurious fluctuations in the original potential files caused by
conversions between single and double precision floating point numbers.

Instructions
------------

Compile the code with
    
    gfortran -oZhou04_EAM_2 Zhou04_create_v2.f
    
The generated executable needs two input files: EAM_code and EAM.input.
EAM_code contains the parameters used to generate the tabulated potentials for
all of the elements.  EAM.input specifies which elements are to be included
in the resulting potential file.  EAM_code and examples of EAM.input for 
different alloys (EAM.input.Cu for Cu, EAM.input.CuTa for Cu-Ta, etc.) can be
downloaded from the NIST Interatomic Potential Repository
https://www.ctcms.nist.gov/potentials/.

Assuming that EAM_code and the EAM.input file you want to use are in the same
directory as the executable, potential files can be generated with
    
    ./Zhou04_EAM_2<EAM.input
    
or on Windows
    
    ./Zhou04_EAM_2.exe<EAM.input
    
This will generate a potential file named *_Zhou04.eam.alloy, where * is a
list of the included elements.