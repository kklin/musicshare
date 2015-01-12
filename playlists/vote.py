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
        for verdict in self.votes.keys():
            ret += Vote.verdict_to_string(verdict) + " : " + str(len(self.votes[verdict])) + "\n"
        return ret

class Vote(object):
    # TODO: could do this better with some kind of enum
    YES = 1
    NO = -1
    ABSTAIN = 0

    def __init__(self, voter, vote):
        self.voter = voter
        self.vote = vote

    @staticmethod
    def verdict_to_string(verdict):
        if verdict is Vote.YES:
            return "Yes"
        elif verdict is Vote.NO:
            return "No"
        elif verdict is Vote.ABSTAIN:
            return "Abstain"
        else:
            return "UNKNOWN"
