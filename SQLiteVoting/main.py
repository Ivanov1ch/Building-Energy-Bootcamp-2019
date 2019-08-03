import os
import sqlalchemy
import pandas as pd
from SQLiteVoting.affiliation_tracker import AffiliationTracker

# Define all parties - Format: [(Symbol in DB, Full Name)]
PARTY_DEFINITIONS = [('D', 'Democratic Party'), ('R', 'Republican Party'), ('L', 'Libertarian Party'),
                     ('J', 'Green-Rainbow Party'), ('CC', 'United Independent Party'), ('U', 'Independent')]

# The path to the sqlite file
db_path = os.path.join('SQLiteVoting', 'student.sqlite')
engine = sqlalchemy.create_engine('sqlite:///' + db_path)  # Read the sqlite file into sqlalchemy

# Read the ElectionModel table into a df
df = pd.read_sql_table('ElectionModel_01', engine, parse_dates=True)

# Keep only the important columns
df = df[['party_affiliation', 'resident_id', 'election_type', 'party_voted']].copy()

# Remove all voter data not involving primaries
df = df[df['election_type'].str.contains("PRIMARY")]

# Create an empty list to house AffiliationTrackers
tracker_list = []

# Get all unique resident_ids
resident_ids = df['resident_id'].unique()

for id in resident_ids:
    data_rows = df[df['resident_id'] == id]
    tracker = AffiliationTracker(PARTY_DEFINITIONS, id, data_rows['party_affiliation'].value_counts().idxmax().rstrip())

    for index, primary in data_rows.iterrows():
        tracker.record_vote(primary['party_voted'].rstrip())

    tracker_list.append(tracker)

print()