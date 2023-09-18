from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup
import pandas as pd
from lxml import etree
import time
import os

class DissertScraper:
    """
    Açılan chrom scrap sayfasından aram kriterleri girildikten sonra bul tuşuna basılır
    ve sütun olarak üniversite seçilir. scrap işleminin tamamlanması beklenir.
    Scrap edilen 30 lu json dosyalar olarak output klasöründe saklanır. 
    """
    def __init__(self):
        self.options = Options()
        self.driver = webdriver.Chrome(executable_path='./chromedriver', options=self.options)
        self.url = "https://tez.yok.gov.tr/UlusalTezMerkezi/"
            
    def ajax_complete(self):
        try:
            return 0 == self.driver.execute_script("return jQuery.active")
        except WebDriverException:
            pass

    def extract_data(self, path):
        try:
            clickable = self.driver.find_element(by='xpath', value=path)
        except Exception as e:
            print('clickable object:', e)
        ActionChains(self.driver).click(clickable).perform()
        time.sleep(2)

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        en_absract = soup.find(id='td1').text
        tr_absract = soup.find(id='td0').text
        kapat = self.driver.find_element(by='xpath', value='/html/body/div[3]/div[1]/a/span')
        kapat.click()
        print('işlem başarılı')
        self.driver.switch_to.default_content()
        return tr_absract, en_absract
    
    def total_result_number(self):
        satır_sayısı_xpath = '/html/body/div[2]/div[1]/table/tbody/tr[2]/td/div[3]/table/tfoot/tr/td/p'
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        source = etree.HTML(str(soup))
        row_numbers = int(source.xpath(satır_sayısı_xpath)[0].text.split()[-1])
        return row_numbers

    def iteration_number(self, row_numbers):
        if row_numbers % 30:
            döngü = row_numbers // 30 + 1
            son_sayfa_satır_sayısı = row_numbers % 30
            return döngü, son_sayfa_satır_sayısı
        else:
            döngü = row_numbers // 30
            son_sayfa_satır_sayısı = 0
            return döngü, son_sayfa_satır_sayısı

    def get_page_source(self):
        newURl = self.driver.window_handles[0]
        self.driver.switch_to.window(newURl)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        dom = etree.HTML(str(soup))
        return dom

    def next_page(self):
        next_button_xpath = '/html/body/div[2]/div[1]/table/tbody/tr[2]/td/div[2]/table/tfoot/tr/td/div/div[1]/div/ul/li[7]/a'
    
        try:
            next_button = self.driver.find_element(by='xpath', value=next_button_xpath)
            next_button.click()
        except NoSuchElementException as e:
            print('Element bulunamadı:', e)
        
        wait(self.driver, 10).until(
            lambda driver: self.ajax_complete(), "Timeout waiting for page to load")
        
        print("sonraki sayfaya geçildi")

    def get_info(self, source, number):
        data_path = f'//*[@id="div1"]/table/tbody/tr[{number}]/td[2]/span'
        try:
            tez_no = source.xpath(f'//*[@id="div1"]/table/tbody/tr[{number}]/td[2]/span')[0].text
        except:
            tez_no = None
        # Diğer verileri benzer şekilde çekmeye devam edebilirsiniz...

        try:
            yazar  = source.xpath(f'//*[@id="div1"]/table/tbody/tr[{number}]/td[3]')[0].text
        except:
            yazar = None

        try:
            yıl = source.xpath(f'//*[@id="div1"]/table/tbody/tr[{number}]/td[4]')[0].text
        except:
            yıl = None

        try:
            try:
                tez_adı_tr = source.xpath(f'//*[@id="div1"]/table/tbody/tr[{number}]/td[5]')[0].text
            except:
                tez_adı_tr = None

            try:
                tez_adı_en = source.xpath(f'//*[@id="div1"]/table/tbody/tr[{number}]/td[5]/span')[0].text
            except:
                tez_adı_en = None
            
            tez_adı = {'tr':tez_adı_tr, 'en':tez_adı_en}
        except:
            tez_adı = None
            
        try:
            üniversite = source.xpath(f'//*[@id="div1"]/table/tbody/tr[{number}]/td[6]')[0].text
        except:
            üniversite = None
        
        try:
            tez_türü = source.xpath(f'//*[@id="div1"]/table/tbody/tr[{number}]/td[7]')[0].text
        except:
            tez_türü = None

        try:    
            konu = source.xpath(f'//*[@id="div1"]/table/tbody/tr[{number}]/td[8]')[0].text
        except:
            konu = None

        try:
            tr, en = self.extract_data(data_path)
            tr_en = {'tr':tr, 'en':en}
        except:
            tr, en = None, None
            tr_en = None     
        
        return tez_no, yazar, yıl, tez_adı, üniversite, tez_türü, konu, tr_en   

    def launch(self):
        row_numbers = self.total_result_number()
        sayfa_sayısı, son_sayfa_satır_sayısı = self.iteration_number(row_numbers)  # sayfa_sayısı ve son_sayfa_satır_sayısı burada tanımlanır
        print(f'bulunan sonuç sayısı: {row_numbers}, tahmini scrap süresi: {row_numbers * 4.05/60:.2f} dakika')
        tez_no_data, yazar_data, yıl_data, tez_adı_data, üniversite_data, tez_türü_data, konu_data, tr_en_data = [], [], [], [], [], [], [], []
        for i in range(1, sayfa_sayısı + 1):
            source = self.get_page_source()
            print(f'{i}. sayfa')
            if i != sayfa_sayısı:
                for j in range(1, 31):  # Her seferinde 30 row çek
                    print(f'{i}. sayfa {j}. satır')
                    tez_no, yazar, yıl, tez_adı, üniversite, tez_türü, konu, tr_en = self.get_info(source, j)
  
                    tez_no_data.append(tez_no)               
                    yazar_data.append(yazar)
                    yıl_data.append(yıl)
                    tez_adı_data.append(tez_adı)
                    üniversite_data.append(üniversite)
                    tez_türü_data.append(tez_türü)
                    konu_data.append(konu)
                    tr_en_data.append(tr_en)
                    time.sleep(1.5)
                self.next_page()

            else:
                source = self.get_page_source()
                for j in range(1, son_sayfa_satır_sayısı + 1):
                    print(f'son sayfa {j}. satır')
                    tez_no, yazar, yıl, tez_adı, üniversite, tez_türü, konu, tr_en = self.get_info(source, j)

                    tez_no_data.append(tez_no)           
                    yazar_data.append(yazar)
                    yıl_data.append(yıl)
                    tez_adı_data.append(tez_adı)
                    üniversite_data.append(üniversite)
                    tez_türü_data.append(tez_türü)
                    konu_data.append(konu)
                    tr_en_data.append(tr_en)
                    time.sleep(1.5)  
        
        # Her bir sorgunun sonuçlarını ayrı JSON dosyasına kaydedin
        for sorgu_sayısı in range(1, sayfa_sayısı + 1):
            output_file = f'output/arama_sonucu_{sorgu_sayısı}.json'
            start_index = (sorgu_sayısı - 1) * 30
            end_index = sorgu_sayısı * 30 if sorgu_sayısı != sayfa_sayısı else start_index + son_sayfa_satır_sayısı
            
            sorgu_df = pd.DataFrame({"tez_no": tez_no_data[start_index:end_index], 'yazar': yazar_data[start_index:end_index], 'yıl': yıl_data[start_index:end_index], 'tez_adı': tez_adı_data[start_index:end_index], 'üniversite': üniversite_data[start_index:end_index], \
                                     'tez_türü': tez_türü_data[start_index:end_index], 'konu': konu_data[start_index:end_index], 'tr_en': tr_en_data[start_index:end_index]})
            
            sorgu_df.to_json(output_file, orient='records')
            print(f'{output_file} dosyası kaydedildi')
        
        print('Tüm sorgular tamamlandı')

    def close(self):
        self.driver.quit()
    
    def run(self):
        self.driver.get(self.url)
        time.sleep(30)
        self.launch()
        self.close()

