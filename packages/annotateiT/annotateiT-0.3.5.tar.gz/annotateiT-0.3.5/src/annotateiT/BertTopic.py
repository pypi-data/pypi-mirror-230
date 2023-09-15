import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from umap import UMAP
import string
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

class BERTopicAnalyzer:
    def __init__(self, data, text_column, output_folder):
        self.data = data
        self.text_column = text_column
        self.output_folder = output_folder

        self.docs = None
        self.topic_model = None
        self.embeddings = None

    def preprocess(self):
        # Her bir doküman için temizleme işlemini uygula
        cleaned_corpus = []
        for doc in self.docs:
            cleaned_doc = self.clean(doc)
            cleaned_corpus.append(cleaned_doc)
        self.docs = cleaned_corpus

    def clean(self, doc):
        stop = set(stopwords.words('english'))
        exclude = set(string.punctuation)
        wordnet_lemmatizer = WordNetLemmatizer()
        stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
        punc_free = "".join(ch for ch in stop_free if ch not in exclude)
        normalized = " ".join(wordnet_lemmatizer.lemmatize(word) for word in punc_free.split())
        return normalized

    def fit_topics(self, num_topics=10):
        sentence_model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
        self.topic_model = BERTopic(embedding_model=sentence_model)
        self.topic_model.fit(self.docs)
        self.topic_model.save(self.output_folder + "_bert_topic_model", save_embedding_model=sentence_model)
        
    def get_topic_assignments(self):
        topics, probabilities = self.topic_model.transform(self.docs)
        return topics, probabilities
    
    def visualize_topics(self):
        topics, probabilities = self.get_topic_assignments()

        fig_barchart = self.topic_model.visualize_barchart(top_n_topics=10)
        fig_barchart.write_html("topic_word_barchart.html")

        fig_tsnescatterplot = self.topic_model.visualize_topics(top_n_topics=10)
        fig_tsnescatterplot.write_html("topic_word_tsnescatterplot.html")

        fig_hierarchy = self.topic_model.visualize_hierarchy(top_n_topics=10, custom_labels=True)
        fig_hierarchy.write_html("topic_word_hierarchy.html")

        fig_heat = self.topic_model.visualize_heatmap(top_n_topics=10)
        fig_heat.write_html("topic_word_heatmap.html")  

    def visualize_documents(self):
        sentence_model = SentenceTransformer("all-MiniLM-L6-v2")  # Use the appropriate model
        self.embeddings = sentence_model.encode(self.docs, show_progress_bar=False)
        reduced_embeddings = UMAP(n_neighbors=10, n_components=2, metric='cosine',random_state=71).fit_transform(self.embeddings)
        # umap_embeddings = umap_model.transform(self.embeddings)
        self.topic_model.visualize_documents(self.docs, reduced_embeddings=reduced_embeddings, custom_labels=True)

        fig_doc = self.topic_model.visualize_documents(self.docs, reduced_embeddings=reduced_embeddings, custom_labels=True)
        fig_doc.write_html("documents_visualization.html")        

        fig_doc = self.topic_model.visualize_documents(self.docs, reduced_embeddings=reduced_embeddings, custom_labels=True, hide_annotations=True)
        fig_doc.write_html("documents_visualization (no_annotations).html")           
     
    def run_analysis(self):
        self.docs = self.data[self.text_column].dropna().tolist()
        self.preprocess()
        self.fit_topics()
        self.visualize_topics()
        self.visualize_documents()

# if __name__ == "__main__":
#     data = pd.read_csv("Bert_preprocessed_data.csv")
#     text_column_name = "Bert_preprocessed_data"
#     output_folder_path = "output"

#     analyzer = BERTopicAnalyzer(data, text_column_name, output_folder_path)
#     analyzer.run_analysis()



#**********************************************************************************************
import pandas as pd
from gensim.parsing.preprocessing import preprocess_string, remove_stopwords
import yaml
from transformers import BertTokenizer
import re

class BertPreprocessor:
    def __init__(self, corpus):
        self.corpus = corpus
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.preprocessed_data = []

    def preprocess(self):
        def preprocess_text(text):
            text = re.sub(r'<.*?>', '', text)
            text = re.sub(r'[^\w\s]', ' ', text)
            text = re.sub(r'\d+', ' ', text)
            tokens = self.tokenizer.tokenize(text)
            return ' '.join(tokens)

        self.preprocessed_data = [preprocess_text(text) for text in self.corpus]
        return self.preprocessed_data

    def save_preprocessed_data(self, output_path):
        preprocessed_df = pd.DataFrame({'Bert_preprocessed_data': self.preprocessed_data})
        preprocessed_df.to_csv(output_path, index=False)

    def run(self, output_path):
        self.preprocess()
        self.save_preprocessed_data(output_path)

# # Bert Preprocessing
# bert_preprocessor = BertPreprocessor(corpus)
# bert_preprocessed_data = bert_preprocessor.preprocess()
# bert_preprocessor.save_preprocessed_data('Bert_preprocessed_data.csv')