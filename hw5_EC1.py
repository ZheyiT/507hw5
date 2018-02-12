from requests_oauthlib import OAuth1
from requests_oauthlib import OAuth1Session
from datetime import datetime
import json
import sys
import requests
import secret_data # file that contains OAuth credentials
import nltk # uncomment line after you install nltk
import string


## SI 206 - HW
## Name: Zheyi Tian
## UMID: 36521510
## COMMENT WITH:
## Your section day/time: 006
## Any names of people you worked with on this assignment:

#usage should be python3 hw5_twitter.py <username> <num_tweets>
username1 = sys.argv[1]
username2 = sys.argv[2]
num_tweets = sys.argv[3]

consumer_key = secret_data.CONSUMER_KEY
consumer_secret = secret_data.CONSUMER_SECRET
access_token = secret_data.ACCESS_KEY
access_secret = secret_data.ACCESS_SECRET

#Code for OAuth starts
url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
auth = OAuth1(consumer_key, consumer_secret, access_token, access_secret)
requests.get(url, auth=auth)
#Code for OAuth ends

#Write your code below:
#Code for Part 3:Caching
#Finish parts 1 and 2 and then come back to this
CACHE_FNAME = 'twitter_cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)

MAX_STALENESS = 30  # 30 seconds

def is_fresh(cache_entry):
    now = datetime.now().timestamp()
    staleness = now - cache_entry[0]['cache_timestamp']
    return staleness < MAX_STALENESS 

def make_request_using_cache(baseurl, params):
    unique_ident = params_unique_combination(baseurl,params)

    if unique_ident in CACHE_DICTION:
        if is_fresh(CACHE_DICTION[unique_ident]): 
            print("Getting cached data...")
            return CACHE_DICTION[unique_ident]  
    else:
        pass 

    resp = requests.get(baseurl, params=params, auth=auth)   # requests.get(baseurl, params) ## Do not need oauth, requests.get is enough. ## Because OAuth was conducted above.
    CACHE_DICTION[unique_ident] = json.loads(resp.text)    # json.loads(resp.text)
    CACHE_DICTION[unique_ident][0]["cache_timestamp"] = datetime.now().timestamp() #Because the format of cache file changed, delete the old cache file first. # Make sure the "cache_timestamp" is added into a dicrtionary, not list.

    ## Return the json file for understanding.
    fw1 = open("tweet.json","w")
    json_string = json.dumps(CACHE_DICTION[unique_ident], indent=4) # Then, use json.dumps to get a str
    fw1.write(json_string)
    fw1.close()

    ## Get json file for CACHE
    dumped_json_cache = json.dumps(CACHE_DICTION)
    fw = open(CACHE_FNAME,"w")
    fw.write(dumped_json_cache)
    fw.close() # Update the CACHE_FNAME
    return CACHE_DICTION[unique_ident]

#Code for Part 1:Get Tweets
baseurl = 'https://api.twitter.com/1.1/statuses/user_timeline.json'

A = {"username":username1}
B = {"username":username2}
common = {}

for i in [A,B]:
    i["param"] = {'screen_name':i["username"], 'count':num_tweets}
    i["r_dict"] = make_request_using_cache(baseurl, i["param"])

    i["tweet_list"] = []
    for j in i["r_dict"]:
        i["tweet_list"].append(j['text'])

    i["word_list"] = []
    for j in i["tweet_list"]:
        sentence = j
        i["tokens"] = nltk.word_tokenize(sentence)
        i["word_list"] += i["tokens"]

    i["new_word_list"] = []
    ignore_words = ['http', 'https', 'RT']
    for j in i["word_list"]:
        if j[0] in string.ascii_letters:
            if j not in ignore_words:
                i["new_word_list"].append(j)

    i["word_dict"] = {}
    for j in i["new_word_list"]:
        if j not in i["word_dict"]:
            i["word_dict"][j] = 0
        i["word_dict"][j] +=1

    


    #i["sort_word"] = sorted(word_dict, key = lambda x: word_dict[x], reverse = True)

A["unique_dict"] = {}
B["unique_dict"] = {}
common["unique_dict"] = {}
for k in A["word_dict"]:
    if k not in B["word_dict"]:
        A["unique_dict"][k] = A["word_dict"][k]
    else:
        common["unique_dict"][k] = A["word_dict"][k]

for k in B["word_dict"]:
    if k not in common["unique_dict"]:
        B["unique_dict"][k] = B["word_dict"][k]
    else:
        common["unique_dict"][k] += B["word_dict"][k]

for i in [A,B,common]:
    i["sort_word"] = sorted(i["unique_dict"], key = lambda x: i["unique_dict"][x], reverse = True)

    i["freq_words"] = ""
    for k in range(5):
        i["freq_words"] += "{}({}) ".format(i["sort_word"][k], i["unique_dict"][i["sort_word"][k]])
    
print("USER: {}\nTWEETS ANALYZED: {}\n5 MOST FREQUENT UNIQUE WORDS: {}".format(username1, num_tweets, A["freq_words"])) 
print("USER: {}\nTWEETS ANALYZED: {}\n5 MOST FREQUENT UNIQUE WORDS: {}".format(username2, num_tweets, B["freq_words"]))   
print("\n5 MOST FREQUENT UNIQUE WORDS SHARED BY THE TWO: {}".format(common["freq_words"]))


if __name__ == "__main__":
    if not consumer_key or not consumer_secret:
        print("You need to fill in client_key and client_secret in the secret_data.py file.")
        exit()
    if not access_token or not access_secret:
        print("You need to fill in this API's specific OAuth URLs in this file.")
        exit()
