import unittest

from playlists.models import SongList, SongRequest
from playlists import secret
from playlists.vote import Vote

from pyechonest import song, config
config.ECHO_NEST_API_KEY = secret.echo_nest_api_key

class TestSongList(unittest.TestCase):

    def setUp(self):
        self.song_list = SongList()
        self.song_list.add_song_request(SongRequest(song.Song('SOUBXIA1498972C676'), None))
        self.song_list.add_song_request(SongRequest(song.Song('SOWFHVM1315CD4907D'), None))
        self.song_list.add_song_request(SongRequest(song.Song('SOZSJSZ135C25D5D03'), None))
        self.song_list.add_song_request(SongRequest(song.Song('SOWYIGE13739C41CDC'), None))
        self.song_list.add_song_request(SongRequest(song.Song('SODGCAF12AB01818A3'), None))

    def test_ordering(self):
        yes_vote1 = Vote('test', Vote.YES)
        no_vote1 = Vote('test', Vote.NO)
        yes_vote2 = Vote('test2', Vote.YES)
        no_vote2 = Vote('test2', Vote.NO)
        yes_vote3 = Vote('test3', Vote.YES)
        no_vote3 = Vote('test3', Vote.NO)

        # with only one yes vote, that song should be the first song
        self.song_list.set_vote('SOUBXIA1498972C676', yes_vote1)
        ordered = self.song_list.ordered
        self.assertEqual(ordered[0].song.id, 'SOUBXIA1498972C676')

        # in a tie for the top number of votes, both songs should be in the top two
        self.song_list.set_vote('SOWFHVM1315CD4907D', yes_vote1)
        ordered = map(lambda x: x.song.id, self.song_list.ordered)
        self.assertTrue('SOUBXIA1498972C676' in ordered[:2] and
                'SOWFHVM1315CD4907D' in ordered[:2])

        # but if another song gets more votes, it should move into first
        self.song_list.set_vote('SOZSJSZ135C25D5D03', yes_vote2)
        self.song_list.set_vote('SOZSJSZ135C25D5D03', yes_vote3)
        ordered = map(lambda x: x.song.id, self.song_list.ordered)
        self.assertEqual('SOZSJSZ135C25D5D03', ordered[0])
        self.assertTrue('SOUBXIA1498972C676' in ordered[1:3] and
                'SOWFHVM1315CD4907D' in ordered[1:3])

if __name__ == '__main__':
    unittest.main()
