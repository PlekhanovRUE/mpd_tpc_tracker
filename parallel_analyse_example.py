from analyse.parallel_collect_stats.data_class import MlModelData
from analyse.parallel_collect_stats.func_file import rewrite_stats_files
from analyse.parallel_collect_stats.start_parallel_workers import event_pool_analyse
from config import SettingParams


def run_parallel():
    '''main func to run parallel analyse'''
    # Input data
    data_for_ml = MlModelData(
        checkpoint_file_path="post_processing/cleaning/tf_neural_net/weight_data/cp.ckpt")

    # Prepare result stats files
    rewrite_stats_files()

    # Start analyse
    event_pool_analyse(data_for_ml=data_for_ml,
                       input_dir=SettingParams.input_dir,
                       num_workers=SettingParams.num_workers,
                       # not recommend to set more than there are logical processors
                       start_event=SettingParams.start_event,
                       end_event=SettingParams.end_event)


if __name__ == "__main__":
    run_parallel()
