from collections import defaultdict

class VoteTracker(object):

    def __init__(self):
        self.votes = defaultdict(lambda: [])

    @property
    def verdict(self):
        if len(self.votes[Vote.YES]) > len(self.votes[Vote.NO]):
            return Vote.YES
        return Vote.NO

    def register_vote(self, vote):
        self.votes[vote.vote].append(vote.voter)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        ret = ""
        for vote in self.votes.keys():
            ret += str(vote) + " : " + len(self.votes[vote])
        return ret

class Vote(object):
    YES = 1
    NO = -1
    ABSTAIN = 0

    def __init__(self, voter, vote):
        self.voter = voter
        self.vote = vote
