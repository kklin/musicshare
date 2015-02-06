def to_spotify_track_id(song_obj):
    '''Takes an echonest song object and extracts the spotify track id'''
    # TODO: return None when uri can't be retrieved
    return song_obj.get_tracks('spotify')[0]['foreign_id']
