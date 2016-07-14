import re
import random

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
    f = open(filename, 'r')
    wordlist = [fix_caps(w) for w in re.findall(r"[\w']+|[.,!?;]", f.read())]
    f.close()
    return wordlist

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

def main(file_, tweet_len):
    filename = file_
    markovLength = int(tweet_len)
    build_mapping(wordlist(filename), markovLength)

    print gen_tweet(markovLength)

if __name__ == "__main__":
    main('/Users/marcversage/Desktop/Apps/Beer_Review_Bot/data/beer_reviews.txt', 3)
