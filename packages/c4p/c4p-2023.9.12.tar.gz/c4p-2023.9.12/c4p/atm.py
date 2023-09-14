import os, glob
import numpy as np
from IPython.display import display, Image, IFrame
from datetime import date
import xarray as xr

from . import utils

cwd = os.path.dirname(__file__)

class ATM:
    def __init__(self, grids_dirpath=None, path_create_ESMF_map_sh=None, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v

        self.grids_dirpath='/glade/p/cesmdata/inputdata/share/scripgrids' if grids_dirpath is None else grids_dirpath
        self.path_create_ESMF_map_sh=os.path.join(cwd, './src/rof/create_ESMF_map.sh') if path_create_ESMF_map_sh is None else path_create_ESMF_map_sh
        self.configs = {}

        for k, v in self.__dict__.items():
            utils.p_success(f'>>> ATM.{k}: {v}')

    def gen_topo(self, path_topo, path_mk_10min_topo_ncl=os.path.join(cwd, './src/atm/mk_10min_definesurf_input_paleo.ncl')):
        utils.p_header('>>> Create a 10min topographic file ...')
        fpath_ncl = utils.copy(path_mk_10min_topo_ncl, 'mk_ocninput.ncl')
        utils.replace_str(
            fpath_ncl,
            {
                '<casename>': self.casename,
                '<directory_with_topo-bath_file>': os.path.dirname(path_topo),
                '<topo-bath_file>': os.path.basename(path_topo),
            },
        )
        utils.run_shell(f'source $LMOD_ROOT/lmod/init/zsh && module load ncl && ncl {fpath_ncl}', timeout=3)

    def gen_boundary(self):
        utils.p_header('>>> Create boundary dataset for topography fields ...')
        # TODO
        # Step 29, 30

    def gen_solar_forcing(self):
        utils.p_header('>>> Create solar forcing file ...')
        # TODO
        # Step 31

    def gen_aerosol(self):
        utils.p_header('>>> Customize aerosol settings ...')
        # TODO
        # Step 32
