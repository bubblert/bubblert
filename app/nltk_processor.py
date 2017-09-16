import nltk

nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')


def find_nouns(sentence):
    tokens = nltk.word_tokenize(sentence)
    tagged = nltk.pos_tag(tokens)
    nouns = [word for word, pos in tagged \
             if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS')]
    return nouns
