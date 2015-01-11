import unittest

from playlists.vote import VoteTracker, Vote

class TestVoting(unittest.TestCase):

    def test_verdict(self):
        vote_tracker = VoteTracker()
        vote_tracker.register_vote("user1", Vote.YES)
        vote_tracker.register_vote("user2", Vote.NO)
        vote_tracker.register_vote("user3", Vote.YES)
        self.assertEqual(vote_tracker.verdict, Vote.YES)
        vote_tracker.register_vote("user1", Vote.NO)
        self.assertEqual(vote_tracker.verdict, Vote.NO)

if __name__ == '__main__':
    unittest.main()
