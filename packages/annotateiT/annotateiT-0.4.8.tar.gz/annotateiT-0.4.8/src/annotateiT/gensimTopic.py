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

class Analyzer:
    def __init__(self, data_file=None, text_column="text", output_folder="output", num_topics=10):
        self.data_file = data_file or "output/Preprocessed_text_GensimBert.csv"
        self.text_column = text_column or "text"
        self.output_folder = output_folder
        self.num_topics = num_topics
        self.texts = None
        self.dictionary = None
        self.corpus = None
        self.lda_model = None
        self.data = None

    def load_data(self):
        self.data = pd.read_csv(self.data_file)

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

    def run_analysis(self):
        self.preprocess_data()
        
        start_topics = int(input("Please enter the starting number of topics: "))
        end_topics = int(input("Please enter the ending number of topics: "))        
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

# analyzer = GensimTopic()
# analyzer.load_data()
# analyzer.run_analysis()
