import tweepy
import io
import re
import string
from random import randint, choice
from datetime import datetime
from config import *

# Creating the authentication object
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# Setting your access token and secret
auth.set_access_token(access_token, access_token_secret)
# Creating the API object while passing in auth information
api = tweepy.API(auth) 

SEPERATOR = '^~SEPERATOR~^'
TWITTERUSERNAME = 'realDonaldTrump'
NUMTWEETSSCRAPED = 500
LENGTHOFCHAIN = 100
STARTINGWORD = 'I'

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
                trumpTweets.write(status.full_text + "\n" + SEPERATOR + "\n")
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

    text = re.sub('[?!.] ', ' ' + SEPERATOR + ' ', text)

    # Make sure punctuation marks are treated as their own "words,"
    # so that they will be included in the Markov chain
    punctuation = ['.',';',':','?','!']
    for symbol in punctuation:
        text = text.replace(symbol, ' {} '.format(symbol));
    text = re.sub(r'(\D)(,)(\D)', r'\1 , \3', text)

    words = text.split(' ')
    # Filter out empty words
    words = [word.upper() for word in words if word != '']

    words = list(splitOnSep(words, SEPERATOR))

    print("txt file postprocessing:\n")
    print(words)
    print("="*20)

    countWordsInTweets(words)

    wordDict = {}
    for sentence in words:
        for i in range(1, len(sentence)):
            if sentence[i-1] not in wordDict:
                    # Create a new dictionary for this word
                wordDict[sentence[i-1]] = {}
            if sentence[i] not in wordDict[sentence[i-1]]:
                wordDict[sentence[i-1]][sentence[i]] = 0
            wordDict[sentence[i-1]][sentence[i]] += 1
    
    return wordDict

def countWordsInTweets(words):
    wordCountFile = open("wordCount/wordCount" + getDate() + ".txt", "x+")
    wordfreq = {}
    for sentence in words:
        for word in sentence:
            if (isSignificantWord(word)):
                if (word not in wordfreq):
                    wordfreq[word] = 0
                wordfreq[word] += 1
    wordfreq = {k: v for k, v in sorted(wordfreq.items(), key=lambda item: item[1], reverse = True)}
    for key, value in wordfreq.items():
        line = '{:<18}  {:<18}\n'.format(str(key), str(value))
        wordCountFile.write(line)
    wordCountFile.close()

def isSignificantWord(word):
    commonWords = ['THE', 'BE', 'AND', 'OF', 'A', 'IN', 'TO', 'HAVE', 'IT', 'I', 'THAT', 'FOR', 'YOU', 'HE', 'WITH', 'ON', 'DO', 'SAY', 'THIS', 'THEY', 'IS', 'AN', 'AT', 'BUT', 'WE', 'HIS', 'FROM', 'THAT', 'NOT', 'BY', 'SHE', 'OR', 'AS', 'WHAT', 'GO', 'THEIR', 'CAN', 'WHO', 'GET', 'IF', 'WOULD', 'HER', 'ALL', 'MY', 'MAKE', 'ABOUT', 'KNOW', 'WILL', 'AS', 'UP', 'ONE', 'HAS', 'BEEN', 'THERE', 'YEAR', 'SO', 'THINK', 'WHEN', 'WHICH', 'THEM', 'ME', 'OUT', 'INTO', 'JUST', 'SEE', 'HIM', 'YOUR', 'COME', 'COULD', 'NOW', 'THAN', 'LIKE', 'OTHER', 'HOW', 'THEN', 'ITS', 'OUR', 'TWO', 'MORE', 'THESE', 'WANT', 'WAY', 'LOOK', 'FIRST', 'ALSO', 'NEW', 'BECAUSE', 'DAY', 'MORE', 'USE', 'NO', 'MAN', 'FIND', 'HERE', 'THING', 'GIVE', 'ARE', 'WAS', 'GOT']
    if (word not in commonWords and
        word not in string.punctuation and
        word not in string.whitespace):
        return True
    return False

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

def splitOnSep(seq, sep):
    chunk = []
    for val in seq:
        if val == sep:
            yield chunk
            chunk = []
        else:
            chunk.append(val)
    yield chunk

scrapeTweetsIntoFile(TWITTERUSERNAME, NUMTWEETSSCRAPED)
f = io.open(fileName, mode="r", encoding="utf-8")
wordDict = buildWordDict(f.read())
print(wordDict)
print("="*20)

length = LENGTHOFCHAIN
chain = [STARTINGWORD]
for i in range(0, length):
    try:
        newWord = retrieveRandomWord(wordDict[chain[-1]])
    except:
        newWord = choice(list(wordDict))
        print('***A RANDOM WORD WAS PICKED DUE TO REACHING THE END OF A CHAIN***')
    print("newWord: " + newWord)
    chain.append(newWord)

markovChain = ' '.join(chain)
markovChainFile = open("markovChain/mchain" + getDate() + ".txt", "x+")
markovChainFile.write(markovChain)
markovChainFile.close()

