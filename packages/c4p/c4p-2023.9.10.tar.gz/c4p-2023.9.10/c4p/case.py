import os
import shutil
from datetime import date

from . import utils
from .rof import ROF
from .ocn import OCN
from .lnd import LND
from .atm import ATM
from .mapping import Mapping

cwd = os.path.dirname(__file__)

class PaleoSetup:
    def __init__(self, casename=None, work_dirpath=None, account=None, lmod_path=None, esmfbin_path=None, netcdf_lib_path=None, netcdf_inc_path=None, clean_old=False):
        self.casename = casename
        self.account = account
        self.work_dirpath = work_dirpath
        self.lmod_path = '/glade/u/apps/derecho/23.06/spack/opt/spack/lmod/8.7.20/gcc/7.5.0/pdxb/lmod' if lmod_path is None else lmod_path
        self.esmfbin_path = '/glade/u/apps/derecho/23.06/spack/opt/spack/esmf/8.4.2/cray-mpich/8.1.25/oneapi/2023.0.0/fslf/bin' if esmfbin_path is None else esmfbin_path
        self.netcdf_lib_path = '/glade/u/apps/derecho/23.06/spack/opt/spack/netcdf/4.9.2/oneapi/2023.0.0/iijr/lib' if netcdf_lib_path is None else netcdf_lib_path
        self.netcdf_inc_path = '/glade/u/apps/derecho/23.06/spack/opt/spack/netcdf/4.9.2/oneapi/2023.0.0/iijr/include' if netcdf_inc_path is None else netcdf_inc_path

        if clean_old:
            shutil.rmtree(work_dirpath) if os.path.exists(work_dirpath) else None

        if not os.path.exists(work_dirpath):
            os.makedirs(work_dirpath, exist_ok=True)
            utils.p_success(f'>>> {work_dirpath} created')

        os.chdir(work_dirpath)
        utils.p_success(f'>>> Current directory switched to: {work_dirpath}')

    def mapping(self, atm_grid, ocn_grid, rof_grid, gen_cesm_maps_script=None, gen_esmf_map_script=None, gen_domain_exe=None):
        return Mapping(
            atm_grid=atm_grid, ocn_grid=ocn_grid, rof_grid=rof_grid,
            gen_cesm_maps_script=gen_cesm_maps_script,
            gen_esmf_map_script=gen_esmf_map_script,
            gen_domain_exe=gen_domain_exe, **self.__dict__,
        )

    def setup_rof(self):
        return ROF(**self.__dict__)

    def setup_ocn(self):
        return OCN(**self.__dict__)

    def setup_lnd(self):
        return LND(**self.__dict__)

    def setup_atm(self):
        return ATM(**self.__dict__)

class CESMCase: 
    def __init__(self,
        account=None, casename=None, codebase=None,
        res=None, machine=None, compset=None,
        case_root=None, output_root=None, clean_old=True,
    ):
        self.account = account
        self.casename = casename
        self.res = res
        self.machine = 'derecho' if machine is None else machine
        self.compset = compset
        self.codebase = codebase
        self.case_dirpath = os.path.join(case_root, casename)
        self.output_root = output_root
        self.output_dirpath = os.path.join(output_root, casename)

        for k, v in self.__dict__.items():
            utils.p_success(f'>>> CESMCase.{k}: {v}')

        if clean_old:
            shutil.rmtree(self.case_dirpath) if os.path.exists(self.case_dirpath) else None
            shutil.rmtree(self.output_dirpath) if os.path.exists(self.output_dirpath) else None

    def create(self, run_unsupported=False):
        cmd = f'{self.codebase}/cime/scripts/create_newcase --case {self.case_dirpath} --res {self.res} --compset {self.compset} --output-root {self.output_root}'
        if run_unsupported:
            cmd += ' --run-unsupported'

        os.environ['PROJECT'] = self.account
        utils.run_shell(cmd)
        os.chdir(self.case_dirpath)
        utils.p_success(f'>>> Current directory switched to: {self.case_dirpath}')

    def xmlquery(self, string):
        utils.run_shell(f'./xmlquery -p {string}')

    def xmlchange(self, modification_dict):
        for k, v in modification_dict.items():
            utils.run_shell(f'./xmlchange {k}={v}')

    def setup(self):
        utils.run_shell('./case.setup')

    def build(self, clean=False):
        cmd = './case.build'
        if clean:
            cmd += ' --clean'
            utils.run_shell(cmd)
        else:
            utils.qcmd_script(cmd, account=self.account)

    def submit(self):
        utils.run_shell('./case.submit')

    def preview_run(self):
        utils.run_shell('./preview_run')

    def preview_namelists(self):
        utils.run_shell('./preview_namelists')

    def write_file(self, fname, content=None, mode='w'):
        utils.write_file(fname=fname, content=content, mode=mode)

    def set_paths(self, atm_domain=None, lnd_domain=None, ocn_domain=None, ice_domain=None,
                  atm2ocn_fmap=None, atm2ocn_smap=None, atm2ocn_vmap=None,
                  ocn2atm_fmap=None, ocn2atm_smap=None,
                  lnd2rof_fmap=None,
                  rof2lnd_fmap=None,
                  rof2ocn_fmap=None, rof2ocn_rmap=None):
        if atm_domain is not None: self.xmlchange({'ATM_DOMAIN_PATH': os.path.dirname(atm_domain), 'ATM_DOMAIN_FILE': os.path.basename(atm_domain)})
        if lnd_domain is not None: self.xmlchange({'LND_DOMAIN_PATH': os.path.dirname(lnd_domain), 'LND_DOMAIN_FILE': os.path.basename(lnd_domain)})
        if ocn_domain is not None: self.xmlchange({'OCN_DOMAIN_PATH': os.path.dirname(ocn_domain), 'OCN_DOMAIN_FILE': os.path.basename(ocn_domain)})
        if ice_domain is not None: self.xmlchange({'ICE_DOMAIN_PATH': os.path.dirname(ice_domain), 'ICE_DOMAIN_FILE': os.path.basename(ice_domain)})
        if atm2ocn_fmap is not None: self.xmlchange({'ATM2OCN_FMAPNAME': atm2ocn_fmap})
        if atm2ocn_smap is not None: self.xmlchange({'ATM2OCN_SMAPNAME': atm2ocn_smap})
        if atm2ocn_vmap is not None: self.xmlchange({'ATM2OCN_VMAPNAME': atm2ocn_vmap})
        if ocn2atm_fmap is not None: self.xmlchange({'OCN2ATM_FMAPNAME': ocn2atm_fmap})
        if ocn2atm_smap is not None: self.xmlchange({'OCN2ATM_SMAPNAME': ocn2atm_smap})
        if lnd2rof_fmap is not None: self.xmlchange({'LND2ROF_FMAPNAME': lnd2rof_fmap})
        if rof2lnd_fmap is not None: self.xmlchange({'ROF2LND_FMAPNAME': rof2lnd_fmap})
        if rof2ocn_fmap is not None: self.xmlchange({'ROF2OCN_FMAPNAME': rof2ocn_fmap})
        if rof2ocn_rmap is not None: self.xmlchange({'ROF2OCN_RMAPNAME': rof2ocn_rmap})

    def add_mod(self, component, mod_path):
        target_dir = os.path.join(self.case_dirpath, 'SourceMods', f'src.{component}')
        utils.copy(mod_path, target_dir)
        utils.p_success(f'>>> Copy {mod_path} to: {target_dir}')

        