from analyse.parallel_collect_stats.data_class import MlModelData
from analyse.parallel_collect_stats.func_file import rewrite_stats_files
from analyse.parallel_collect_stats.start_parallel_workers import event_pool_analyse

if __name__ == "__main__":
    # Input data
    data_for_ml = MlModelData(checkpoint_file_path="post_processing/cleaning/tf_neural_net/weight_data/cp.ckpt")
    input_dir = "data/new_format_tracks_data"

    # Prepare result stats files
    rewrite_stats_files()

    # Start analyse
    event_pool_analyse(data_for_ml=data_for_ml,
                       input_dir=input_dir,
                       num_workers=1,  # not recommend to set more than there are logical processors
                       start_event=0,
                       end_event=0)
