
"""
environment: visual studio 2019
reference: copy the function: oauth_login(), make_twitter_request() 
from Mining the Social Web, 3rd Edition:Chapter 9: Twitter Cookbook.
"""

import twitter
from textblob import TextBlob
import json
#import networkx as nx
#import matplotlib.pyplot as plt


def oauth_login():
    # XXX: Go to http://twitter.com/apps/new to create an app and get values
    # for these credentials that you'll need to provide in place of these
    # empty string values that are defined as placeholders.
    # See https://developer.twitter.com/en/docs/basics/authentication/overview/oauth
    # for more information on Twitter's OAuth implementation.
    
    CONSUMER_KEY = 'KmtQre6nXaxlhrov6b98zoo3W'
    CONSUMER_SECRET = 'YQBO45L8IkuOeHJSwWtchOlVjzJBDkQwOZoZMgLzg4TN0NV8Ft'
    OAUTH_TOKEN = '1366839526208004101-Hjs0iSxyWGzbrLoc3BFU6KDF2oX4DE'
    OAUTH_TOKEN_SECRET = '6rkguLQR4BtOkLyhYXNtxNvUVyZ5XqjbFeXR7QnJKNxp2'
    
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                               CONSUMER_KEY, CONSUMER_SECRET)
    
    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

import sys
import time
from urllib.error import URLError
from http.client import BadStatusLine
import json
import twitter

def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw): 
    
    # A nested helper function that handles common HTTPErrors. Return an updated
    # value for wait_period if the problem is a 500 level error. Block until the
    # rate limit is reset if it's a rate limiting issue (429 error). Returns None
    # for 401 and 404 errors, which requires special handling by the caller.
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):
    
        if wait_period > 3600: # Seconds
            print('Too many retries. Quitting.', file=sys.stderr)
            raise e
    
        # See https://developer.twitter.com/en/docs/basics/response-codes
        # for common codes
    
        if e.e.code == 401:
            print('Encountered 401 Error (Not Authorized)', file=sys.stderr)
            return None
        elif e.e.code == 404:
            print('Encountered 404 Error (Not Found)', file=sys.stderr)
            return None
        elif e.e.code == 429: 
            print('Encountered 429 Error (Rate Limit Exceeded)', file=sys.stderr)
            if sleep_when_rate_limited:
                print("Retrying in 15 minutes...ZzZ...", file=sys.stderr)
                sys.stderr.flush()
                time.sleep(60*15 + 5)
                print('...ZzZ...Awake now and trying again.', file=sys.stderr)
                return 2
            else:
                raise e # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504):
            print('Encountered {0} Error. Retrying in {1} seconds'                  .format(e.e.code, wait_period), file=sys.stderr)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e

    # End of nested helper function
    
    wait_period = 2 
    error_count = 0 

    while True:
        try:
            return twitter_api_func(*args, **kw)
        except twitter.api.TwitterHTTPError as e:
            error_count = 0 
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError as e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print("URLError encountered. Continuing.", file=sys.stderr)
            if error_count > max_errors:
                print("Too many consecutive errors...bailing out.", file=sys.stderr)
                raise
        except BadStatusLine as e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print("BadStatusLine encountered. Continuing.", file=sys.stderr)
            if error_count > max_errors:
                print("Too many consecutive errors...bailing out.", file=sys.stderr)
                raise

#---------------------------------------------------------
#-------------------start of main-------------------------
#---------------------------------------------------------
#if __name__ == "__main__":

# Returns an instance of twitter.Twitter
twitter_api = oauth_login()

# Reference the self.auth parameter
twitter_stream = twitter.TwitterStream(auth=twitter_api.auth)

posTweetID = []
negTweetID = []
tweetCounter = 0

# Query terms
q = 'Biden, biden, Democratic, democratic'
#q = 'Trump,trump, Republican, republican'

print('Filtering the public timeline for track={0}'.format(q), file=sys.stderr)
sys.stderr.flush()

stream = twitter_stream.statuses.filter(track=q)

f = open(q+".txt", 'w');
for tweet in stream:
    try:
        #print (json.dumps(tweet, indent=1, sort_keys=True))
        print (tweet['id'])
        print (tweet['text'])
        #Save to a database in a particular collection
        json.dump(tweet['id'], f, indent=1, sort_keys=True)
        f.write("\n")
        json.dump(tweet['text'], f, indent=1, sort_keys=True)       
        f.write("\n\n")

        #sentiment analysis using TextBlob
        blob = TextBlob(tweet['text'])
        sentimentScore = 0
        for sentence in blob.sentences:
            sentimentScore += sentence.sentiment.polarity
        print(sentimentScore)
        #adding id to positive or negative tweet list
        if sentimentScore > 0:
            posTweetID.append(tweet['id'])
        if sentimentScore < 0:
            negTweetID.append(tweet['id'])

        #print("POSITIVE TWEET ID")
        #print(posTweetID)

        #get a number of tweet in stream
        tweetCounter += 1
        if tweetCounter == 10:
            break

    except:
        pass

f.write('POSITIVE TWEET ID \n')
json.dump(posTweetID, f, indent=1, sort_keys=True)
f.write('\n\n')
f.write('NEGATIVE TWEET ID \n')
json.dump(negTweetID, f, indent=1, sort_keys=True)
f.write('\n\n')
f.close()
sys.stdout.flush()



