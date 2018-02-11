from requests_oauthlib import OAuth1
from requests_oauthlib import OAuth1Session
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
username = sys.argv[1]
num_tweets = sys.argv[2]

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
CACHE_FNAME = 'twitter_EC2_cache.json'
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
    resp = requests.get(baseurl, params=params, auth=auth)   
    CACHE_DICTION["cache_unique_ident"] = json.loads(resp.text)
    return CACHE_DICTION["cache_unique_ident"][0]["id_str"] + "_".join(res)
    ###EC2 CACHE by id and parameters.


def make_request_using_cache(baseurl, params):
    unique_ident = params_unique_combination(baseurl,params)

    if unique_ident in CACHE_DICTION: 
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]  
    else:
        pass 

    resp = requests.get(baseurl, params=params, auth=auth)   # requests.get(baseurl, params) ## Do not need oauth, requests.get is enough. ## Because OAuth was conducted above.
    CACHE_DICTION[unique_ident] = json.loads(resp.text)    # json.loads(resp.text)
    

    ## Return the json file for understanding.
    fw1 = open("tweet_EC2.json","w")
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
params = {'screen_name':username, 'count':num_tweets}

r_dict = make_request_using_cache(baseurl, params)

#Code for Part 2:Analyze Tweets
tweet_list = []
for i in r_dict:
	tweet_list.append(i['text'])

word_list = []
for i in tweet_list:
	sentence = i
	tokens = nltk.word_tokenize(sentence)
	word_list += tokens


new_word_list = []
ignore_words = ['http', 'https', 'RT']
for i in word_list:
	if i[0] in string.ascii_letters:
		if i not in ignore_words:
			new_word_list.append(i)

#abc = nltk.FreqDist(tokens).items()
#sorted(abc, key = lambda x: x...)

word_dict = {}
for i in new_word_list:
	if i not in word_dict:
		word_dict[i] = 0
	word_dict[i] +=1

sort_word = sorted(word_dict, key = lambda x: word_dict[x], reverse = True)

freq_words = ""
for i in range(5):
	freq_words += "{}({}) ".format(sort_word[i], word_dict[sort_word[i]])
print("USER: {}\nTWEETS ANALYZED: {}\n5 MOST FREQUENT WORDS: {}".format(username, num_tweets, freq_words))






if __name__ == "__main__":
    if not consumer_key or not consumer_secret:
        print("You need to fill in client_key and client_secret in the secret_data.py file.")
        exit()
    if not access_token or not access_secret:
        print("You need to fill in this API's specific OAuth URLs in this file.")
        exit()
