import urllib
from bs4 import BeautifulSoup
import re
import pickle
import nltk
import json
from nltk.stem.porter import *
import string
import time

masterURL = "https://ideas.repec.org/top/top.person.all.html"
prefix = "https://ideas.repec.org"

#Pull all pages for ranked economists
def readAuthorRankings(url):
	doc = urllib.urlopen(url).read()
	soup = BeautifulSoup(doc)
	authors = soup.find('table',{'class':'shorttop'})
	body = str(authors)
	body2 = re.sub("<p>.*?</p>",'',body,0,re.DOTALL|re.IGNORECASE)
	L = re.findall("href=\"(.*?)\">",body2,re.DOTALL|re.IGNORECASE)
	A = [prefix + x for x in L]
	return(A)

#Read the page of an ecomomist and pull all links for articles
def readAuthorPapers(url):
	doc = urllib.urlopen(url).read()
	soup = BeautifulSoup(doc)
	articles = soup.find('div',{'id':'author-articles'})
	body = str(articles)
	body2 = re.sub("\"(otherversion|publishedas)\">.*?</div>",'',body,0,re.DOTALL | re.IGNORECASE)
	L = re.findall("class=\"down.*?href=\"(.*?)\">",body2,re.DOTALL | re.IGNORECASE)
	A = [prefix + x for x in L]
	return(A)

#Read the page of an economist and pull descriptive information including first name, last name, institution, etc.
def readAuthorBio(url):
    doc = urllib.urlopen(url).read()
    soup = BeautifulSoup(doc)
    affiliationSoup = soup.find('a',{'name':'subaffil'})
    affiliation = re.findall("<br>(.*?)<",str(affiliationSoup))
    detailsSoup = soup.find('div',{'id':'details-body'})
    firstName = re.findall('First Name:.*?<td>(.*?)<',str(detailsSoup))[0]
    lastName = re.findall('Last Name:.*?<td>(.*?)<',str(detailsSoup))[0]
    shortID = re.search("org/(.*?).html",url).group(1).replace("/","")
    return([firstName,lastName,shortID,url])

#Read info about a paper, including paper name, other authors, and abstract. Note this only pulls authors registered with REPEC
def readPaper(url):
    doc = urllib.urlopen(url).read()
    soup = BeautifulSoup(doc)
    try:
        titleSoup = soup.find('div',{'id':'title'})
        title = re.search('<h1>(.*?)<',str(titleSoup)).group(1)
    except AttributeError:
        return("NA")
    otherAuthSoup = soup.find('ul',{'id':'authorregistered'})
    otherAuth = re.findall('href=\"(.*?).html',str(otherAuthSoup))
    otherAuth2 = [x.replace("/","") for x in otherAuth]
    abstractSoup = soup.find('div',{'id':'abstract-body'})
    abstract = re.search("<p>(.*?)</p>",str(abstractSoup)).group(1)
    abstractClean = cleanText(abstract)
    stemmer = PorterStemmer()
    abstractStem = ' '.join([stemmer.stem(x) for x in abstractClean.split(' ')])
    return([title,otherAuth2,abstract,abstractStem,url])

#Remove all punctuation and convert the text to lower case
def cleanText(corpus):
    corpus = re.sub(r'[^\x00-\x7F]+',' ',corpus)
    for c in string.punctuation:
        corpus = corpus.replace(c,'')
    return (corpus.lower())

#Given an author url, write all that author's info to a json file
def writeAuthor(authorURL):
    D = {}
    Bio = readAuthorBio(authorURL)
    D[Bio[2]] = {'firstname':Bio[0],'lastname':Bio[1],'homepage':Bio[3]}
    paperList = readAuthorPapers(authorURL)
    for paperURL in paperList:
        print(paperURL)
        Paper = readPaper(paperURL)
        if Paper!="NA":
            D[Bio[2]][Paper[4]] = {"title":Paper[0],"authors":Paper[1],"abstract":Paper[2],"abstractStem":Paper[3]}
        else:
            print "Error"
        time.sleep(0.05)
    t = open("AllAuthors/%s.json" % Bio[2],"w")
    json.dump(D,t)
    t.close()

#Go through all the top n authors and pull their data
n = 100
def go():
    authList = readAuthorRankings(masterURL)
    allAuthors = authList[0:n]
    i = 1
    for authorURL in allAuthors:
        print(i)
        i = i+1
        writeAuthor(authorURL)


