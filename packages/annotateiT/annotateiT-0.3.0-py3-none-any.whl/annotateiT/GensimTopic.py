import pandas as pd
from gensim.models import LdaModel
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel
import pyLDAvis
import pyLDAvis.gensim_models as gensimvis
import matplotlib.pyplot as plt
import os

class GensimTopic:
    def __init__(self, data, text_column, output_folder):
        self.data = data
        self.text_column = text_column
        self.output_folder = output_folder

        self.texts = None
        self.dictionary = None
        self.corpus = None
        self.lda_model = None

    def preprocess_data(self):
        self.texts = [text.split() for text in self.data[self.text_column]]

    def build_lda_model(self, num_topics=5):
        self.dictionary = Dictionary(self.texts)
        self.corpus = [self.dictionary.doc2bow(text) for text in self.texts]
        self.lda_model = LdaModel(self.corpus, num_topics=num_topics, id2word=self.dictionary)

    def calculate_coherence(self):
        coherence_model = CoherenceModel(model=self.lda_model, texts=self.texts, dictionary=self.dictionary, coherence='c_v')
        return coherence_model.get_coherence()

    def visualize_coherence(self, coherence_values, topic_range):
        plt.figure(figsize=(10, 5))
        plt.plot(topic_range, coherence_values, marker='o')
        plt.xlabel("Number of Topics")
        plt.ylabel("Coherence Score")
        plt.title("Coherence Scores by Topic Number")
        coherence_plot_path = os.path.join(self.output_folder, "coherence_plot.png")
        plt.savefig(coherence_plot_path)
        plt.close()
        print(f"Coherence plot saved as {coherence_plot_path}")

    def find_optimal_topic_number(self, start, limit, step=1):
        coherence_values = []
        topic_range = range(start, limit, step)

        for num_topics in topic_range:
            self.build_lda_model(num_topics)
            coherence_score = self.calculate_coherence()
            coherence_values.append(coherence_score)

        self.visualize_coherence(coherence_values, topic_range)
        
        optimal_topic_index = coherence_values.index(max(coherence_values))
        optimal_topic_number = topic_range[optimal_topic_index]
        return optimal_topic_number

    def visualize_topics(self):
        vis_data = gensimvis.prepare(self.lda_model, self.corpus, self.dictionary)
        pyLDAvis.save_html(vis_data, os.path.join(self.output_folder, "lda_visualization.html"))

    def run_analysis(self, start_topics, end_topics, step=1):
        self.preprocess_data()
        
        coherence_values = []
        topic_range = range(start_topics, end_topics + 1)
        for num_topics in topic_range:
            self.build_lda_model(num_topics)
            coherence_score = self.calculate_coherence()
            coherence_values.append(coherence_score)
        self.visualize_coherence(coherence_values, topic_range)
        
        topic_number = int(input("Please enter the number of topics you want for the analysis: "))
        
        self.build_lda_model(topic_number)
        self.visualize_topics()

# if __name__ == "__main__":
#     data = pd.read_csv("preprocessed_veriler.csv")
#     text_column_name = "preprocessed_text"
#     output_folder_path = input ("output folder path:" )
#     start_topic_number = 3
#     end_topic_number = 10

#     analyzer = GensimTopic(data, text_column_name, output_folder_path)
#     analyzer.run_analysis(start_topic_number, end_topic_number)

#*********************************************************************************************************
# import pandas as pd
# from gensim.parsing.preprocessing import preprocess_string, remove_stopwords
# import yaml
# from transformers import BertTokenizer
# import re

# class GensimPreprocessor:
#     def __init__(self, corpus):
#         self.corpus = corpus
#         self.custom_filters = [lambda x: x.lower(), remove_stopwords, lambda x: x.strip()]
#         self.processed_corpus = []

#     def preprocess(self):
#         self.processed_corpus = [preprocess_string(doc, self.custom_filters) for doc in self.corpus]
#         return self.processed_corpus

#     def save_preprocessed_data(self, output_path):
#         preprocessed_df = pd.DataFrame({'preprocessed_text': [' '.join(doc) for doc in self.processed_corpus]})
#         preprocessed_df.to_csv(output_path, index=False)

#     def run(self, output_path):
#         self.preprocess()
#         self.save_preprocessed_data(output_path)

# # Verileri yükle
# file_path = input('data yolunu veriniz:')
# df = pd.read_csv(file_path)
# corpus = df['en_abs'].tolist()

# Gensim Preprocessing
# gensim_preprocessor = GensimPreprocessor(corpus)
# gensim_preprocessed_corpus = gensim_preprocessor.preprocess()
# gensim_preprocessor.save_preprocessed_data('Gensim_preprocessed_data.csv')

import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from gensim.parsing.preprocessing import preprocess_string, remove_stopwords

# Özellikle stopwords ve lemmatizer için NLTK kaynaklarını indirin.
nltk.download('stopwords')
nltk.download('wordnet')

class GensimPreprocessor:
    def __init__(self, file_path, output_path):
        self.file_path = file_path
        self.output_path = output_path
        self.custom_filters = [lambda x: x.lower(), remove_stopwords, lambda x: x.strip()]
        self.processed_corpus = []

    def load_data(self):
        df = pd.read_csv(self.file_path)
        self.corpus = df['en_abs'].tolist()

    def preprocess(self):
        self.processed_corpus = [self.custom_preprocess(doc) for doc in self.corpus]
        return self.processed_corpus

    def custom_preprocess(self, doc):
        doc = ' '.join(preprocess_string(doc, self.custom_filters))  # Gensim pre-processing
        words = word_tokenize(doc)  # Metni kelimelere ayır
        lemmatizer = WordNetLemmatizer()
        words = [lemmatizer.lemmatize(word) for word in words]  # Lemma uygula
        return ' '.join(words)

    def save_preprocessed_data(self):
        preprocessed_df = pd.DataFrame({'preprocessed_text': self.processed_corpus})
        preprocessed_df.to_csv(self.output_path, index=False)

    def run(self):
        self.load_data()
        self.preprocess()
        self.save_preprocessed_data()

# # Verilerinizi yükleme, işleme ve lemma uygulama
# file_path = 'veri_yolu.csv'
# output_path = 'Gensim_preprocessed_data.csv'

# preprocessor = GensimPreprocessor(file_path, output_path)
# preprocessor.run()
