import numpy as np

def gen_eam_setfl(F=None, rho=None, phi=None, rphi=None,
                  numr=1000, cutoffr=6, numrho=1000, cutoffrho=20, 
                  a_symbol=None, a_number=None, a_mass=None, a_lat_const=None, a_lat_type=None,
                  header=None, xf='%25.16e', ncolumns=5, outfile=None):
    """
    Generates a LAMMPS eam/alloy setfl style potential table file from supplied functions.
    
    Keyword Arguments:
    outfile -- file path or file-like object to save the generated table to. If not given, the table is returned as a string.
    F -- function or list/tuple of functions for the F(rho) embedding.
    rho -- function or list/tuple of functions for the electron density rho(r).
    phi -- function or list/tuple of functions for the pair-style phi(r).
    numr -- number of r datapoints to use for rho(r) and phi(r). More datapoints 
            provides a better representation of the underlying function at the 
            cost of some computational slowdown. Default value is 1000.
    cutoffr -- The r values will range from 0 to cutoffr. Default value is 6 
               (which may not be a good choice).
    numrho -- number of r datapoints to use for F(rho). More datapoints 
              provides a better representation of the underlying function at the 
              cost of some computational slowdown. Default value is 1000.
    cutoffrho -- The rho values will range from 0 to cutoffrho. Default value is 20 
               (which may not be a good choice).
    a_symbol -- string or list/tuple of strings representing the unique element symbol tags.
    a_number -- integer or list/tuple of integers for the atomic numbers.
    a_mass -- float or list/tuple of floats for the atomic masses.
    a_lat_const -- float or list/tuple of floats for the lattice constant.
    a_lat_type -- string or list/tuple of strings for the lattice type.
    header -- a string that gives the text to put into the header comment lines of 
              the file. This is limited to three lines (i.e. up to two newline 
              characters).
    xf -- c-style format string for representing the floating point values. Default 
          value is '%17.13f'.
    ncolumns -- specifies how many columns to divide the data tables up by. Default 
                value is 5.
    """
    
    # Check that F, rho, and phi have all been given and convert to tuples if needed
    assert F is not None, 'F function(s) must be given'
    assert rho is not None, 'rho function(s) must be given'
    assert phi is not None, 'phi function(s) must be given'
    if not isinstance(F, (list, tuple)): F = (F,)
    if not isinstance(rho, (list, tuple)): rho = (rho,)
    if not isinstance(phi, (list, tuple)): phi = (phi,)
    
    # Check number of supplied functions
    nelements = len(F)
    nphi = np.arange(1,nelements+1).sum()
    if len(phi) != nphi:
        raise ValueError('Invalid number of phi functions')
    if len(rho) == nelements:
        style = 'alloy'
    elif len(rho) == nelements**2:
        style = 'fs'
        k = 0
    else:
        raise ValueError('Invalid number of rho functions')
    
    # Check elemental information
    assert a_symbol is not None, 'a_symbol must be given'
    assert a_number is not None, 'a_number must be given'
    assert a_mass is not None, 'a_mass must be given'
    assert a_lat_const is not None, 'a_lat_const must be given'
    assert a_lat_type is not None, 'a_lat_type must be given'
    if not isinstance(a_symbol, (list, tuple)): a_symbol = (a_symbol,)
    if not isinstance(a_number, (list, tuple)): a_number = (a_number,)
    if not isinstance(a_mass, (list, tuple)): a_mass = (a_mass,)
    if not isinstance(a_lat_const, (list, tuple)): a_lat_const = (a_lat_const,)
    if not isinstance(a_lat_type, (list, tuple)): a_lat_type = (a_lat_type,)
    assert len(a_symbol) == nelements, 'Invalid number of a_symbol terms'
    assert len(a_number) == nelements, 'Invalid number of a_number terms'
    assert len(a_mass) == nelements, 'Invalid number of a_mass terms'
    assert len(a_lat_const) == nelements, 'Invalid number of a_lat_const terms'
    assert len(a_lat_type) == nelements, 'Invalid number of a_lat_type terms'
    
    # Check header information and use it to start eamdata
    if header is None:
        header = '\n\n\n'
    else:
        header = header.splitlines()
        if len(header) > 3:
            raise ValueError("Header is limited to three lines")
        while len(header) < 3:
            header.append('')
        header = '\n'.join(header)+'\n'
    eamdata = header
    
    # Add elemental symbol header information
    eamdata += str(nelements)
    for symbol in a_symbol:
        eamdata += ' ' + symbol
    eamdata += '\n'
    
    # Generate r and rhobar tables
    r = np.linspace(0, cutoffr, numr)
    rhobar = np.linspace(0, cutoffrho, numrho)
    
    # Add r and rho header info
    # ([1] terms in tables are deltas)
    eamdata += ('%i '+xf+' %i '+xf+' '+xf+'\n') % (numrho, rhobar[1], numr, r[1], cutoffr)
    
    line = []
    for i in xrange(nelements):
        
        # Per element-symbol header
        eamdata += ('%i '+xf+' '+xf+' %s\n') % (a_number[i], a_mass[i], a_lat_const[i], a_lat_type[i])
        
        #F values
        Fvals = F[i](rhobar)
        for j in xrange(len(Fvals)):
            line.append(xf % Fvals[j])
            if (j+1) % ncolumns == 0:
                eamdata += ' '.join(line) + '\n'
                line = []
        if len(line) > 0:
            eamdata += ' '.join(line) + '\n'
            line = []
            
        if style == 'alloy':
            #rho values for alloy style
            rhovals = rho[i](r)
            for j in xrange(len(rhovals)):
                line.append(xf % rhovals[j])
                if (j+1) % ncolumns == 0:
                    eamdata += ' '.join(line) + '\n'
                    line = []
            if len(line) > 0:
                eamdata += ' '.join(line) + '\n'
                line = []
        
        elif style == 'fs':
            # rho values for fs style
            for nk in xrange(nelements):
                rhovals = rho[k](r)
                k += 1
                for j in xrange(len(rhovals)):
                    line.append(xf % rhovals[j])
                    if (j+1) % ncolumns == 0:
                        eamdata += ' '.join(line) + '\n'
                        line = []
                if len(line) > 0:
                    eamdata += ' '.join(line) + '\n'
                    line = []
    
    # phi*r values
    for i in xrange(len(phi)):
        phivals = phi[i](r)
        for j in xrange(len(phivals)):
            line.append(xf % (phivals[j]))
            if (j+1) % ncolumns == 0:
                eamdata += ' '.join(line) + '\n'
                line = []
        if len(line) > 0:
            eamdata += ' '.join(line) + '\n'
            line = []
        
    # Save or display
    if outfile is None:
        return eamdata
    elif isinstance(outfile, (str, unicode)):
        with open(outfile, 'w') as f:
            f.write(eamdata)
    elif hasattr(outfile, 'write'):
        outfile.write(eamdata)
    else:
        raise TypeError('Invalid outfile type')

    
    
    
    