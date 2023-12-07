import pandas as pd

def load_keywords():
    # 讀取csv檔案
    df = pd.read_csv('EAP相關網站.csv')

    # 將csv檔案轉換為字典
    keywords_dict = df.set_index('關鍵字')['回應內容'].to_dict()

    return keywords_dict
