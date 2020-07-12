import tweepy
import io
import re
from random import randint
from datetime import datetime
from config import *

# Creating the authentication object
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# Setting your access token and secret
auth.set_access_token(access_token, access_token_secret)
# Creating the API object while passing in auth information
api = tweepy.API(auth) 



def getDate():
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d-%m-%Y at %H.%M.%S")
    return (dt_string) 

def scrapeTweetsIntoFile(twitHandle, tweet_count):

    global fileName
    fileName = "rawtweets/trmpTwts" + getDate() + ".txt"

    try:
        trumpTweets = open(fileName, "x+")
    except:
        raise
    # Calling the user_timeline function with our parameters
    tweets = api.user_timeline(id=twitHandle, count=tweet_count)
    # foreach through all tweets pulled
    for tweet in tweets:
        # printing the text stored inside the tweet object
        if (not tweet.retweeted) and ('RT @' not in tweet.text):
            status = api.get_status(tweet.id, tweet_mode="extended")
            try:
                #print(status.full_text + "\n")
                trumpTweets.write(status.full_text + "\n")
            except:
                print("Something went wrong when writing to the file")
                trumpTweets.close()
                raise
    trumpTweets.close()

def buildWordDict(text):
    # Remove newlines and quotes
    text = text.replace('\n', ' ');
    text = text.replace('&amp', '&')
    punctuationDel = ['"', '“', '”']
    for symbol in punctuationDel:
        text = text.replace(symbol, '');
 
    text = re.sub('((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*',
        '', text)

    olist = [run for run, leadchar in re.findall(r'(([!.?])\2+)', text)]
    rlist = []
    for s in olist:
        rlist.append(s[0])

    for x, y in zip(olist, rlist):
        text = text.replace(x,y)


    # Make sure punctuation marks are treated as their own "words,"
    # so that they will be included in the Markov chain
    punctuation = [',','.',';',':','?','!']
    for symbol in punctuation:
        text = text.replace(symbol, ' {} '.format(symbol));

    words = text.split(' ')
    # Filter out empty words
    words = [word.lower() for word in words if word != '']

    print("txt file after stripping:\n" + text)
    print("="*20)

    wordDict = {}
    for i in range(1, len(words)):
        if words[i-1] not in wordDict:
                # Create a new dictionary for this word
            wordDict[words[i-1]] = {}
        if words[i] not in wordDict[words[i-1]]:
            wordDict[words[i-1]][words[i]] = 0
        wordDict[words[i-1]][words[i]] += 1
    return wordDict

def wordListSum(wordList):
    sum = 0
    for word, value in wordList.items():
        sum += value
    return sum

def retrieveRandomWord(wordList):
    randIndex = randint(1, wordListSum(wordList))
    for word, value in wordList.items():
        randIndex -= value
        if randIndex <= 0:
            return word

scrapeTweetsIntoFile("realDonaldTrump", 500)
f = io.open(fileName, mode="r", encoding="utf-8")
wordDict = buildWordDict(f.read())
print(wordDict)
print("="*20)

length = 100
chain = ['i']
for i in range(0, length):
    newWord = retrieveRandomWord(wordDict[chain[-1]])
    chain.append(newWord)

markovChain = ' '.join(chain)
markovChainFile = open("markovChain/mchain" + getDate() + ".txt", "x+")
markovChainFile.write(markovChain)
markovChainFile.close()