# scraper = DissertScraper()
# scraper.run()
__doc__ = """
Bu kod parçası, YÖK Tez Merkezi'nden tezleri çekmek için kullanılan kod parçasıdır. Uygun chromedriver.exe dosyasının bulunduğundan emin olun.
Açılan chrom scrap sayfasından aram kriterleri girildikten sonra bul tuşuna basılır ve sütun olarak üniversite seçilir. 
Scrap işleminin tamamlanması beklenir. Scrap edilen 30 lu json dosyalar olarak output klasöründe saklanır.
Bir output klasörü oluşturmayı unutmayın.
"""

#********************************************************************
import os
import pandas as pd
from abc import ABC, abstractmethod

class Descriptive(ABC):
    """
    scrap edilen json dosyalar okunur ve birlesik_veri adında bir csv file olarak output klasöründe saklanır
    """
    def __init__(self, klasor_yolu="output"):
        self.klasor_yolu = klasor_yolu        

    @abstractmethod
    def read_data(self):
        pass

    @abstractmethod
    def convertor(self):
        pass

class JsonProcessor(Descriptive):

    def __init__(self, klasor_yolu="output"):
        super().__init__(klasor_yolu)

    def read_data(self):
        self.json_dosyalari = []
        for dosya in os.listdir(self.klasor_yolu):
            if dosya.endswith(".json"):
                self.json_dosyalari.append(os.path.join(self.klasor_yolu, dosya))

    def convertor(self):
        json_verileri = [pd.read_json(dosya) for dosya in self.json_dosyalari]
        birlesik_veri = pd.concat(json_verileri, ignore_index=True).dropna(subset=["tr_en"])
        birlesik_veri.to_csv(os.path.join(self.klasor_yolu, "birlesik_veri.csv"), index=False)
        return birlesik_veri

# dissertion olarak scrap edilen json files "output" klasörüne konulur ve preprocess edilir. elde edilen "output/birlesik_veri.csv"
# processor = JsonProcessor()
# processor.read_data() 
# df = processor.convertor()
    
#*************************************************************
    
import pandas as pd
import ast

class DataPreprocessor:
    """
    output klasöründe bulunan birlesik_veri.csv dosyası işlemden geçirilir ve output.csv olarak pd.DataFrame olarak
    output klasöründe saklanır
    """
    def __init__(self, file_path="output/birlesik_veri.csv"):
        self.file_path = file_path
        self.data = None

    def load_data(self):
        self.data = pd.read_csv(self.file_path)
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
                                  'tez_türü': "type", 'konu': "field", 'tr': "tr_abs", 'en': "text",
                                  'tr_titel': "tr_title", 'en_titel': "en_title"}, inplace=True)

    def save_processed_data(self):
        self.data.to_csv("output/preprocessed.csv", index=False)

    def run(self):
        self.load_data()
        self.preprocess_abstracts()
        self.preprocess_titles()
        self.rename_columns()
        self.save_processed_data()

#input olarak alınan dissertionlara ait "output/birlesik_veri.csv" file alınır ve "output/preprocessed.csv" olarak kaydedilir.
# dataProcessor = DataPreprocessor()
# dataProcessor.run()

#/************************************************************

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class ImageProcessor:
    def __init__(self, folder_path="output"):
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

#input olarak alınan "output/preprocessed.csv" ile descriptive görseller "output" altına kaydedilir.
# img_processor = ImageProcessor()
# img_processor.process_images()