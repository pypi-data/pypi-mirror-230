import json
import pandas as pd
import re

class JsonDataHandler:
    """ Label studiodan gelen json dosyasını okuyup, dataframe döndürür. """

    def __init__(self, json_file):
        self.json_file = json_file

    def read_data(self):
        with open(self.json_file, 'r') as f:
            data = json.load(f)
        return data

    def process_data(self, data):
        # ... (your existing process_data logic)
        # convert data to dataframe
        df = pd.DataFrame(data)
        df = df[['data', 'annotations']]
        df = df.explode('annotations')
        df = df.reset_index(drop=True)

        # convert annotations to dataframe
        df = pd.concat([df.drop(['annotations'], axis=1), df['annotations'].apply(pd.Series)], axis=1)
        df = df[['data', 'result']]
        df = df.explode('result')
        df = df.reset_index(drop=True)

        # get values from data column
        df = pd.concat([df.drop(['data'], axis=1), df['data'].apply(pd.Series)], axis=1)

        # get values from result column
        df = pd.concat([df.drop(['result'], axis=1), df['result'].apply(pd.Series)], axis=1)
        df = df[['text', 'value']]
        df.rename(columns={'text': 'text1'}, inplace=True)

        # get values from value column
        df = pd.concat([df.drop(['value'], axis=1), df['value'].apply(pd.Series)], axis=1)
        df = df[['text1', 'text', 'start', 'end', 'labels']]
        df.rename(columns={'text1':'text', "start":"begin", 'text': 'chunk'}, inplace=True)
        df.dropna(subset=['labels'], inplace=True)


        #extract values from the df.labels column
        df['labels'] = df['labels'].apply(lambda x: x[0])

        # give unique id to each text
        df['id'] = pd.factorize(df['text'])[0] + 1

        df.begin = df.begin.astype(int)
        df.end = df.end.astype(int)
        df.id = df.id.astype(int)

        return df
#************************************************************************    
   
class LSProcessor:
    """ Bu class label-studio arayüzü için json file ve labelları içeren xml file üretir.Input = csv --> output = json."""

    def __init__(self, result_csv_path):
        self.result_df = pd.read_csv(result_csv_path)
        self.uni_labels = []

    def process(self):
        self.result_df.dropna(inplace=True)
        self.result_df.sort_values(by=["id", 'begin', "end"], inplace=True)
        self.result_df.reset_index(drop=True, inplace=True)
        self.result_df = self.result_df[['text', 'begin', 'end', 'chunk', 'labels']].copy()
        self.result_df.columns = ['text1', 'start', 'end', 'text', 'labels']
        self.result_df['labels'] = self.result_df['labels'].apply(lambda x: [x])
        self.uni_labels = self.result_df['labels'].explode().unique()

    def generate_json(self, json_output_path):
        json_data = []
        for text, group in self.result_df.groupby('text1'):
            dat = {}
            dic = {'predictions':[], 'annotations':[]}
            di = {'result':[]}
            a = group[['start', 'end', 'text', 'labels']]
            ind = list(a.index)
            for i in ind:
                d = {'id': f'{i}',
                    'from_name': 'label',
                    'to_name': 'text',
                    'type': 'labels'}
                n = {}
                n['start'] = str(a.loc[i, 'start'])
                n['end'] = str(a.loc[i, 'end'])
                n['text'] = a.loc[i, 'text']
                n['labels'] = a.loc[i, 'labels']
                d['value'] = n
                di['result'].append(d)
            dat['text'] = f'{text}'
            dic['data'] = dat
            dic['predictions'].append(di)
            dic['annotations'].append(di)
            json_data.append(dic)

        with open(json_output_path, "w") as outfile:
            json.dump(json_data, outfile, cls=SetEncoder, indent=2)
    
    def generate_label_studio_xml(self, xml_output_path):
        label_defs = ''.join([f'<Label value="{label}"></Label>' for label in self.uni_labels])
        label_studio_xml = f'<View><Labels name="label" toName="text">{label_defs}</Labels><Text name="text" value="$text"></Text></View>'
        with open(xml_output_path, "w") as label_file:
            label_file.write(label_studio_xml)

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)