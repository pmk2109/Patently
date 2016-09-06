import tweepy
import os
import re
import random
import csv
import sys
import time
from init_sql import PatentDatabase

csv.field_size_limit(sys.maxsize)



# (tuple of words) -> {dict: word -> number of times the word appears following the tuple}
# Example entry:
#    ('eyes', 'turned') => {'to': 2.0, 'from': 1.0}
# Used briefly while first constructing the normalized mapping
tempMapping = {}

# (tuple of words) -> {dict: word -> *normalized* number of times the word appears following the tuple}
# Example entry:
#    ('eyes', 'turned') => {'to': 0.66666666, 'from': 0.33333333}
mapping = {}

# Contains the set of words that can start sentences
starts = []


class TwitterAPI:
    def __init__(self):
        consumer_key = os.environ['TWITTER_CONSUMER_KEY']
        consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        access_token = os.environ['TWITTER_ACCESS_TOKEN']
        access_token_secret = os.environ['TWITTER_ACCESS_SECRET']
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

    def tweet(self, message):
        self.api.update_status(status=message)



# We want to be able to compare words independent of their capitalization.
def fix_caps(word):
    # Ex: "FOO" -> "foo"
    if word.isupper() and word != "I":
        word = word.lower()
        # Ex: "LaTeX" => "Latex"
    elif word [0].isupper():
        word = word.lower().capitalize()
        # Ex: "wOOt" -> "woot"
    else:
        word = word.lower()
    return word

def toHashKey(lst):
    return tuple(lst)

# Returns the contents of the file, split into a list of words and
# (some) punctuation.
def wordlist(filename):
    # f = open(filename, 'r')
    word_list = []
    with open(filename, 'rb') as csvfile:
        f = csv.reader(csvfile, delimiter = ',')
        for row in f:
            for word in re.findall(r"[\w']+|[.,!?;]", row[5]):
                word_list.append(fix_caps(word))

        # word_list = [fix_caps(word) for row in f for word in re.findall(r"[\w']+|[.,!?;]", row[5])]

    # wordlist = [fix_caps(w) for w in re.findall(r"[\w']+|[.,!?;]", f.read())]
    # f.close()
    return word_list

# tempMapping (and mapping) both match each word to a list of possible next
# words.
# Given history = ["the", "rain", "in"] and word = "Spain", we add "Spain" to
# the entries for ["the", "rain", "in"], ["rain", "in"], and ["in"].
def add_item_to_temp_mapping(history, word):
    while len(history) > 0:
        first = toHashKey(history)
        if first in tempMapping:
            if word in tempMapping[first]:
                tempMapping[first][word] += 1.0
            else:
                tempMapping[first][word] = 1.0
        else:
            tempMapping[first] = {}
            tempMapping[first][word] = 1.0
        history = history[1:]

# Building and normalizing the mapping.
def build_mapping(wordlist, markovLength):
    starts.append(wordlist [0])
    for i in range(1, len(wordlist) - 1):
        if i <= markovLength:
            history = wordlist[: i + 1]
        else:
            history = wordlist[i - markovLength + 1 : i + 1]
        follow = wordlist[i + 1]
        # if the last elt was a period, add the next word to the start list
        if history[-1] == "." and follow not in ".,!?;":
            starts.append(follow)
        add_item_to_temp_mapping(history, follow)
    # Normalize the values in tempMapping, put them into mapping
    for first, followset in tempMapping.iteritems():
        total = sum(followset.values())
        # Normalizing here:
        mapping[first] = dict([(k, v / total) for k, v in followset.iteritems()])

# Returns the next word in the sentence (chosen randomly),
# given the previous ones.
def next(prevList):
    sum = 0.0
    retval = ""
    index = random.random()
    # Shorten prevList until it's in mapping
    while toHashKey(prevList) not in mapping:
        prevList.pop(0)
    # Get a random word from the mapping, given prevList
    for k, v in mapping[toHashKey(prevList)].iteritems():
        sum += v
        if sum >= index and retval == "":
            retval = k
    return retval

def gen_sentence(markovLength):
    # Start with a random "starting word"
    curr = random.choice(starts)
    sent = curr.capitalize()
    prevList = [curr]
    # Keep adding words until we hit a period
    while (curr not in "."):
        curr = next(prevList)
        prevList.append(curr)
        # if the prevList has gotten too long, trim it
        if len(prevList) > markovLength:
            prevList.pop(0)
        if (curr not in ".,!?;"):
            sent += " " # Add spaces between words (but not punctuation)
        sent += curr
    return sent

def gen_tweet(markovLength):
    counter = 0
    tweet = []

    #Keep tweet short enough to tweet
    while counter <=139:
        sentence = gen_sentence(markovLength)
        #Stop sentence appending if it exceeds threshold
        if len(sentence) + counter > 139:
            break
        else:
            for word in sentence:
                for letter in word:
                    counter+=1
        tweet.append(sentence)
    return ' '.join(tweet)

def all_together_now(file_, tweet_len):
    filename = file_
    markovLength = int(tweet_len)
    build_mapping(wordlist(filename), markovLength)

    # length_satisfied = False
    # while length_satisfied == False:
    #     tweet = gen_tweet(markovLength)
    #     print type(tweet), len(tweet), tweet
    #     if len(tweet) < 12:
    #         pass
    #     else:
    #         length_satisfied = True

    return gen_tweet(markovLength)













if __name__ == "__main__":
    twitter = TwitterAPI()

    s = '''
    SELECT abstract FROM total_parsed_data
    '''

    pdb = PatentDatabase()
    df = pdb.query_sql(s)
    data_path = '../data/markov_data.csv'
    df.to_csv(data_path)
    
    _ = all_together_now(data_path, 3)

    # tweet = gen_tweet(10)
    minutes = 0
    while minutes < 10:
        length_satisfied = False
        while length_satisfied == False:
            tweet_string = gen_tweet(25)
            # print type(tweet), len(tweet), tweet
            if len(tweet_string) < 20:
                pass
            else:
                length_satisfied = True

        twitter.tweet(tweet_string)
        time.sleep(60)
        minutes+=1
