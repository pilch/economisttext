import json
import urllib
import os
from os import listdir
from os.path import isfile, join
import nltk
from nltk.stem.porter import *
import textmining
import string
from langid.langid import LanguageIdentifier, model
import nltk
from nltk.tag import pos_tag
import random
from random import choice

identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)

def readFile(filename):
    doc = urllib.urlopen(filename).read()
    return(json.loads(doc))

def testLanguage(authorID):
    J = readFile("AllAuthors/%s.json" % authorID)
    A = []
    L = [this for this in J[authorID]]
    i = 0
    for each in range(0,len(L)):
        try:
            A.append(J[authorID][L[each]]['abstract'].encode('utf-8'))
        except:
            2*2
        i = i+1
    P = []
    [P.append(identifier.classify(x)) for x in A]
    return(P)


def getAbstract(authorID):
    J = readFile("AllAuthors/%s.json" % authorID)
    A = []
    L = [this for this in J[authorID]]
    i = 0
    for each in range(0,len(L)):
        try:
            A.append(J[authorID][L[each]]['abstract'].encode('utf-8'))
        except:
            2*2
        i = i+1
    p = testLanguage(authorID)
    p = [x[0] for x in p]
    ind = [i for i, x in enumerate(p) if x=='en']
    A = [A[i] for i in ind]
    A = [x.replace("no abstract is avail for thi item","") for x in A]
    return(' '.join(A))

def clean(abstract):
    abstract = re.sub(r'[^\x00-\x7F]+',' ',abstract)
    for c in string.punctuation:
        abstract = abstract.replace(c,' ')
    tagged = pos_tag(abstract.split())
    removeproper = [word for word,pos in tagged if pos != "NNP"]
    abstract = ' '.join(removeproper)
    a = abstract.lower()
    stemmer = nltk.PorterStemmer()
    abstractStem = ' '.join([stemmer.stem(x) for x in a.split(' ')])
    return (abstractStem)


def collectAbstracts():
    mypath = os.getcwd() + "/AllAuthors/"
    allfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    L = {}
    i = 0
    for each in allfiles:
        J = readFile("AllAuthors/%s" % each)
        authID = each.replace(".json","")
        auth = J[authID]['firstname'] + ' ' + J[authID]['lastname']
        abstract = getAbstract(authID)
        corpus = clean(abstract)
        L[auth] = corpus
        print(i)
        i = i+1
    return L

def limitWords(C,k):
    for each in C.keys():
        L = C[each].split()
        bagL = random.sample(L,min(len(L),k))
        bag = ' '.join(bagL)
        C[each] = bag
    return(C)

def createTermDocM(C,name):
    tdm = textmining.TermDocumentMatrix()
    [tdm.add_doc(C[x]) for x in C]
    tdm.write_csv('%s .csv' % name)
    names = [x.encode('utf-8') for x in C]
    f = open("authnames.txt",'w')
    f.writelines([name + '\n' for name in names])
    f.close()
    return (tdm)


def collectRawAbstracts():
    mypath = os.getcwd() + "/AllAuthors/"
    allfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    L = {}
    i = 0
    for each in allfiles:
        J = readFile("AllAuthors/%s" % each)
        authID = each.replace(".json","")
        auth = J[authID]['firstname'] + ' ' + J[authID]['lastname']
        abstract = getAbstract(authID)
        L[auth] = abstract
        print(i)
        i = i+1
    return L

def createListOfWords(L):
    A = []
    for each in L.keys():
        A.extend(L[each].split())
    return(A)

#Should be passed a list of words
def build_dict(words):
    """
    Build a dictionary from the words.
 
    (word1, word2) => [w1, w2, ...]  # key: tuple; value: list
    """
    d = {}
    for i, word in enumerate(words):
        try:
            first, second, third = words[i], words[i+1], words[i+2]
        except IndexError:
            break
        key = (first, second)
        if key not in d:
            d[key] = []
        #
        d[key].append(third)
 
    return d
 
EOS = ['.','?','!']

def generate_sentence(d):
	li = [key for key in d.keys()]
	key = choice(li)

	li = []
	first, second = key
	li.append(first)
	li.append(second)
	while True:
	    try:
	        third = choice(d[key])
	    except KeyError:
	        break
	    li.append(third)
	    if third[-1] in EOS:
	        break
	    # else
	    key = (second, third)
	    first, second = key

	return ' '.join(li)

#k is number of sentences:
def createAbstract(d,k):
    L = [generate_sentence(d) for i in range(0,k)]
    return(' '.join(L))
