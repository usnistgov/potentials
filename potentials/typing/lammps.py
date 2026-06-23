
class lammps():
    """Dummy lammps class for typing when lammps is not installed."""
    
    def __init__(self, *args, **kwargs):
        raise ImportError('lammps Python interface not found!')
    def version(self):
        return '19000101'

# Data Types
LAMMPS_INT: int = 0
LAMMPS_INT_2D: int = 1
LAMMPS_DOUBLE: int = 2
LAMMPS_DOUBLE_2D: int = 3
LAMMPS_INT64: int = 4
LAMMPS_INT64_2D: int = 5
LAMMPS_STRING: int = 6

# Style Constants
LMP_STYLE_GLOBAL: int = 0
LMP_STYLE_ATOM: int = 1
LMP_STYLE_LOCAL: int = 2

# Type Constants
LMP_TYPE_SCALAR: int = 0
LMP_TYPE_VECTOR: int = 1
LMP_TYPE_ARRAY: int = 2
LMP_SIZE_VECTOR: int = 3
LMP_SIZE_ROWS: int = 4
LMP_SIZE_COLS: int = 5

# Variable Type Constants
LMP_VAR_EQUAL: int = 0
LMP_VAR_ATOM: int = 1