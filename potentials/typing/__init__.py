"""
Imports for optional dependencies, or creates similar named dummy classes
for typing when optional dependencies are not installed.
"""

from yabadaba.typing import unitfloat

try:
    import lammps
except:
    from . import lammps

__all__ = ['unitfloat', 'lammps']