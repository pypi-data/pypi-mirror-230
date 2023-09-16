import pandas as pd
from gensim.models import LdaModel
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel
import pyLDAvis
import pyLDAvis.gensim_models as gensimvis
import matplotlib.pyplot as plt
import os

from gensim.parsing.preprocessing import remove_stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import string

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

class GensimPreprocessor:
    def __init__(self, corpus):
        self.corpus = corpus
        self.custom_filters = [lambda x: x.lower(), remove_stopwords, lambda x: x.strip()]
        self.processed_corpus = []

    def clean(self, doc):
        stop = set(stopwords.words('english'))
        exclude = set(string.punctuation)
        wordnet_lemmatizer = WordNetLemmatizer()
        stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
        punc_free = "".join(ch for ch in stop_free if ch not in exclude)
        normalized = " ".join(wordnet_lemmatizer.lemmatize(word) for word in punc_free.split())
        return normalized

    def preprocess(self):
        # Her bir doküman için temizleme işlemini uygula
        cleaned_corpus = []
        for doc in self.corpus:
            cleaned_doc = self.clean(doc)
            cleaned_corpus.append(cleaned_doc)
        self.processed_corpus = cleaned_corpus

    def save_preprocessed_data(self, output_path):
        preprocessed_df = pd.DataFrame({'preprocessed_text': [''.join(doc) for doc in self.processed_corpus]})
        preprocessed_df.to_csv(output_path, index=False)

    def run(self, output_path):
        self.preprocess()
        self.save_preprocessed_data(output_path)

# Verileri yükle
# file_path = ('/home/benjamin/Documents/GitHub/myPrivateProject/Healtcare_management/output/preprocessed.csv')
# df = pd.read_csv(file_path)
# corpus = df['en_abs'].dropna().tolist()

# # Gensim Preprocessing
# gensim_preprocessor = GensimPreprocessor(corpus)
# gensim_preprocessor.run('Gensim_preprocessed_data.csv')

