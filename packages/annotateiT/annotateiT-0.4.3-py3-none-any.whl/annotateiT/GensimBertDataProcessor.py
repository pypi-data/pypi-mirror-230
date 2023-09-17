import pandas as pd
from gensim.parsing.preprocessing import remove_stopwords
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string

class GensimBertDataProcessor:
    def __init__(self, input_file=None, text_column=None, custom_filters=None, output_path=None):
        self.input_file = input_file or 'output/preprocessed.csv'
        self.text_column = text_column or 'text'
        self.custom_filters = custom_filters
        self.corpus = None
        self.custom_filters = [lambda x: x.lower(), remove_stopwords, lambda x: x.strip()]
        self.processed_corpus = []
        self.output_path = output_path or 'output/Preprocessed_text_GensimBert.csv'

    def clean(self, doc):
        stop = set(stopwords.words('english'))
        exclude = set(string.punctuation)
        wordnet_lemmatizer = WordNetLemmatizer()
        stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
        punc_free = "".join(ch for ch in stop_free if ch not in exclude)
        normalized = " ".join(wordnet_lemmatizer.lemmatize(word) for word in punc_free.split())
        return normalized

    def load_data(self):
        data = pd.read_csv(self.input_file)
        self.corpus = data[self.text_column].dropna().tolist()

    def preprocess(self):
        # Her bir doküman için temizleme işlemini uygula
        cleaned_corpus = []
        for doc in self.corpus:
            cleaned_doc = self.clean(doc)
            cleaned_corpus.append(cleaned_doc)
        self.processed_corpus = cleaned_corpus

    def save_preprocessed_data(self):
        preprocessed_df = pd.DataFrame({'text': [''.join(doc) for doc in self.processed_corpus]})
        preprocessed_df.to_csv(self.output_path, index=False)

    def run(self):
        self.load_data()
        self.preprocess()
        self.save_preprocessed_data()

# Veri yükleme ve işleme (varsayılan değerlerle)
# bert_preprocessor = GensBertDataPreprocessor()
# bert_preprocessor.run()
