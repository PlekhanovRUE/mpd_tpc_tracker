import concurrent.futures

from tqdm import tqdm

from analyse.parallel_collect_stats.data_class import MlModelData, OneEventRealTrackParams
from analyse.parallel_collect_stats.func_file import calculate_one_event_stats


def event_pool_analyse(data_for_ml: MlModelData, input_dir: str, start_event: int, end_event: int, num_workers: int):
    # Can be changed to concurrent.futures.ThreadPoolExecutor to use same process core for all threads
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Create work pool
        future_pool = (executor.submit(calculate_one_event_stats,
                                       event_number,
                                       input_dir,
                                       data_for_ml) for event_number in range(start_event, end_event + 1))
        bar_format = "\n\n{n}: events analyzed\n\n"
        pool_size = end_event - start_event

        for future in tqdm(concurrent.futures.as_completed(future_pool), total=pool_size, bar_format=bar_format):
            try:
                event_characteristics: OneEventRealTrackParams = future.result()
                event_characteristics.save_characteristics()
            except Exception as exc:
                print(exc)
            finally:
                pass
