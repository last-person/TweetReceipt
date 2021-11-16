#!/usr/bin/env python 
"""
This script uses the twitter v2 api to look for quoted tweets mentioning the {userID} account specified.
It will then pull the text of those quoted tweets, along with the original tweeters username, and a timestamp
and print them to a thermal receipt printer, attached to a raspberry Pi.

Bearer token for twitter account, and twitter id, come from environment variables "tweetreceipttoken" and "tweetreceiptuserid".
"""

import json
import os
import requests

def create_mentions_url(userId):
    """Create url for mentions of the (userId) account"""

    return "https://api.twitter.com/2/users/{}/mentions?expansions=referenced_tweets.id".format(userId)


def create_ref_tweet_url(refTweetId):
    """Create url for referenced tweets"""

    return "https://api.twitter.com/2/tweets/{}?expansions=author_id&user.fields=name,username&tweet.fields=created_at".format(refTweetId)


def get_mentions(userId, bearerToken):
    """Get 10 most recent mentions for {userID}"""

    url = create_mentions_url(userId)
    response = requests.get(url, headers={"Authorization":"Bearer {}".format(bearerToken)})
    return response


def get_referenced_tweets(referencedTweets, bearerToken):
    """Get tweets references returned in get_mentions"""

    for tweet in referencedTweets['data']:
        if "referenced_tweets" in tweet:
            #get referenced tweet id
            refTweetId = tweet['referenced_tweets'][0]['id']

            #create url for referenced tweet object
            refUrl = create_ref_tweet_url(refTweetId)

            #send request to get object for the referenced tweet
            getRefTweet = requests.get(refUrl,headers={"Authorization":"Bearer {}".format(bearerToken)} )
            refTweetResponse = getRefTweet.json()
            if 'data' not in refTweetResponse:
                continue
            #print(refTweetResponse)
            #parse out author name and text of tweet to be printed
            origText=refTweetResponse['data']['text']
            origAuthorUName = refTweetResponse['includes']['users'][0]['username']
            origAuthorName=refTweetResponse['includes']['users'][0]['name']
            origTweetId= refTweetResponse['data']['id']
            origTweetDate=refTweetResponse['data']['created_at']
            print("@{}\n{}\n{}\n{}\n{}\n*********************************************************".format(origAuthorName,origAuthorUName,origTweetDate,origText,origTweetId))     
        else:  
            pass


def main():
    bearerToken = os.getenv("tweetreceipttoken")
    userId = os.getenv('tweetreceiptuserid')

    mentionsResponse = get_mentions(userId, bearerToken)
    jmentionsResponse = mentionsResponse.json()
    get_referenced_tweets(jmentionsResponse, bearerToken)

   

if __name__ == "__main__":
    main()
  
