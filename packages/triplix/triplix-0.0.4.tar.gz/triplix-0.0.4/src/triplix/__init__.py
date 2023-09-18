
import triplix.core.configurations as _configurations

_configurations.load_config()

from triplix.core.concatemers import (
    ConcatemersContainer,
)
from triplix.core.tri_alignments import TriAlignmentsContainer
from triplix.core.triplets import TripletsContainer

__version__ = _configurations.configs['version']
__all__ = [
    'ConcatemersContainer', ]
