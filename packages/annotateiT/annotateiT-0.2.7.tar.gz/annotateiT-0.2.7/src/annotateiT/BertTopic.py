# BURAYA BERTOPİC İLE İLGİLİ SCRİPT GELECEK-- GENSİMde OLDUĞU GİBİ
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