
#*************************************************************************************
import pandas as pd
import re

class TextChunkExtractor:
    def __init__(self, data, mydict):
        self.df = pd.DataFrame(data)
        self.mydict = mydict

    @staticmethod
    def extract_info(text, chunk):
        positions = [(m.start(), m.end()) for m in re.finditer(re.escape(chunk), text)]
        return positions

    def process_text(self, text, unique_text_id):
        results = []
        for label, chunks in self.mydict.items():
            for chunk in chunks:
                extracted_positions = self.extract_info(text, chunk)
                results.extend([{
                    'id': unique_text_id,
                    'text': text,
                    'begin': begin,
                    'end': end,
                    'chunk': chunk,
                    'labels': label
                } for begin, end in extracted_positions if not any(
                    (result['begin'] <= begin < result['end'] or result['begin'] < end <= result['end'])
                    for result in results)])
        return results

    def extract_chunks(self):
        extracted_results = []
        for idx, text in enumerate(self.df['text'].unique(), start=1):
            unique_text_id = str(idx)
            extracted_results.extend(self.process_text(text, unique_text_id))
        df = pd.DataFrame(extracted_results)
        df[['id', 'begin', 'end']] = df[['id', 'begin', 'end']].astype(int)
        df.sort_values(['id', 'begin', 'end'], inplace=True)
        df.drop_duplicates(subset=['id', 'begin', 'end'], keep='first', inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df[['id', 'text', 'chunk', 'begin', 'end', 'labels']]
#*************************************************************************************

class OverlapRemover:

    def __init__(self, df):
        self.df = df

    def find_overlaps(self, group):
        # ... (your existing find_overlaps logic)
        sorted_df = group.sort_values(["id", 'begin', 'end'])  

        overlaps = []

        for i in range(len(sorted_df)-1):        
            curr = sorted_df.iloc[i]
            next = sorted_df.iloc[i+1]

            if curr['end'] >= next['begin']:
                overlaps.append((curr, next))

            elif curr['begin'] >= next['begin']:
                overlaps.append((curr, next))

            elif curr['end'] >= next['end']:
                overlaps.append((curr, next))

            elif curr['begin'] >= next['end']:
                overlaps.append((curr, next))
            
        return overlaps

    def remove_overlaps(self):
        # ... (your existing remove_overlaps logic)
        overlaps = self.df.groupby('id').apply(self.find_overlaps)

        for overlap_pairs in overlaps:

            for pair in overlap_pairs:

                len1 = len(pair[0]['chunk'])
                len2 = len(pair[1]['chunk'])
                
                if len1 < len2:
                    self.df.drop(pair[0].name, inplace=True)

                else:
                     self.df.drop(pair[1].name, inplace=True)
            
        for _, group in self.df.groupby('id'):
        
            sorted_group = group.sort_values(["id", 'begin', 'end'])
        
        for i in range(1, len(sorted_group)):
            
            curr = sorted_group.iloc[i]
            prev = sorted_group.iloc[i-1]
            
            if curr['begin'] <= prev['begin'] and \
            curr['end'] <= prev['end'] and \
            curr['end'] <= prev['begin'] and \
            curr['begin'] <= prev['end']:
                self.df.drop(curr.name, inplace=True)
        

    def get_df(self):
        self.df.dropna(inplace=True)
        self.df.sort_values(by=["id", 'begin', "end"], inplace=True)
        self.df.begin = self.df.begin.astype(int)
        self.df.end = self.df.end.astype(int)
        self.df.reset_index(drop=True, inplace=True)

        return self.df

 
#*************************************************************************************
class DataFrameToDictionary:# make a class to convert df.labels and df.chunk to dictionary

    def __init__(self, dataframe):
        self.dataframe = dataframe

    def convert_to_dict(self):
        combined_data = {}
        for key, value in zip(self.dataframe['labels'], self.dataframe['chunk']):
            if key in combined_data:
                if isinstance(combined_data[key], list):
                    combined_data[key].append(value)
                else:
                    combined_data[key] = [combined_data[key]] + [value]
            else:
                combined_data[key] = value
        return combined_data
#*************************************************************************************
from collections import defaultdict
from nltk import wordpunct_tokenize, sent_tokenize

class TextAnnotator:
    def __init__(self):
        self.mydict = defaultdict(list)
        
    def process_dataframe(self, df):
        for i in df.text.unique():
            begin = df[df.text == i].begin.values
            end = df[df.text == i].end.values
            chunk = df[df.text == i].chunk.values
            labels = df[df.text == i].labels.values

            self.mydict[i] = list(zip(begin, end, chunk, labels))
    
    def process_annotations(self):
        text2 = ""

        for i in self.mydict:
            for j in self.mydict[i][::-1]:
                i = i[:j[1]+1] + " ENDNER " + i[j[1]+1:]
                i = i[:j[0]] + " BEGINER_" + j[3] + " " + i[j[0]:]
            text2 += i + "\n"
        
        return text2
    
    def conll(self, text):
        def start_entity(word):
            nonlocal label
            label = word.split("_")[1]

        def end_entity():
            nonlocal label
            nonlocal cl
            nonlocal conll_text

            for idx, ct in enumerate(cl):
                x = 'B' if idx == 0 else 'I'
                conll_text += f"{ct} NN NN {x}-{label}\n"
            label = 'O'
            cl.clear()

        def add_word(word):
            nonlocal label
            nonlocal cl
            nonlocal conll_text

            if word.startswith("BEGINER_"):
                start_entity(word)

            elif label != 'O' and word != 'ENDNER':
                cl.append(word)

            elif word == f'ENDNER':
                end_entity()

            else:
                conll_text += f"{word} NN NN {label}\n"

        conll_text = ""
        cl = []
        label = 'O'

        sentences = sent_tokenize(text)
        for sentence in sentences:
            words = wordpunct_tokenize(sentence)
            for word in words:
                add_word(word)

            conll_text += "\n"

        return conll_text
    
    def process_and_create_conll(self, df, output_file):
        self.process_dataframe(df)
        processed_text = self.process_annotations()
        conll_text = self.conll(processed_text)
        
        header = "-DOCSTART- -X- -X- O\n\n"
        with open(output_file, "+w", encoding="utf8") as f:
            f.write(header)
            f.write(conll_text)

# annotator = TextAnnotator()
# annotator.process_and_create_conll(df, "MyCoNLL.conll")
#*************************************************************************************
class ConllGenerator:
    """
    Bu class .json file'ını okuyup, CoNLL formatında test ve train olarak split eder.
    """
    def __init__(self, df, myLabels):
        self.df = df
        self.myLabels = myLabels
        self.file = ["-DOCSTART- -X- -X- O\n"]
        self.temp = []
        self.labels = []

    def has_start_label(self, label):
        return any(label.startswith("B-" + x) or label.startswith("I-" + x) for x in self.myLabels)

    def generate_conll(self, output_file):
        for index, row in self.df.iterrows():
            if row["begin"] == 0:
                if any(self.has_start_label(label) for label in self.labels) or 'O' in self.labels:
                    self.file += self.temp
                    self.temp = []
                else:
                    self.temp = []
                self.labels = []
                self.temp.append("\n")
                self.temp.append("{} NN NN {}\n".format(row["token"], row["label"]))
                self.labels.append(row["label"])
            else:
                self.temp.append("{} NN NN {}\n".format(row["token"], row["label"]))
                self.labels.append(row["label"])

        with open(output_file, "w", encoding="utf-8") as a:
            a.writelines(self.file)
            
    def count_labels(self, conll_path):
        label_counts = Counter()

        with open(conll_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            current_labels = []

            for line in lines:
                line = line.strip()
                if not line:
                    label_counts.update(current_labels)
                    current_labels = []
                else:
                    parts = line.split()
                    if len(parts) > 3:
                        current_labels.append(parts[3])

        return label_counts

    def count_labels_in_generated_file(self, output_file):
        label_counts = self.count_labels(output_file)
        return label_counts

    def preprocess_and_convert_to_df(self, data):
        full = CoNLL().readDataset(spark, data)
        train, test = full.randomSplit([0.8, 0.2], seed=42)
        
        df_train = train.select(F.explode(F.arrays_zip(train.token.begin, train.token.end, train.token.result, train.label.result)).alias("cols")) \
            .select(F.expr("cols['0']").alias("begin"),
                    F.expr("cols['1']").alias("end"),
                    F.expr("cols['2']").alias("token"),
                    F.expr("cols['3']").alias("label")).toPandas()
        
        df_test = test.select(F.explode(F.arrays_zip(test.token.begin, test.token.end, test.token.result, test.label.result)).alias("cols")) \
            .select(F.expr("cols['0']").alias("begin"),
                    F.expr("cols['1']").alias("end"),
                    F.expr("cols['2']").alias("token"),
                    F.expr("cols['3']").alias("label")).toPandas()
        
        return df_train, df_test

# # Veri yolunu belirtin
# data_path = ""
# 
# # Spark oturumunu başlatma
# spark = SparkSession.builder.appName("ConllGeneratorApp").getOrCreate()
# print("Spark version", spark.version)
# 
# # Sınıfı kullanma
# generator = ConllGenerator(None, myLabels)
# df_train, df_test = generator.preprocess_and_convert_to_df(data_path)
# generator = ConllGenerator(df_train, myLabels)
# generator.generate_conll('file.conll')
# label_counts = generator.count_labels_in_generated_file('file.conll')
# 
# print("Eğitim verisi etiket sayıları:")
# label_counts

#*************************************************************************************
# from transformers import AutoTokenizer, AutoModelForTokenClassification
# from sklearn.metrics import confusion_matrix
# import pandas as pd
# from seqeval.metrics import classification_report
# import warnings

class NerEvaluation:
    def __init__(self, model_name, test_conll_path, device='cuda'):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)
        self.model = self.model.to(device)
        self.device = device
        self.test_conll_path = test_conll_path
        
    def read_conll(self, filename):
        df = pd.read_csv(filename,
                        sep=' ', header=None, keep_default_na=False,
                        names=['words', 'pos', 'chunk', 'labels'],
                        quoting=3, skip_blank_lines=False, encoding="utf8")
        df = df[~df['words'].astype(str).str.startswith('-DOCSTART-')]
        df['sentence_id'] = (df.words == '').cumsum()
        return df[df.words != '']
    def write_results_to_file(self, output_path):
        with open(output_path, "w", encoding="utf-8") as f:
            original_stdout = sys.stdout  # Önceki çıktıyı koru
            sys.stdout = f  # Çıktıyı dosyaya yönlendir

            self.evaluate()  # Sonuçları yazdır

            sys.stdout = original_stdout  # Çıktıyı geri döndür
    
    def evaluate(self):
        warnings.filterwarnings('ignore')

        test = self.read_conll(self.test_conll_path)
        sents_tokens_list, truth_list = [], []
        for i in test.sentence_id.unique():
            sents_tokens_list.append(list(test[test.sentence_id == i].words))
            truth_list.append(list(test[test.sentence_id == i].labels))
        
        tokens, preds, truths = [], [], []
        for sentence_idx, sent_token_list in enumerate(sents_tokens_list):
            model_inputs = self.tokenizer(sent_token_list, is_split_into_words=True, truncation=True,
                                        padding=False, max_length=512, return_tensors="pt").to(self.device)
            word_ids = model_inputs.word_ids()
            outputs = self.model(**model_inputs)
            predictions = outputs.logits.argmax(dim=-1).tolist()[0]
            idx = 1
            while idx < len(word_ids)-1:
                word_id1 = word_ids[idx]
                word_id2 = word_ids[idx + 1]
                label = self.model.config.id2label[predictions[idx]]
                if word_id1 == word_id2:
                    while word_id1 == word_ids[idx]:                
                        idx +=1
                    idx -=1

                token = sent_token_list[word_ids[idx]]
                truth = truth_list[sentence_idx][word_ids[idx]]
                tokens.append(token)        
                preds.append(label)
                truths.append(truth)
                idx +=1

       
        conf_matrix = confusion_matrix(truths, preds)
        conf_matrix_df = pd.DataFrame(conf_matrix, columns=pd.unique(truths), index=pd.unique(truths)).to_csv("results2.csv",index = True)