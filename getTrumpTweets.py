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
# List of parameters to adjust how the program scrapes and
# processes the markov chain
TWITTERUSERNAME = 'realDonaldTrump'
NUMTWEETSSCRAPED = 500
LENGTHOFCHAIN = 100
STARTINGWORD = 'I'


def getDate():
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y at %H.%M.%S")
    return (dt_string) 

def scrapeTweetsIntoFile(twitHandle, tweet_count):
    '''
    Creates a file to store the text data gathered from twitter's api.

    :param str twitHandle: The username of the twitteraccount
    :param int tweet_count: The amount of tweets to look through
    :return none:
    '''

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
        # Writing the text stored inside the tweet object
        if (not tweet.retweeted) and ('RT @' not in tweet.text):
            status = api.get_status(tweet.id, tweet_mode="extended")
            try:
                trumpTweets.write(status.full_text + "\n" + SEPERATOR + "\n")
            except:
                print("Something went wrong when writing to the file")
                trumpTweets.close()
                raise
    trumpTweets.close()

def buildWordDict(text):
    '''
    Takes the raw text from the tweet and makes a markov chain
    out of the words extracted

    :param str text: text that contains all the tweets scraped
    :return dict wordDict: dictionary of 2-grams from words in tweets
    '''

    text = text.replace('\n', ' '); 
    text = text.replace('&amp', '&')
    punctuationDel = ['"', '“', '”']
    for symbol in punctuationDel:
        text = text.replace(symbol, ''); # Words with quotes are not treated as unique
 
    text = re.sub('((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*',
        '', text) # URL's are not considered valuable text and are deleted

    olist = [run for run, leadchar in re.findall(r'(([!.?])\2+)', text)] # Multiple continous puncation are treated as one mark
    rlist = []
    for s in olist:
        rlist.append(s[0])

    for x, y in zip(olist, rlist):
        text = text.replace(x,y)

    text = re.sub('[?!.] ', ' ' + SEPERATOR + ' ', text) # Words cannot point to another link if they are at the end of sentences

    # Make sure punctuation marks are treated as their own "words,"
    # so that they will be included in the Markov chain
    punctuation = ['.',';',':','?','!']
    for symbol in punctuation:
        text = text.replace(symbol, ' {} '.format(symbol));
    
    text = re.sub(r'(\D)(,)(\D)', r'\1 , \3', text) # Commas that used as numerical separators are not treated as punctuation

    words = text.split(' ') # Split words into lists

    # Filter out empty words
    words = [word.upper() for word in words if word != '']

    words = list(splitOnSep(words, SEPERATOR)) # Split words into separate lists on end of sentences and tweets

    countWordsInTweets(words)

    # This makes a 2-gram mapping of all of the words in tweets per senetence
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
    '''
    Creates an file that contains an ordered dictionary of occurences of words tweeted

    :param list words: contains lists of lists where each sublist is a sentence
    :return none:
    '''

    wordCountFile = open("wordCount/wordCount" + getDate() + ".txt", "x+")
    wordfreq = {}
    for sentence in words:
        for word in sentence:
            if (isSignificantWord(word)):
                if (word not in wordfreq):
                    wordfreq[word] = 0
                wordfreq[word] += 1

    # This code orders the dictionary based on the values of the keys
    wordfreq = {k: v for k, v in sorted(wordfreq.items(), key=lambda item: item[1], reverse = True)}
    for key, value in wordfreq.items():
        line = '{:<18}  {:<18}\n'.format(str(key), str(value))
        wordCountFile.write(line)
    wordCountFile.close()

def isSignificantWord(word):
    '''
    Determines whether the word should be included in the dicitonary

    :param str word: word to be compared to sets of exclusionary words
    :return boolean: False if word is insignificant, True is the word is relevant 
    '''

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
    '''
    Splits a list into sublists so markov chains can't be made inbetween
    sentences or tweets

    :param string seq: List of words after some processing
    :param string sep: String that determines where the sublists start and end
    :yield list chunk: the batch of words to be returned
    '''

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
f.close()

length = LENGTHOFCHAIN
chain = [STARTINGWORD] # This is the first word of the Markov Chain
for i in range(0, length):
    try:
        newWord = retrieveRandomWord(wordDict[chain[-1]]) 
    except:
        newWord = choice(list(wordDict)) # If the word chosen was only used at the end of a sentence and is not a key, then choose a random word.
    chain.append(newWord) # Creating chain based on random choice of 2-gram in dictionary

markovChain = ' '.join(chain)
markovChainFile = open("markovChain/mchain" + getDate() + ".txt", "x+")
markovChainFile.write(markovChain)
markovChainFile.close()

