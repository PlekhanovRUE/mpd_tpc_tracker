import datetime
import os
import re
import shutil
import subprocess

# import logging
# my_logger = logging.getLogger('my_logger')
# my_logger.setLevel(logging.DEBUG)

def gen_logfile_name(postfix=''):
    now = datetime.datetime.now()
    timestamp = datetime.datetime.strftime(now, '%Y-%d-%m-%H-%M-%S')
    return f"acts_{timestamp}{postfix}.txt"


def save_log(path, stdout, zip_log=True, postfix=''):

    fshort = gen_logfile_name(postfix)
    fname = os.path.join(path, fshort)

    with open(fname, 'w') as f:
        f.write(stdout)
    if zip_log:
        subprocess.run(['gzip', fname])


def get_mpdroot_bin_dir():
    if 'VMCWORKDIR' not in os.environ:
        raise ValueError('VMCWORKDIR environment variable is not set. '
                         'Please run <MPDROOT_INSTALLATION_DIR>/config/env.sh')
    return os.environ['VMCWORKDIR']


def _run_acts(
        infile,
        json_fname,
        outfile=None,
        start_event=None,
        n_events=None,
        digi=None):

    bin_dir = get_mpdroot_bin_dir()
    macro = os.path.join(bin_dir, 'macros', 'common', 'runReco.C')
    macro_s = f'{macro}("{infile}", "{outfile}", {start_event}, ' + \
              f'{n_events}, {digi}, ETpcTracking::ACTS, ' + \
              f'EQAMode::OFF, "{json_fname}")'
    cmd_l = ['root', '-q', '-b', f"'{macro_s}'"]
    cmd_s = ' '.join(cmd_l)

    # To estimate memory consumption
    cmd_s = "/usr/bin/time -v " + cmd_s

    out = subprocess.run(
            cmd_s, text=True, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return out.stdout


def parse_line(line, recompile, type_to_cast=float):
    match = recompile.match(line)
    if not match:
        return
    val_s = match.group(1)
    val = None
    try:
        val = type_to_cast(val_s)
    except:
        print(f'Error: can not convert "{val_s}" to {type_to_cast}')
    return val


def parse_output(arg):
    eff_sel_compile  = re.compile("^Total efficiency.* (.*)$")
    fake_sel_compile = re.compile("^Total fake rate.* (.*)$")
    memory_compile   = re.compile("^.*Memory.*virtual (.*) KB$")

    eff_sel  = None
    fake_sel = None
    memory   = None
    arg_sp = arg.split(os.linesep)

    for l in arg_sp:
        if (v1 := parse_line(l, eff_sel_compile))  is not None: eff_sel  = v1
        if (v2 := parse_line(l, fake_sel_compile)) is not None: fake_sel = v2
        if (v3 := parse_line(l, memory_compile, type_to_cast=int)) is not None:
            memory = v3

    eff_sel  = -1 if eff_sel  is None else eff_sel
    fake_sel = -1 if fake_sel is None else fake_sel
    memory   = -1 if memory   is None else memory

    return eff_sel, fake_sel, memory


def check_path_exist(path):
    if not os.path.exists(path):
        raise ValueError(f'"{path}" does not exist!')


def check_params(json_fname, json_out_dir, infile):
    check_path_exist(json_fname)
    check_path_exist(json_out_dir)
    check_path_exist(infile)


# Run ACTS, parse stdout, return list of values.
# Every return value must be non-negative, otherwise some error occured.
def run_acts(
        infile,
        json_fname,
        json_out_dir=None, # if empty then will be set to $VMCWORKDIR/etc
        outfile='',
        start_event=0,
        n_events=2,
        log=False,
        log_dir='',
        log_postfix=''):

    bin_dir = get_mpdroot_bin_dir()
    if not json_out_dir:
        json_out_dir = os.path.join(bin_dir, 'etc')

    check_params(json_fname, json_out_dir, infile)

#   shutil.copy(json_fname, os.path.join(bin_dir, 'etc'))
    # full path to not raise exception on file already exists
    json_fname_out = os.path.join(json_out_dir, json_fname)
    shutil.move(json_fname, json_fname_out)

    if not outfile:
        outfile = os.path.join(bin_dir, 'macros', 'common', 'dst.root')

    stdout = _run_acts(
        infile=infile,
        json_fname=json_fname_out,
        start_event=start_event,
        n_events=n_events,
        outfile=outfile,
        digi="ETpcClustering::MLEM")
    if log or log_dir:
        save_log(log_dir, stdout, postfix=log_postfix)
    eff_sel, fake_sel, memory = parse_output(stdout)
    return eff_sel, fake_sel, memory


def test(infile, json):
#infile = '/path/to/input/root/file'
#json = '/path/to/acts_params_config.json'
    eff = run_acts(infile=infile, json_fname=json, log=True, log_dir='/tmp')
    print(f"eff = {eff}")
#   logging.warning(f"{eff=}")
