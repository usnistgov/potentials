from .build import (EamBuilder, EimBuilder, KimBuilder, LibParamBuilder,
               PairBuilder, ParamFileBuilder)

def build_lammps_potential(pair_style, **kwargs):
    
    subclasses = [PairBuilder, ParamFileBuilder, LibParamBuilder, 
                  EamBuilder, EimBuilder, KimBuilder]
    # Strip acceleration tags
    gputags = ['gpu', 'intel', 'kk', 'omp', 'opt']
    terms = pair_style.split('/')
    if terms[-1] in gputags:
        base_pair_style = '/'.join(terms[:-1])
    else:
        base_pair_style = pair_style

    # Identify builder to use
    match = False
    for subclass in subclasses:
        if base_pair_style in subclass().supported_pair_styles:
            match = True
            break
    
    if match:
        return subclass(pair_style=pair_style, **kwargs)
    else:
        raise ValueError(f'pair_style {pair_style} not in current list of supported styles')

