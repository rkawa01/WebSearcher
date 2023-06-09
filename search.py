import numpy as np
import pickle as pkl
import json
import sys
import spacy
from nltk.stem import WordNetLemmatizer
import warnings
warnings.filterwarnings("ignore")

def search(top,text):
    wnl = WordNetLemmatizer()
    with open("content/titles.pkl", "rb") as read_file:
        sites = pkl.load(read_file)
    with open("content/dict.pkl", "rb") as read_file:
        indexes = pkl.load(read_file)
    with open("content/matrix.pkl", "rb") as read_file:
        matrix = pkl.load(read_file)

    reverse_index = {indexes[i]:i for i in indexes}

    vector = np.zeros(len(indexes))

    for word in text.split():
        word_lemma = wnl.lemmatize("".join(filter(lambda x: x.isalpha(), word))).casefold()
        if word_lemma in reverse_index:
            index = reverse_index[word_lemma]
            vector[int(index)] += 1
    
    prob = np.abs((vector.T @ matrix.T)) / np.sqrt(np.sum(
            matrix ** 2, axis=1))
    prob = [(prob[i],i) for i in range(len(prob))]
    prob.sort(reverse=True)
    all = prob[:top]
    best = [(sites[i], f"{prob*100:.2f}",get_links(sites[i])) for prob,i in all]
    print(json.dumps({"result": best}))
def get_links(title):
    return "https://en.wikipedia.org/wiki/"+title.replace(" ", "_")

try:
    nlp = spacy.load("en_core_web_sm")
    query = " ".join([token.lemma_ for token in nlp(sys.argv[1])])

    top = int(sys.argv[2])
    search(top,query)
except Exception as e:
    sys.exit(json.dumps({"error": str(e)}))
