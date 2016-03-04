BOT_CREDENTIALS = {
        'username':'gthealth',
        'password':'password'
    }

TEST_DB_URI = 'mongodb://elc:yak@ds047652.mongolab.com:47652/redditdump'

SUBREDDITS = [
            {'name': 'McGill University', 'subreddit': 'mcgill'},
            {'name': 'Georgia Tech', 'subreddit': 'gatech'},
            {'name': 'UT Austin', 'subreddit': 'UTAustin'},
            {'name': 'Penn State University', 'subreddit': 'PennStateUniversity'},
            {'name': 'Purdue', 'subreddit': 'purdue'},
            {'name': 'UC Berkeley', 'subreddit': 'berkeley'},
            {'name': 'CalPoly Ubispo', 'subreddit': 'CalPoly'},
            {'name': 'UC Santa Barbara', 'subreddit': 'ucsantabarbara'},
            {'name': 'North Carolina State University', 'subreddit': 'ncsu'},
            {'name': 'York University', 'subreddit': 'yorku'},
            {'name': 'Texas A&M', 'subreddit': 'aggies'},
            {'name': 'Arizona State University', 'subreddit': 'asu'},
            {'name': 'University of Central Florida', 'subreddit': 'ucf'},
            {'name': 'University of British Columbia', 'subreddit': 'UBC'},
            {'name': 'University of Maryland', 'subreddit': 'UMD'},
            {'name': 'Rochester Institute of Technology', 'subreddit': 'rit'},
            {'name': 'Ohio State University', 'subreddit': 'OSU'},
            {'name': 'UC San Diego', 'subreddit': 'ucsd'},
            {'name': 'University of Missouri', 'subreddit': 'mizzou'},
            {'name': 'University of Georgia', 'subreddit': 'UGA'}
      ]

keywords = set(['depressed', 'depression', 'suicide', 'suicidal', 'kill',
                    'unhappy', 'counseling', 'counselor', 'psychiatrist',
                    'hate', 'death', 'die', 'heartbroken', 'lonely', 'hopeless',
                    'scared', 'suffer','failure', 'therapy', 'cry', 'alone', 'loser']);