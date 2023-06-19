import pickle as pkl
import wikipediaapi as wpa
from urllib.error import HTTPError
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
from urllib.parse import quote
from time import perf_counter

class WikipediaPage():
    def __init__(self,max_articles_per_category=100):
        self.sites = set()
        self.wiki = wpa.Wikipedia('en')
        self.words = dict()
        self.dicts = []
        self.site_list = []
        self.wnl = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.max_articles_per_category = max_articles_per_category

    def crawl(self,categorymembers,max_articles,level=0, max_level=1):
        for c in categorymembers.values():
            if c.ns == wpa.Namespace.CATEGORY and level < max_level and len(self.sites) <= max_articles:
                self.crawl(c.categorymembers,max_articles ,level=level + 1, max_level=max_level)
            elif c.ns == wpa.Namespace.MAIN:
                if len(self.sites) <= max_articles:
                    self.sites.add(c)
    def get_words(self,sites):
        for site in sites:
            
            # link = site
            # if we sent there full links we can use the above line
            link = self.get_links(site)
            try:
                # start = perf_counter()
                webpage = str(urlopen(link).read())
                soup = bs(webpage, features="html.parser")
                content = self.filter_out(soup.get_text())
                self.dicts.append(dict())
                word_list = content.split()
                lemmatized = [self.wnl.lemmatize("".join(filter(lambda x: x.isalpha(), word))
                                        ).casefold() for word in word_list]
                # filter out words with length less than 3
                filtered = list(filter(lambda x: len(x) > 2, lemmatized))
                # filter out words that are in stop words
                filtered = list(filter(lambda x: x not in self.stop_words, filtered))
         
                for s in filtered:
                    dicts_element_count = self.dicts[-1].get(s, 0)
                    if dicts_element_count == 0:
                        self.words[s] = self.words.get(s, 0) + 1
                    self.dicts[-1][s] = dicts_element_count + 1
                        
                # end = perf_counter()
                # print(f"Time taken for {site.title} is {end-start}")
            except HTTPError:
                print("HTTPError")
                pass
            except Exception as e:
                print(f"Different Error: , {e}")
                pass

    def get_wiki_data(self,i):
        categories = ["Physics","Music","Games","Mathematics", "Medicine", "Chemistry", "Biology", "Astronomy", "History", "Geography", \
                      "Art", "Literature", "Philosophy", "Religion", "Mythology", "Politics", "Law", "Economics", "Psychology", "Sociology", \
                        "Education", "Technology", "Engineering", "Transport", "Food", "Drink", "Health", "Fashion", "Media", "Entertainment", \
                            "Sports", "Military", "Travel", "Business", "Finance", "Industry", "Agriculture", "Language", "Communication", \
                                "Architecture", "Infrastructure", "Environment", "Nature", "Disasters", "Energy", "Space", "Time", "Measurement", \
                                    "Numbers", "Money", "Units", "People", "Organizations", "Animals", "Plants", "Materials", "Computing", \
                                        "Internet", "Software", "Hardware", "Programming", "Data", "Fiction", "Chemicals"]
        print("Downloading categories started")
        count = 0
        for c in categories:
            count += 1
            print(c)
            wiki_name = "Category:" + c
            cat = self.wiki.page(wiki_name)
            self.crawl(cat.categorymembers,self.max_articles_per_category * count, max_level=1)
            if len(self.sites) > i:
                break
        self.site_list = list(self.sites)[:i]
        titles = [site.title for site in self.site_list]
        with open("content/titles.pkl", "wb") as write_file:
            pkl.dump(titles, write_file)
        
        print("Downloading categories finished")
        # alternatively we can send the links to the get_words function
        # self.get_words([site.fullurl for site in self.sites])
        self.get_words(titles)
        print("Downloading sites finished")
        return self.words,self.dicts
    def filter_out(self,text):
        # get rid of all special characters
        partly = re.sub('\\\\t|\\\\n|\\\\r|\\\\a|\\\\f|\\\\v|\\\\b', " ", text)
        # get rid of all special ascii characters
        partly = re.sub('\\\\x[0-9a-fA-F]{2}', " ", partly)
        partly = re.sub('[^A-Za-z]+', ' ', partly)
        return partly
    def get_links(self,title):
        return "https://en.wikipedia.org/wiki/"+quote(title.replace(" ", "_"))

if __name__ == "__main__":
    # nltk.download("punkt")
    # nltk.download('stopwords')
    # nltk.download("wordnet")
    # nltk.download("omw-1.4")
    Wiki = WikipediaPage(500)
    start = perf_counter()
    words_data,sites_data = Wiki.get_wiki_data(10000)
    end = perf_counter()
    print(f"Time taken for bag_of_words: {end-start}s")
    with open("content/words_data.pkl", "wb") as write_file:
        pkl.dump(words_data, write_file)
    with open("content/sites_data.pkl", "wb") as write_file:
        pkl.dump(sites_data, write_file)
    print(len(sites_data))

