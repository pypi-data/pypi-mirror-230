import os
from datetime import date

from . import utils

cwd = os.path.dirname(__file__)

class Mapping:
    def __init__(self, atm_grid, ocn_grid, rof_grid, job_name=None,
                 gen_cesm_maps_script=None, gen_esmf_map_script=None, gen_domain_exe=None,
                 **kwargs):
        '''Generate mapping and domain files

        Args:
            atm_grid (dict): grid information for atm in the format of {grid_name: path_to_scrip_file}
            ocn_grid (dict): grid information for ocn in the format of {grid_name: path_to_scrip_file}
            rof_grid (dict): grid information for rof in the format of {grid_name: path_to_scrip_file}
        '''
        for k, v in kwargs.items():
            self.__dict__[k] = v

        self.job_name = 'mapping' if job_name is None else job_name
        self.atm_grid_name, self.atm_scrip  = list(atm_grid.keys())[0], list(atm_grid.values())[0]
        self.ocn_grid_name, self.ocn_scrip  = list(ocn_grid.keys())[0], list(ocn_grid.values())[0]
        self.rof_grid_name, self.rof_scrip  = list(rof_grid.keys())[0], list(rof_grid.values())[0]

        # paths for mapping and domain generation scripts
        self.gen_cesm_maps_script = os.path.join(cwd, './src/cime_mapping/gen_cesm_maps.ncpu36.sh') if gen_cesm_maps_script is None else gen_cesm_maps_script
        self.gen_esmf_map_script = os.path.join(cwd, './src/cime_mapping/create_ESMF_map.sh') if gen_esmf_map_script is None else gen_esmf_map_script
        self.gen_domain_exe = os.path.join(cwd, './src/cime_mapping/gen_domain') if gen_domain_exe is None else gen_domain_exe

        for k, v in self.__dict__.items():
            utils.p_success(f'>>> Mapping.{k}: {v}')

    def ocn2atm(self, **qsub_kws):
        utils.p_header(f'>>> Creating ocean<->atmosphere mapping files')
        utils.qsub_script(
            self.gen_cesm_maps_script,
            args=f'-fatm {self.atm_scrip} -natm {self.atm_grid_name} -focn {self.ocn_scrip} -nocn {self.ocn_grid_name} --nogridcheck',
            name=self.job_name, account=self.account, **qsub_kws,
        )

    def rof2atm(self, **qsub_kws):
        utils.p_header(f'>>> Creating river->atmosphere(land) mapping files')
        utils.qsub_script(
            self.gen_esmf_map_script,
            args=f'-fsrc {self.rof_scrip} -nsrc {self.rof_grid_name} -fdst {self.atm_scrip} -ndst {self.atm_grid_name} -map aave',
            name=self.job_name, account=self.account, **qsub_kws,
        )
    
    def atm2rof(self, **qsub_kws):
        utils.p_header(f'>>> Creating atmosphere(land)->river mapping files')
        utils.qsub_script(
            self.gen_esmf_map_script,
            args=f'-fsrc {self.atm_scrip} -nsrc {self.atm_grid_name} -fdst {self.rof_scrip} -ndst {self.rof_grid_name} -map aave',
            name=self.job_name, account=self.account, **qsub_kws,
        )
        
    def rof2ocn(self, **qsub_kws):
        utils.p_header(f'>>> Creating river->ocean mapping files')
        utils.qsub_script(
            self.gen_esmf_map_script,
            args=f'-fsrc {self.rof_scrip} -nsrc {self.rof_grid_name} -fdst {self.ocn_scrip} -ndst {self.ocn_grid_name} -map aave',
            name=self.job_name, account=self.account, **qsub_kws,
        )

    def gen_mapping(self, **qsub_kws):
        self.ocn2atm(**qsub_kws)
        self.atm2rof(**qsub_kws)
        self.rof2atm(**qsub_kws)
        self.rof2ocn(**qsub_kws)

    def gen_domain(self, **qsub_kws):
        utils.p_header(f'>>> Creating ocean<->atmosphere domain files')
        date_today = date.today().strftime('%y%m%d')
        utils.qsub_script(
            self.gen_domain_exe,
            args=f'-m map_{self.ocn_grid_name}_TO_{self.atm_grid_name}_aave.{date_today}.nc -o {self.ocn_grid_name} -l {self.atm_grid_name}',
            name=self.job_name, account=self.account, **qsub_kws,
        )

    def clean(self):
        utils.run_shell(f'rm -rf {self.job_name}.* PET* pbs_*')