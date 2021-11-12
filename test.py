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

url="https://api.twitter.com/2/users/{}/mentions?&tweet.fields=referenced_tweets&user.fields=username".format(userId)
response = requests.get(url,headers={"Authorization":"Bearer {}".format(bearerToken)})

jsponse=response.json()
print(json.dumps(jsponse, indent=4))

    # for tweet in jsponse['data']:
    #     if "referenced_tweets" in tweet:
    #         #get referenced tweet id
    #         refTweetId = tweet['referenced_tweets'][0]['id']
    #         print(refTweetId)
    #         #create url for referenced tweet object
    #         refUrl = create_ref_tweet_url(refTweetId)
    #         #send request to get object for the referenced tweet
    #         getRefTweet = requests.get(refUrl,headers={"Authorization":"Bearer {}".format(bearerToken)} )
    #         refTweetResponse = getRefTweet.json()
    #         #get the twitter username for the author of the referenced tweet
    #         authorName = lookup_ref_auth()
    #         print(refTweetResponse['data'][0]['text'])
    #     else:  
    #         pass
