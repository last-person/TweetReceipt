#!/usr/bin/env python 
import requests
import json
import os

# This script uses the twitter v2 api to look for quoted tweets mentioning the {userID} account specified.
# It will then pull the text of those quoted tweets, along with the original tweeters username, and a timestamp
# and print them to a thermal receipt printer, attached to a raspberry Pi.

#Get bearer token for twitter account, and twitter id, from environment variables
bearerToken = os.getenv("tweetreceipttoken")
userId=os.getenv('tweetreceiptuserid')

#Create url for mentions of the {userId} account
def create_mentions_url():
    return "https://api.twitter.com/2/users/{}/mentions?expansions=referenced_tweets.id".format(userId)

#Create url for referenced tweets
def create_ref_tweet_url(refTweetId):
    return "https://api.twitter.com/2/tweets/{}?expansions=author_id&user.fields=name,username&tweet.fields=created_at".format(refTweetId)

#Get 10 most recent mentions for {userID}
def get_mentions():
    url = create_mentions_url()
    response = requests.get(url, headers={"Authorization":"Bearer {}".format(bearerToken)})
    return response


#Get tweets references returned in get_mentions
def get_referenced_tweets(referencedTweets):
    for tweet in referencedTweets['data']:
        if "referenced_tweets" in tweet:
            #get referenced tweet id
            refTweetId = tweet['referenced_tweets'][0]['id']

            #create url for referenced tweet object
            refUrl = create_ref_tweet_url(refTweetId)

            #send request to get object for the referenced tweet
            getRefTweet = requests.get(refUrl,headers={"Authorization":"Bearer {}".format(bearerToken)} )
            refTweetResponse = getRefTweet.json()
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
    mentionsResponse = get_mentions()
    jmentionsResponse = mentionsResponse.json()
    get_referenced_tweets(jmentionsResponse)

   

if __name__ == "__main__":
    main()
  
