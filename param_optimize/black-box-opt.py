from functools import partial
import threading
import os
import sys
import json
import logging
import warnings
import datetime
import optuna
from acts_launcher import run
from argparse import ArgumentParser

warnings.filterwarnings("ignore", category=optuna.exceptions.ExperimentalWarning)

id_threads = {}
id_curr = 1

search_space = {}

fixed_params = {
    "EtaMax": 2.11,
    "PtMin": 0.0,
    "CollisionZmin": -300.0,
    "CollisionZmax": 300.0,
    "SeedBinSizeR": 10.0,
    "SeedDeltaRmin": 10.0,
    "SeedDeltaRmax": 60.0,
    "SeedDeltaZmax": 200.0,
    "MaxSeedsPerSpM": 3,
    "SigmaScattering": 5,
    "MaxPtScattering": 5.0,
    "RadLengthPerSeed": 0.05,
    "BeamX": 0.0,
    "BeamY": 0.0,
    "ImpactMax": 30.0,
    "SigmaLoc0": 0.5,
    "SigmaLoc1": 0.5,
    "SigmaPhi": 0.00872665,
    "SigmaTheta": 0.00872665,
    "SigmaQOverP": 0.1,
    "SigmaT0": 2000.0,
    "InitVarInflatLoc0": 1.0,
    "InitVarInflatLoc1": 1.0,
    "InitVarInflatPhi": 1.0,
    "InitVarInflatTheta": 1.0,
    "InitVarInflatQOverP": 1.0,
    "InitVarInflatT0": 1.0,
    "ResolvePassive": False,
    "ResolveMaterial": True,
    "ResolveSensitive": True,
    "PropagationMaxSteps": 1000,
    "MultipleScattering": True,
    "EnergyLoss": True,
    "Smoothing": True,
    "Chi2max": 30.0,
    "NmaxPerSurface": 5,
    "ComputeSharedHits": False,
    "TrackMinLength": 4,
    "NewHitsInRow": 6,
    "NewHitsRatio": 0.25,
    "PostProcess": False,
    "SelectorEnabled": True,
    "PrimaryParticlesOnly": True,
    "SelectorPhiMin": -3.15,
    "SelectorPhiMax": 3.15,
    "AbsEtaMin": 0,
    "SelectorPtMax": 10.0,
    "KeepNeutral": False,
    "NHitsMin": 9,
    "TruthMatchProbMin": 0.5,
    "MeasurementsMin": 6,
    "EtaNBins": 40,
    "PhiNBins": 100,
    "PtNBins": 40,
    "PerfPlotToolPtMin": 0.0,
    "PerfPlotToolPtMax": 2.5,
    "NumNBins": 30,
    "NumMin": -0.5,
    "NumMax": 29.5,
    "OnlyCertainTracks": False,
    "DumpData": False,
    "WriteTrajSummary": False
}

samplers_optuna = {
    'grid': optuna.samplers.GridSampler(search_space),
    'random': optuna.samplers.RandomSampler(seed=0),
    'tpe': optuna.samplers.TPESampler(),
    'cmaes': optuna.samplers.CmaEsSampler(),
    'nsgaii': optuna.samplers.NSGAIISampler(),
    'qmc': optuna.samplers.QMCSampler(),
    'gp': optuna.samplers.GPSampler(seed=0),
    'bayes': optuna.integration.BoTorchSampler()
}


def to_json(dct_vals: dict):
    '''dump to json'''

    thread_id = threading.current_thread().ident
    if thread_id not in id_threads:
        global id_curr
        id_threads[thread_id] = id_curr
        id_curr += 1
    name_json = f'acts_params_config_{id_threads[thread_id]}.json'
    with open(name_json, 'w', encoding='utf-8') as f:
        json.dump(dct_vals, f, indent=4)
    return name_json


def opt_func(dct_params: dict, n_events: int):
    '''func to optimize (black-box)'''

    dct_vals = {**dct_params, **fixed_params}
    name = to_json(dct_vals)
    eff_sel, eff_all, fake_sel, fake_all, memory = run(name, n_events=n_events)
    return eff_sel, eff_all, fake_sel, fake_all, memory


def write_log(_, trial):
    '''custom callback'''

    eff_sel, eff_all, fake_sel, fake_all, memory = trial.values

    params = {repr(key): val for key, val in trial.params.items()}
    num = trial.number

    duration_sec = trial.duration.total_seconds()
    minutes = round((duration_sec % 3600) / 60, 3)

    dr = f'\n\t"duration(min)": {minutes},'
    me = f'\n\t"memory": {memory},'
    es = f'\n\t"eff_sel": {eff_sel},'
    ea = f'\n\t"eff_all": {eff_all},'
    fs = f'\n\t"fake_sel": {fake_sel},'
    fa = f'\n\t"fake_all": {fake_all},'
    pm = f'\n\t"params": {params}'

    msg = f'"{num}": {{{dr}{me}{es}{ea}{fs}{fa}{pm}}},'

    logging.info(msg)


