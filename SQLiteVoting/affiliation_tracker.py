class AffiliationTracker:
    def __init__(self, defined_parties, resident_id, registered_party, independent=False):
        self.total_votes = 0
        self.defined_parties = defined_parties

        # Setup empty arrays of the right length for votes and vote_rates

        # Votes: how many votes each party received, following the order in which they are defined
        self.votes = [0 for party in range(len(defined_parties))]

        # How often this person tends to vote for each party, following the order in which they are defined
        # It is a decimal number between 0 and 1, rounded to 4 decimal places
        self.vote_rates = [0 for party in range(len(defined_parties))]

        self.resident_id = resident_id
        self.registered_party = registered_party
        self.independent = independent if independent == True else True if registered_party == 'U' else False

        # How often this person votes for a different party than the one they are registered for
        # This is stored as a decimal between 0 and 1, rounded to 6 decimal places
        # If they are independent, this is always 0
        self.party_deviation_rate = 0

    def get_party_index_from_abbreviation(self, abbreviation):
        for index in range(len(self.defined_parties)):
            if self.defined_parties[index][0] == abbreviation:
                return index

        raise ValueError("Voted party's symbol is not in list of defined parties!")

    def update_vote_rates(self):
        for index in range(len(self.vote_rates) - 1):
            self.vote_rates[index] = round(self.votes[index] / self.total_votes, 6)

        # Set the last vote_rate to be 1 - (the sum of the others), so it always adds to 100%
        # This accounts for weird rounding
        self.vote_rates[len(self.vote_rates) - 1] = 1 - sum(self.vote_rates[:-1])

        # Calculate deviation rate
        # Check if they are independent
        if self.registered_party == 'U':
            self.party_deviation_rate = 0

    def record_vote(self, party):
        self.total_votes += 1
        self.votes[self.get_party_index_from_abbreviation(party)] += 1
        self.update_vote_rates()
