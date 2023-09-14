from pkg_resources import get_distribution, DistributionNotFound

version = get_distribution(__name__).version

from .tools import *
from .toolsDB import *
from .readerCSK import readerCSK
from .readerOnline import readerOnline
from .calibration import *
from .acceptance_tests import acceptance_test
from .calibration_object import calibration_object
from .definitions import *
