import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from umap import UMAP
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

class BERTopicAnalyzer:
    def __init__(self, data_file, text_column, output_folder, num_topics=10):
        self.data_file = data_file
        self.text_column = text_column
        self.output_folder = output_folder
        self.num_topics = num_topics
        self.data = None
        self.topic_model = None

    def preprocess(self, doc):
        stop = set(stopwords.words('english'))
        wordnet_lemmatizer = WordNetLemmatizer()
        cleaned_doc = " ".join(wordnet_lemmatizer.lemmatize(word) for word in doc.lower().split() if word not in stop)
        return cleaned_doc

    def fit_topics(self):
        sentence_model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
        self.data = pd.read_csv(self.data_file)
        docs = self.data[self.text_column].dropna().apply(self.preprocess).tolist()

        self.topic_model = BERTopic(embedding_model=sentence_model)
        self.topic_model.fit(docs)
        self.topic_model.save(f"{self.output_folder}_bert_topic_model", save_embedding_model=sentence_model)

    def visualize_topics(self):
        topic_model = BERTopic.load(f"{self.output_folder}_bert_topic_model")

        fig_barchart = topic_model.visualize_barchart(top_n_topics=self.num_topics)
        fig_barchart.write_html("topic_word_barchart.html")

        fig_tsnescatterplot = topic_model.visualize_topics(top_n_topics=self.num_topics)
        fig_tsnescatterplot.write_html("topic_word_tsnescatterplot.html")

        fig_hierarchy = topic_model.visualize_hierarchy(top_n_topics=self.num_topics, custom_labels=True)
        fig_hierarchy.write_html("topic_word_hierarchy.html")

        fig_heat = topic_model.visualize_heatmap(top_n_topics=self.num_topics)
        fig_heat.write_html("topic_word_heatmap.html")

    def visualize_documents(self):
        sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
        topic_model = BERTopic.load(f"{self.output_folder}_bert_topic_model")

        docs = self.data[self.text_column].dropna().apply(self.preprocess).tolist()

        embeddings = sentence_model.encode(docs, show_progress_bar=False)
        reduced_embeddings = UMAP(n_neighbors=10, n_components=2, metric='cosine', random_state=71).fit_transform(embeddings)

        topic_model.visualize_documents(docs, reduced_embeddings=reduced_embeddings, custom_labels=True).write_html("documents_visualization.html")
        topic_model.visualize_documents(docs, reduced_embeddings=reduced_embeddings, custom_labels=True, hide_annotations=True).write_html("documents_visualization (no_annotations).html")

    def create_topic_dataframes(self):

        # topic dict'ini al
        topic_dfs = self.topic_model.get_topic_info()

        return topic_dfs

    def save_topic_dataframes(self):

        topic_dfs = self.create_topic_dataframes()

        for topic, df in topic_dfs.items():
            df.to_csv(f"topic_{topic}_data.csv")

    def run_analysis(self):
        self.fit_topics()
        self.visualize_topics()
        self.visualize_documents()
        self.create_topic_dataframes()
        self.save_topic_dataframes()

# if __name__ == "__main__":
#     data_file = "Bert_preprocessed_data.csv"
#     text_column_name = "Bert_preprocessed_text"
#     output_folder_path = "output"
#     num_topics = 10

#     analyzer = BERTopicAnalyzer(data_file, text_column_name, output_folder_path, num_topics)
#     analyzer.run_analysis()
#     topic_dataframes = analyzer.create_topic_dataframes()


#*********************************************************************************************************
import pandas as pd
from gensim.parsing.preprocessing import preprocess_string, remove_stopwords

class BertPreprocessor:
    def __init__(self, corpus):
        self.corpus = corpus
        self.custom_filters = [lambda x: x.lower(), remove_stopwords, lambda x: x.strip()]
        self.processed_corpus = []

    def preprocess(self):
        self.processed_corpus = [preprocess_string(doc, self.custom_filters) for doc in self.corpus]
        return self.processed_corpus

    def save_preprocessed_data(self, output_path):
        preprocessed_df = pd.DataFrame({'Bert_preprocessed_text': [' '.join(doc) for doc in self.processed_corpus]})
        preprocessed_df.to_csv(output_path, index=False)

# file_path = ('preprocessed.csv')
# df = pd.read_csv(file_path)
# df.dropna(inplace=True)
# corpus = df['en_abs'].tolist()

# # # Bert Preprocessing
# bert_preprocessor = BertPreprocessor(corpus)
# bert_preprocessed_data = bert_preprocessor.preprocess()  # Tüm corpus'u işle
# bert_preprocessor.save_preprocessed_data('Bert_preprocessed_data.csv')