def objective(trial, n_events):
    '''optuna func to optimize'''

    # #SeedBinSizeR = trial.suggest_int("SeedBinSizeR", 6, 36, step=1) # no-effect
    # SeedDeltaRmin = trial.suggest_int("SeedDeltaRmin", 5, 20, step=1)
    # SeedDeltaRmax = trial.suggest_int("SeedDeltaRmax", 30, 120, step=2)
    # SeedDeltaZmax = trial.suggest_int("SeedDeltaZmax", 100, 400, step=2)
    # SigmaScattering = trial.suggest_int("SigmaScattering", 1, 10, step=1)
    # MaxPtScattering = trial.suggest_int("MaxPtScattering", 1, 5, step=1)
    # RadLengthPerSeed = trial.suggest_float("RadLengthPerSeed", 0.01, 0.1, step=0.01)
    # Chi2max = trial.suggest_int("Chi2max", 15, 60, step=5)
    # MaxSeedsPerSpM = trial.suggest_int("MaxSeedsPerSpM", 1, 10, step=1)
    # ImpactMax = trial.suggest_int("ImpactMax", 10, 100, step=5)
    # PropagationMaxSteps = trial.suggest_int("PropagationMaxSteps", 100, 1000, step=100)
    # #NmaxPerSurface = trial.suggest_int("NmaxPerSurface", 1, 10, step=1) # no-effect
    # EtaMax = trial.suggest_float("EtaMax", 1.8, 2.2, step=0.04)
    # PtMin = trial.suggest_float("PtMin", 0.04, 0.1, step=0.002)
    # BeamX = trial.suggest_int("BeamX", 0, 10, step=1)
    # BeamY = trial.suggest_int("BeamY", 0, 10, step=1)
    NumLayers = trial.suggest_int("NumLayers", 171, 229, step=2)
    NumSectors = trial.suggest_int("NumSectors", 151, 209, step=2)

    dct_params = {
        "NumLayers": NumLayers,
        "NumSectors": NumSectors
    }
    
    eff_sel, eff_all, fake_sel, fake_all, memory = opt_func(dct_params, n_events)

    return eff_sel, eff_all, fake_sel, fake_all, memory


def run_optimization(logdir: str,
                     n_trials: int or None,
                     method: str,
                     n_events: int,
                     n_jobs: int):
    '''main func for optimization'''

    if not os.path.isdir(logdir):
        new_dirpath = os.path.join(os.getcwd(), logdir)
        os.mkdir(new_dirpath)

    curr_time = datetime.datetime.now()
    timestamp = datetime.datetime.strftime(curr_time, "%Y-%d-%m-%H-%M-%S")
    logging.basicConfig(
        filename=f'{logdir}/param_history_{timestamp}.json',
        filemode='w', encoding='utf-8',
        level=logging.INFO,
        format='%(message)s'
    )

    if method in samplers_optuna:
        sampler = samplers_optuna[method]
    else:
        print('Incorrect method type. ',
              'See possible choices by running black-box-opt.py -h')
        sys.exit(1)

    study = optuna.create_study(
        directions=["maximize", "maximize", "minimize", "minimize", "minimize"],
        sampler=sampler
    )
    if n_trials < 1:
        n_trials = None

    study.optimize(partial(objective, n_events=n_events), n_trials=n_trials, callbacks=[write_log], n_jobs=n_jobs)
    best_trial = max(study.best_trials, key=lambda t: t.values[0])
    best_params = best_trial.params

    with open('best_params.json', 'w', encoding='utf-8') as f:
        json.dump({**best_params, **fixed_params}, f, indent=4)


def main():
    parser = ArgumentParser(
        usage='''
    black-box-opt.py <optional params>
    Example: black-box-opt.py -logdir logs -n_trials 100 -method random -n_events 20
    Run black-box-opt.py -h for more information about args.
        ''',
        description='Param optimization')

    parser.add_argument('-logdir',
                        help='directory where optimization logs will be saved',
                        default='log_params')
    parser.add_argument('-n_trials',
                        help='number of optimizer iterations',
                        type=int,
                        default=200)
    parser.add_argument('-method',
                        choices=['random', 'tpe', 'cmaes', 'nsgaii', 'qmc', 'gp', 'bayes'],
                        default='random',
                        help='method by which the search for optimal parameters is carried out')
    parser.add_argument('-n_events',
                        default=20,
                        type=int,
                        help='number of events for tracker')
    parser.add_argument('-n_jobs',
                        default=1,
                        type=int,
                        help='number of parallel jobs')
    
    args = parser.parse_args()
    if args.n_jobs < 1 or args.n_jobs > os.cpu_count():
        print('Wrong n_jobs is specified.')
        sys.exit()

    run_optimization(args.logdir, args.n_trials, args.method, args.n_events, args.n_jobs)


if __name__ == "__main__":
    main()
