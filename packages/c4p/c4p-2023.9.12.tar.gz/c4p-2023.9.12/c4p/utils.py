import os, sh
import shutil
import subprocess
import colorama as ca
from tqdm import tqdm


def p_header(text):
    print(ca.Fore.CYAN + ca.Style.BRIGHT + text)
    print(ca.Style.RESET_ALL, end='')

def p_hint(text):
    print(ca.Fore.LIGHTBLACK_EX + ca.Style.BRIGHT + text)
    print(ca.Style.RESET_ALL, end='')

def p_success(text):
    print(ca.Fore.GREEN + ca.Style.BRIGHT + text)
    print(ca.Style.RESET_ALL, end='')

def p_fail(text):
    print(ca.Fore.RED + ca.Style.BRIGHT + text)
    print(ca.Style.RESET_ALL, end='')

def p_warning(text):
    print(ca.Fore.YELLOW + ca.Style.BRIGHT + text)
    print(ca.Style.RESET_ALL, end='')

def replace_str(fpath, d):
    ''' Replace the string in a given text file according
    to the dictionary `d`
    '''
    with open(fpath, 'r') as f:
        text = f.read()
        for k, v in d.items():
            search_text = k
            replace_text = v
            text = text.replace(search_text, replace_text)

    with open(fpath, 'w') as f:
        f.write(text)

def run_shell(cmd, timeout=None):
    print(f'CMD >>> {cmd}')
    try:
        subprocess.run(cmd, timeout=timeout, shell=True)
    except:
        pass

def svn_export(url, fpath=None):
    if fpath is None:
        fpath = os.path.basename(url)

    if os.path.exists(fpath): os.remove(fpath)
    run_shell(f'svn export {url} {fpath}')
    return fpath

def copy(src, dst=None):
    if dst is None:
        dst = os.path.basename(src)

    dst = os.path.abspath(dst)
    sh.cp(src, dst)
    return dst

def exec_script(fpath, args=None, timeout=None, chmod_add_x=True):
    if chmod_add_x:
        run_shell(f'chmod +x {fpath}')

    if args is None:
        cmd = fpath
    else:
        cmd = f'{fpath} {args}'

    run_shell(cmd, timeout=timeout)

def make_pbs(fpath, args=None, name='test', queue='main', select=1, ncpus=36, mpiprocs=36, mem=64, walltime='06:00:00', account=None):
    if account is None:
        raise ValueError('account must be specified')

    if args is None:
        cmd = fpath
    else:
        cmd = f'{fpath} {args}'

    fname = f'pbs_{name}.zsh'
    with open(fname, 'w') as f:
        f.write(f'''#!/bin/zsh
#PBS -N {name}
#PBS -q {queue}
#PBS -l select={select}:ncpus={ncpus}:mpiprocs={mpiprocs}:mem={mem}GB
#PBS -l walltime={walltime}
#PBS -A {account}

{cmd}
                ''')

    p_success(f'>>> {fname} created')

def qsub_script(fpath, args=None, name='test', queue='main', select=1, ncpus=36, mpiprocs=36, mem=64, walltime='06:00:00', account=None):
    if account is None:
        raise ValueError('account must be specified')

    make_pbs(fpath, args=args, name=name, queue=queue, select=select, ncpus=ncpus, mpiprocs=mpiprocs, mem=mem, walltime=walltime, account=account)
    run_shell(f'qsub pbs_{name}.zsh')
    
def qcmd_script(fpath, args=None, name='test', queue='main', select=1, ncpus=36, mpiprocs=36, mem=64, walltime='06:00:00', account=None, **env_vars):
    if account is None:
        raise ValueError('account must be specified')

    env_str = ''
    for k, v in env_vars.items():
        env_str += f'{k}="{v},"'

    if args is None:
        cmd = fpath
    else:
        cmd = f'{fpath} {args}'

    l1 = f'select={select}:ncpus={ncpus}:mpiprocs={mpiprocs}:mem={mem}GB'
    l2 = f'walltime={walltime}'

    run_shell(f'qcmd -N {name} -q {queue} -l {l1} -l {l2} -A {account} -- {cmd}')

def write_file(fname, content=None, mode='w'):
    if content is None:
        raise ValueError('Please assign the value for `content`.')

    with open(fname, mode) as f:
        f.write(f'''{content}''')

class PDF(object):
  def __init__(self, pdf, size=(200,200)):
    self.pdf = pdf
    self.size = size

  def _repr_html_(self):
    return '<iframe src={0} width={1[0]} height={1[1]}></iframe>'.format(self.pdf, self.size)

  def _repr_latex_(self):
    return r'\includegraphics[width=1.0\textwidth]{{{0}}}'.format(self.pdf)