def create_clusters(track_list, min_n_shared_hits):
    # Sort tracks by length in descending order
    trackId_to_hits_dict = {index: value for index, value in enumerate(track_list)}
    # Converting tracks to format as {track_id: hit_id_list}
    sorted_tracks = dict(sorted(trackId_to_hits_dict.items(), key=lambda item: len(item[1]), reverse=True))
    clusters = []
    used_track_id = set()

    for track_id, track in sorted_tracks.items():
        if track_id in used_track_id:
            # If the track already belongs to the cluster, skip it
            continue

        # Create a new cluster with the current track
        current_cluster = [{track_id: track}]
        used_track_id.add(track_id)

        # Checking all other tracks
        for other_track_id, other_track in sorted_tracks.items():
            if other_track_id in used_track_id:
                continue
            # Check the number of shared hits
            if len(set(tuple(row) for row in track) & set(tuple(row) for row in other_track)) >= min_n_shared_hits:
                current_cluster.append({other_track_id: other_track})
                used_track_id.add(other_track_id)

        # Add a cluster to the final list
        clusters.append(current_cluster)

    return clusters
