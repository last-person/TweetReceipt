#!/usr/bin/env python 

import json
import os
import requests
import sys

class Tweeters(object):
    """
    This script uses the twitter v2 api to look for quoted tweets mentioning the {userID} account specified.
    It will then pull the text of those quoted tweets, along with the original tweeters username, and a timestamp
    and print them to a thermal receipt printer, attached to a raspberry Pi.

    Bearer token for twitter account, and twitter id, come from environment variables "tweetreceipttoken" and "tweetreceiptuserid".

    For now, this is a one-and-done operation, so there's little point in exception handling.
    The API handling should eventually be made more robust, or at least made to not raise exceptions
    when an API call fails.
    """

    env_vars = [
        ("userId", "tweetreceiptuserid"),
        ("bearerToken", "tweetreceipttoken"),
    ]

    twitter_api_url = "https://api.twitter.com/2"

    def __init__(self):
        self.read_environment_variables()
        self.mentions_path = "/users/{}/mentions?expansions=referenced_tweets.id".format(self.userId)
        self.auth_header = {"Authorization": "Bearer {}".format(self.bearerToken)}


    def read_environment_variables(self):
        """
        Read the environment variables referenced in Tweeters.env_vars.
        Store their values in the attributes refenced in Tweeters.env_vars.
        Raise an exception if any of them are missing.
        """

        missing_env_vars = []
        for attr_name, var_name in self.env_vars:
            env_value = os.getenv(var_name)
            if env_value is None:
                missing_env_vars.append(var_name)
            else:
                setattr(self, attr_name, env_value)

        if missing_env_vars:
            raise Exception("Missing environment variables: " + ", ".join(missing_env_vars))


    def err(self, msg):
        sys.stderr.write(msg)
        sys.stderr.write("\n")


    def is_valid_response(api_response):
        if not api_response or 'data' not in api_response:
            return False
        return True


    def valid_responses(func):
        def return_valid_responses(*args, **kwargs):
            responses = func(*args, **kwargs)
            return filter(Tweeters.is_valid_response, responses)
        return return_valid_responses


    def api_get(self, path):
        if not path.startswith("/"):
            path = "/" + path
        url = self.twitter_api_url + path

        response = requests.get(url, headers=self.auth_header)

        if response.status_code > 299:
            self.err("Error {} getting API path {}: {}".format(response.status_code, path, response.text))
            return {}

        return response.json()


    def get_referenced_tweet(self, tweet):
        """Create api call for referenced tweets"""
 
        if "referenced_tweets" not in tweet:
            return {}

        return self.api_get("/tweets/{}?expansions=author_id&user.fields=name,username&tweet.fields=created_at".format(tweet["referenced_tweets"][0]["id"]))


    def get_mentions(self):
        """Get 10 most recent mentions for {userID}"""

        return self.api_get(self.mentions_path)


    @valid_responses
    def get_referenced_tweets(self, referencedTweets):
        """Get tweets references returned in get_mentions"""

        if not Tweeters.is_valid_response(referencedTweets):
            return {}

        return map(self.get_referenced_tweet, referencedTweets["data"])


def printTweetReference(refTweetResponse):
    #parse out author name and text of tweet to be printed
    origText=refTweetResponse["data"]["text"]
    origAuthorUName = refTweetResponse["includes"]["users"][0]["username"]
    origAuthorName=refTweetResponse["includes"]["users"][0]["name"]
    origTweetId= refTweetResponse["data"]["id"]
    origTweetDate=refTweetResponse["data"]["created_at"]
    print("@{}\n{}\n{}\n{}\n{}\n*********************************************************".format(origAuthorName,origAuthorUName,origTweetDate,origText,origTweetId))


def main():
    twtr = Tweeters()
    mentions = twtr.get_mentions()
    referenced_responses = twtr.get_referenced_tweets(mentions)
    for refTweetResponse in referenced_responses:
        printTweetReference(refTweetResponse)


if __name__ == "__main__":
    main()
  
