from . import loaded_formats, failed_formats, style2format

def potential_LAMMPS(pair_format=None, **kwargs):
    """
    Build potential_LAMMPS record
    """

    # Get pair_format if not given
    if pair_format is None:
        if 'pair_style' not in kwargs:
            raise ValueError('pair_format and/or pair_style are required')
        pair_format = style2format(kwargs['pair_style'])

    # Load appropriate subclass
    if pair_format in loaded_formats:
        return loaded_formats[pair_format](**kwargs)
    else:
        if pair_format in failed_formats:
            raise ImportError('pair_format ' + pair_format + ' failed to load: ' + failed_formats[pair_format])
        else:
            raise ValueError('Unknown pair_format: ' + pair_format)