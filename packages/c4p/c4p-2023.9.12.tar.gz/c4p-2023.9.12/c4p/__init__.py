from .case import PaleoSetup
from .case import CESMCase
from .case import Mapping
from .case import ROF

# get the version
from importlib.metadata import version
__version__ = version('c4p')


# mute future warnings from pkgs like pandas
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)