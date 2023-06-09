import numpy as np
import pickle as pkl
from web_crawler import WikipediaPage
from nltk.stem import WordNetLemmatizer


class Matrix():
    def __init__(self,words=None,sites_words=None,n=None):
        self.n = n
        self.words = words
        self.dicts = sites_words
        self.wnl = WordNetLemmatizer()

    def get_matrix(self):
        self.keys = list(self.words.keys())
        self.number_of_words = len(self.keys)
        self.matrix = np.zeros((self.n, self.number_of_words))
        self.index = {i: self.keys[i] for i in range(self.number_of_words)}
        self.reverse_index = {self.keys[i]: i for i in range(self.number_of_words)}
        #Iterate through sites
        for i in range(self.n):
            #Iterate through words
            for word in self.dicts[i]:
                self.matrix[i,self.reverse_index[word]] = self.dicts[i][word]
        print("frequency normalization started")
        #It's inverse document frequency
        m = np.log10(np.array([n / sum(1 for article in self.dicts if self.keys[i] in article) for i in range(self.number_of_words)]))
        self.matrix = self.matrix * m

        #Here starts normalization of vectors
        lengths = np.nan_to_num(1 / np.sqrt(np.sum(self.matrix ** 2, axis=1)), False, nan=0.0, posinf=0.0, neginf=0.0)
        self.matrix = (self.matrix.T * lengths).T
        print("frequency normalization finished")
        #lower approximation
        print("starting lower approximation")
        U, D, V = np.linalg.svd(self.matrix)
        r = len(D)
        print("calculating matrix")
        self.matrix = U[:, :r] @ np.diag(D) @ V[:r, :]
        print("matrix created")

    def save(self):
        with open("content/matrix.pkl", "wb") as write_file:
            pkl.dump(self.matrix, write_file)
        with open("content/dict.pkl", "wb") as write_file:
            pkl.dump(self.index, write_file)

if __name__ == "__main__":
    n = 160
    print(n)
    with open("content/words_data.pkl", "rb") as read_file:
        words_data = pkl.load(read_file)
    with open("content/sites_data.pkl", "rb") as read_file:
        sites_data = pkl.load(read_file)
    # Wiki = WikipediaPage()
    # words_data, sites_data = Wiki.get_wiki_data(n)
    matrix = Matrix(words_data,sites_data,n)
    matrix.get_matrix()
    matrix.save()

