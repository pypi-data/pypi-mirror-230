import re
import pandas as pd
import os
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
from umap import UMAP
from bertopic import BERTopic
import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt

class Analyzer:
    def __init__(self, data_file=None, text_column="text", output_folder="output", num_topics=10):
        self.data_file = data_file or "output/Preprocessed_text_GensimBert.csv"
        self.text_column = text_column or 'text'
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
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        self.data = pd.read_csv(self.data_file)
        docs = self.data[self.text_column].dropna().apply(self.preprocess).tolist()

        self.topic_model = BERTopic(embedding_model=sentence_model)
        self.topic_model.fit(docs)
        self.topic_model.save(os.path.join(self.output_folder, "bert_topic_model"), save_embedding_model=sentence_model)

    def visualize_topics(self):
        topic_model = BERTopic.load(os.path.join(self.output_folder, "bert_topic_model"))

        fig_barchart = topic_model.visualize_barchart()
        fig_barchart.write_html(os.path.join(self.output_folder, "topic_word_barchart.html"))

        fig_tsnescatterplot = topic_model.visualize_topics(top_n_topics=self.num_topics)
        fig_tsnescatterplot.write_html(os.path.join(self.output_folder, "topic_word_tsnescatterplot.html"))

        fig_hierarchy = topic_model.visualize_hierarchy(top_n_topics=self.num_topics, custom_labels=True)
        fig_hierarchy.write_html(os.path.join(self.output_folder, "topic_word_hierarchy.html"))

        fig_heat = topic_model.visualize_heatmap(top_n_topics=self.num_topics)
        fig_heat.write_html(os.path.join(self.output_folder, "topic_word_heatmap.html"))

    def visualize_documents(self):
        sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
        topic_model = BERTopic.load(os.path.join(self.output_folder, "bert_topic_model"))

        docs = self.data[self.text_column].dropna().apply(self.preprocess).tolist()

        embeddings = sentence_model.encode(docs, show_progress_bar=False)
        reduced_embeddings = UMAP(n_neighbors=10, n_components=2, metric='cosine', random_state=71).fit_transform(embeddings)

        topic_model.visualize_documents(docs, reduced_embeddings=reduced_embeddings, custom_labels=True).write_html(
            os.path.join(self.output_folder, "documents_visualization.html"))
        topic_model.visualize_documents(docs, reduced_embeddings=reduced_embeddings, custom_labels=True,
                                        hide_annotations=True).write_html(
            os.path.join(self.output_folder, "documents_visualization (no_annotations).html"))

    def duzenle_cumle(self, cumle):
        # Başındaki rakamları kaldırın
        cumle = re.sub(r'^\d+_', '', cumle)
        # Aralardaki alt çizgileri boşlukla değiştirin
        cumle = cumle.replace('_', ' ')
        return cumle

    def create_topic_df(self):
        docs = self.data[self.text_column].dropna().apply(self.preprocess).tolist()
        topics, probs = self.topic_model.fit_transform(docs)
        topic_info = self.topic_model.get_topic_info()

        # Temizleme ve düzenleme işlemleri
        topic_info['Name'] = topic_info['Name'].apply(self.duzenle_cumle)
        topic_info['Topic'] = topic_info['Topic'].astype(int)

        return topics, probs, topic_info

    def save_topic_df(self):
        topics, probs, topic_info = self.create_topic_df()
        topic_df = pd.DataFrame({'topics': topics, 'probs': probs})
        topic_df = pd.concat([self.data, topic_df], axis=1)

        topic_df = topic_df.sort_values(by='topics', ascending=True)
        topic_df = topic_df.drop_duplicates(subset=['topics'], keep='first')

        topic_df = topic_df.iloc[1:self.num_topics + 2]
        topic_info = topic_info.iloc[1:self.num_topics + 2]

        topic_df.to_csv(os.path.join(self.output_folder, "bert_topic_df.csv"), index=False)
        topic_info.to_csv(os.path.join(self.output_folder, "bert_topic_info.csv"), index=False)

    def save_wordcloud(self):
        data = self.topic_model.get_topic_info()["Representative_Docs"]
        sentences = [" ".join(sent) for sent in data]
        unwanted_words = ["ii", "iii", "mm", "aim", "p005", "study", "group", "different",
                          "difference", "result", "conclusion", "conclude", "method", 
                          "statistically", "parameter","data", "use", "using"]

        # NLTK'den İngilizce stopwords listesini alın
        stop_words = set(stopwords.words("english"))

        # Kelimeleri çıkarma işlemini gerçekleştirin
        cleaned_corpus = []

        for text in sentences:
            words = text.split()  # Metni kelimelere ayırın
            cleaned_text = [word for word in words if word.lower() not in stop_words and word.lower() not in unwanted_words]
            cleaned_corpus.append(" ".join(cleaned_text))

        # Birleştirilmiş metin dizisini kullanarak WordCloud oluşturun
        word_freq = WordCloud().process_text(" ".join(cleaned_corpus))
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(word_freq)

        # WordCloud'ı görselleştirin
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.savefig(os.path.join(self.output_folder, "wordcloud.png"))
        # plt.show()

    def run_analysis(self):
        self.fit_topics()
        self.visualize_topics()
        self.visualize_documents()
        self.save_wordcloud()
        self.create_topic_df()
        self.save_topic_df()
    
# input olarak default olarak "output/Bert_preprocessed_data.csv" alır.
# output olarak default olarak "output" klasörüne çıktılarını verir.
# # Ana kod bloğu
# analyzer = BERTopicAnalyzer()
# analyzer.run_analysis()
