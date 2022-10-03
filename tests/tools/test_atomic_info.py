from potentials.tools.atomic_info import atomic_mass, atomic_number, atomic_symbol

import numpy as np

def test_atomic_info():

    assert atomic_symbol(46) == 'Pd'
    assert atomic_number('U') == 92
    assert np.isclose(atomic_mass('Be'), 9.0121831)
