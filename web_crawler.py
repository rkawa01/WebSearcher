import json
import pickle as pkl
import wikipediaapi as wpa
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

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

    def crawl(self,categorymembers,count,level=0, max_level=1):
        for c in categorymembers.values():
            if c.ns == wpa.Namespace.CATEGORY and level < max_level:
                self.crawl(c.categorymembers,count ,level=level + 1, max_level=max_level)
            elif c.ns == wpa.Namespace.MAIN:
                if len(self.sites) <= self.max_articles_per_category * count:
                    self.sites.add(c)
    def get_words(self,sites):
        for site in sites:
            self.dicts.append(dict())
            content = site.text
            word_list = content.split()
            stemmed = [self.wnl.lemmatize("".join(filter(lambda x: x.isalpha(), word))
                                     ).casefold() for word in word_list]
            for s in stemmed:
                if s not in self.stop_words:
                    self.dicts[-1][s] = self.dicts[-1].get(s, 0) + 1
                    self.words[s] = self.words.get(s, 0) + 1
    def get_wiki_data(self,i):
        categories = ["Physics","Music","Games","Mathematics", "Medicine", "Chemistry", "Biology", "Astronomy"]
        print("Downloading categories started")
        count = 0
        for c in categories:
            count += 1
            print(c)
            wiki_name = "Category:" + c
            cat = self.wiki.page(wiki_name)
            self.crawl(cat.categorymembers,count)
            if len(self.sites) > i:
                break
        self.site_list = list(self.sites)[:i]
        with open("content/titles.pkl", "wb") as write_file:
            pkl.dump([site.title for site in self.site_list], write_file)
        print("Downloading categories finished")
        self.get_words(self.site_list)
        print("Downloading sites finished")
        return self.words,self.dicts

if __name__ == "__main__":
    # nltk.download("punkt")
    # nltk.download('stopwords')
    # nltk.download("wordnet")
    # nltk.download("omw-1.4")
    Wiki = WikipediaPage(40)
    words_data,sites_data = Wiki.get_wiki_data(160)
    with open("content/words_data.pkl", "wb") as write_file:
        pkl.dump(words_data, write_file)
    with open("content/sites_data.pkl", "wb") as write_file:
        pkl.dump(sites_data, write_file)
    print(len(sites_data))

