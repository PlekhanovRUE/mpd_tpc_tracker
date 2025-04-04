import os
import sys
import subprocess
from argparse import ArgumentParser
from parallel_analyse_example import run_parallel
from analyse.count_fakes_v2 import count_fakes
from config import SettingParams


def main():
    '''main func to run the whole post processing'''

    parser = ArgumentParser(
        usage='''
    To run without plotting graphs specify -no_plot flag:
        python run_post_processing.py -no_plot
    To run with plotting all available plots and default path directories:
        python run_post_processing.py
    Run python run_post_processing.py -h for more information about args and keys.
        ''',
        description='Post Processing Runner')

    parser.add_argument('-no_plot',
                        dest='plot_graphs',
                        action='store_false',
                        help='plot root graphs (default: True)')
    parser.add_argument('-plot_args',
                        dest='plot_args',
                        default='all',
                        choices=['eff_pt', 'eff_eta', 'eff_mult',
                                 'duplicates_pt', 'duplicates_eta',
                                 'duplicates_mult', 'fakes_mult',
                                 'all'],
                        help='params to plot graphs (default: all)')
    parser.add_argument('-input_dir',
                        dest='input_dir',
                        default=SettingParams.input_dir,
                        help='directory with event files')
    parser.add_argument('-result_dir',
                        dest='result_dir',
                        default=".",
                        help='directory with post processing results')

    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print('Wrong input dir path.')
        sys.exit(1)
    if not os.path.isdir(args.result_dir):
        print('Wrong result dir path.')
        sys.exit(1)
    run_parallel()
    if len(os.listdir(args.result_dir)) < 1:
        print('Result dir is empty.')
        sys.exit(1)
    count_fakes(args.result_dir)
    if args.plot_graphs:
        if args.plot_args == 'all':
            for plot_arg in (('eff', 'pt'), ('eff', 'eta'), ('eff', 'mult'),
                             ('duplicates', 'pt'), ('duplicates', 'eta'),
                             ('duplicates', 'mult'), ('fakes', 'mult')):
                cmd = ["root", "-q",
                       f"analyse/plotgraphs.C(\"{args.result_dir}\", \"{args.result_dir}\", "
                       f"\"\", {plot_arg[0]}, {plot_arg[1]})"]
                with subprocess.Popen(cmd, text=True) as process_paint:
                    process_paint.wait()
        else:
            y, x = args.plot_args.split("_", maxsplit=1)
            cmd = ["root", "-q",
                   f"analyse/plotgraphs.C(\"{args.result_dir}\", \"{args.result_dir}\", "
                   f"\"\", {y}, {x})"]
            with subprocess.Popen(cmd, text=True) as process_paint:
                process_paint.wait()


if __name__ == "__main__":
    main()
