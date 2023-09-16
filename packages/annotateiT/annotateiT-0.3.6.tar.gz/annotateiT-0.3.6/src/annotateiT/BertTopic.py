import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from umap import UMAP
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

class BERTopicAnalyzer:
    def __init__(self, data_file, text_column, output_folder):
        self.data_file = data_file
        self.text_column = text_column
        self.output_folder = output_folder

    def preprocess(self, doc):
        stop = set(stopwords.words('english'))
        wordnet_lemmatizer = WordNetLemmatizer()
        cleaned_doc = " ".join(wordnet_lemmatizer.lemmatize(word) for word in doc.lower().split() if word not in stop)
        return cleaned_doc

    def fit_topics(self):
        sentence_model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
        data = pd.read_csv(self.data_file)
        docs = data[self.text_column].dropna().apply(self.preprocess).tolist()

        topic_model = BERTopic(embedding_model=sentence_model)
        topic_model.fit(docs)
        topic_model.save(f"{self.output_folder}_bert_topic_model", save_embedding_model=sentence_model)

    def visualize_topics(self):
        topic_model = BERTopic.load(f"{self.output_folder}_bert_topic_model")

        fig_barchart = topic_model.visualize_barchart(top_n_topics=10)
        fig_barchart.write_html("topic_word_barchart.html")

        fig_tsnescatterplot = topic_model.visualize_topics(top_n_topics=10)
        fig_tsnescatterplot.write_html("topic_word_tsnescatterplot.html")

        fig_hierarchy = topic_model.visualize_hierarchy(top_n_topics=10, custom_labels=True)
        fig_hierarchy.write_html("topic_word_hierarchy.html")

        fig_heat = topic_model.visualize_heatmap(top_n_topics=10)
        fig_heat.write_html("topic_word_heatmap.html")

    def visualize_documents(self):
        sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
        topic_model = BERTopic.load(f"{self.output_folder}_bert_topic_model")

        data = pd.read_csv(self.data_file)
        docs = data[self.text_column].dropna().apply(self.preprocess).tolist()

        embeddings = sentence_model.encode(docs, show_progress_bar=False)
        reduced_embeddings = UMAP(n_neighbors=10, n_components=2, metric='cosine', random_state=71).fit_transform(embeddings)

        topic_model.visualize_documents(docs, reduced_embeddings=reduced_embeddings, custom_labels=True).write_html("documents_visualization.html")
        topic_model.visualize_documents(docs, reduced_embeddings=reduced_embeddings, custom_labels=True, hide_annotations=True).write_html("documents_visualization (no_annotations).html")

    def run_analysis(self):
        self.fit_topics()
        self.visualize_topics()
        self.visualize_documents()

# if __name__ == "__main__":
#     data_file = "Bert_preprocessed_data.csv"
#     text_column_name = "Bert_preprocessed_data"
#     output_folder_path = "output"

#     analyzer = BERTopicAnalyzer(data_file, text_column_name, output_folder_path)
#     analyzer.run_analysis()
