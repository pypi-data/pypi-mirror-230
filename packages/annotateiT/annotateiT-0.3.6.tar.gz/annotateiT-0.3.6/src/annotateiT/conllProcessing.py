import pyspark
import sparknlp
from pyspark.sql import SparkSession
from collections import Counter
spark = sparknlp.start() 
from sparknlp.training import CoNLL
import pyspark.sql.functions as F
class splitCoNLL:
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

#********************************************************************************
from collections import defaultdict
from nltk import wordpunct_tokenize, sent_tokenize

class makeConll:
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