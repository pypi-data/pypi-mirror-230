import pandas as pd
import ast

class DataPreprocessor:
    """
    output klasöründe bulunan birlesik_veri.csf dosyası işlemden geçirilir ve output.csv olarak pd.DataFrame olarak
    output klasörüğnde saklanır
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = pd.read_csv(file_path)
        self.data[["tez_no", "yıl"]] = self.data[["tez_no", "yıl"]].astype(int)
        
    def process_text_abs(self, text):
        try:
            data = ast.literal_eval(text.replace('\x00', ''))
            return pd.Series({'tr': data['tr'], 'en': data['en']})
        except:
            return pd.Series({'tr': '', 'en': ''})
        
    def preprocess_abstracts(self):
        processed_abs = self.data["tr_en"].apply(self.process_text_abs)
        df = pd.concat([self.data, processed_abs], axis=1)
        df['tr'] = df['tr'].str.strip('\n\t ')
        df['en'] = df['en'].str.strip('\n\t ')
        self.data = df.drop(["tr_en"], axis=1)
        
    def process_text_titel(self, text):
        try:
            data = ast.literal_eval(text.replace('\x00', ''))
            return pd.Series({'tr_titel': data['tr'], 'en_titel': data['en']})
        except:
            return pd.Series({'tr_titel': '', 'en_titel': ''})
        
    def preprocess_titles(self):
        processed_titel = self.data["tez_adı"].apply(self.process_text_titel)
        df = pd.concat([self.data, processed_titel], axis=1)
        self.data = df.drop(["tez_adı"], axis=1)
        
    def rename_columns(self):
        self.data.rename(columns={'tez_no': "no", 'yazar': "author", 'yıl': "year", 'üniversite': "university",
                                  'tez_türü': "type", 'konu': "field", 'tr': "tr_abs", 'en': "en_abs",
                                  'tr_titel': "tr_title", 'en_titel': "en_title"}, inplace=True)
        
    def save_processed_data(self):
        self.data.to_csv("output/preprocessed.csv", index=False)
    
    def run(self):
        #self.process_text_abs()
        self.preprocess_abstracts()
        #self.process_text_titel()
        self.preprocess_titles()
        self.rename_columns()
        self.save_processed_data()

        
# Veri işleme işlemi için bir DataPreprocessor nesnesi oluşturun
# processor = DataPreprocessor("input.csv")

# Veriyi işle ve sonucu belirtilen çıkış yoluna kaydet
# processor.run("output.csv")

#********************************************************************
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class ImageProcessor:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.csv_file_path = os.path.join(folder_path, 'preprocessed.csv')

    def process_images(self):
        # CSV dosyasını okuyun
        output = pd.read_csv(self.csv_file_path)

        # Görsel işleme ve kaydetme işlemleri burada yapılabilir
        try:
            fig, ax = self.plot_and_save(output, 'year', 'Thesis by Year')
            self.save_image(fig, 'Thesis_by_Year.png')
        except Exception as e:
            print("Hata:", e)

        try:
            fig, ax = self.plot_and_save(output, 'university', 'Studies by Universities', order=output['university'].value_counts().iloc[:10].index)
            self.save_image(fig, 'Studies_by_Universities.png')
        except Exception as e:
            print("Hata:", e)

        # Diğer görselleştirmeleri de aynı şekilde devam ettirin
        # Diğer görselleştirmeleri de aynı şekilde devam ettirin
        try:
            fig, ax = self.plot_and_save(output, 'type', 'Distribution of Studies According to Thesis Types', rotation=0)
            self.save_image(fig, 'Distribution_of_Studies_According_to_Thesis_Types.png')
        except:
            pass
        try:
            fig, ax = self.plot_and_save(output, 'field', 'Distribution of Thesis Studies by Subject', order=output.field.value_counts().iloc[:5].index)
            self.save_image(fig, 'Distribution_of_Thesis_Studies_by_Subject.png')
        except Exception as e:
            print("Hata:", e)
        try:
            tezturu_YL = output[output.type == 'Yüksek Lisans']
            # Distribution of Master Degree Studies by Universities
            fig, ax = self.plot_and_save(tezturu_YL, 'university', 'Distribution of Master Degree Studies by Universities', order=tezturu_YL.university.value_counts().iloc[:5].index)
            self.save_image(fig, 'Distribution_of_Master_Degree_Studies_by_Universities.png')
        except Exception as e:
            print("Hata:", e)
        try:
            tezturu_PhD = output[output.type == 'Doktora']
            # Distribution of Doctoral Studies by Universities
            fig, ax = self.plot_and_save(tezturu_PhD, 'university', 'Distribution of Doctoral Studies by Universities', order=tezturu_PhD.university.value_counts().iloc[:5].index)
            self.save_image(fig, 'Distribution_of_Doctoral_Studies_by_Universities.png')
        except Exception as e:
            print("Hata:", e)
        try:      
            tezturu_uzmanlık = output[output.type == 'Tıpta Uzmanlık']
            # Distribution of Specialization in Medicine Studies by Universities
            fig, ax = self.plot_and_save(tezturu_uzmanlık, 'university', 'Distribution of Specialization in Medicine Studies by Universities', order=tezturu_uzmanlık.university.value_counts().iloc[:5].index)
            self.save_image(fig, 'Distribution_of_Specialization_in_Medicine_Studies_by_Universities.png')
        except Exception as e:
            print("Hata:", e)
        

        print("Görseller kaydedildi.")

    def plot_and_save(self, data, x, title, order=None, rotation=75):
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.countplot(x=x, data=data, order=order)
        plt.title(title)
        plt.xticks(rotation=rotation)
        for i in ax.patches:
            ax.text(i.get_x() + 0.25, i.get_height() + 0.1, str(round((i.get_height()))), fontsize=7, color='black')
        plt.subplots_adjust(bottom=0.15)
        return fig, ax

    def save_image(self, fig, file_name):
        image_path = os.path.join(self.folder_path, file_name)
        fig.savefig(image_path, dpi=300, bbox_inches='tight')
        plt.close(fig)

# if __name__ == "__main__":
#     klasor_yolu = "/home/benjamin/Documents/GitHub/myPrivateProject/yoktezScrapping/output"  # Verilerin ve kaydedilecek görsellerin bulunduğu klasör yolunu belirtin

#     processor = ImageProcessor(klasor_yolu)
#     processor.process_images()



