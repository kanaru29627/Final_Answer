import requests
import pandas as pd
#↓正規表現を用いるために必要
import re
from bs4 import BeautifulSoup
import time

# 初期設定
base_url = "https://r.gnavi.co.jp/area/jp/rs/?curLoc=1&fw=焼肉&loc=34.72904365956014%2C135.33851831927623&r=2500&p={}"
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
header = {
    'User-Agent': user_agent
}

# データを格納するためのリスト
Store_name = []
Phone_number = []
Email = []
Address = []
Prefecture = []
City = []
Street = []
Locality = []
Url = []
Ssl = []

# 正規表現パターンを定義
address_pattern = r'(.+?[都道府県])(.+?[市区町村])(.+?[市区町村])(.+)'

# ページ数を指定
num_pages = 3

for page in range(1, num_pages + 1):
    url = base_url.format(page)
    
    # 最初のリクエストの前に3秒間のアイドリングタイムを追加
    if page == 1:
        time.sleep(3)

    # ここで最初のリクエストが実行される
    start_time = time.time()
    response = requests.get(url, headers=header)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')

    elems_Store_name = soup.select('.style_title___HrjW')
    for elem in elems_Store_name:
        Store_name.append(elem.text)

    elems_Url = soup.select('.style_titleLink__oiHVJ')
    for elem1 in elems_Url:
        value = elem1.get('href')
        if value is not None and "https://r.gnavi.co.jp/" in value:
            Url.append(value)
        
    # アイドリングタイムが3秒になるように
    end_time = time.time()
    idling_time = max(0, 3 - (end_time - start_time))
    time.sleep(idling_time)

# URLごとに店舗のメールアドレス、電話番号、住所(都道府県、市区町村、番地)、建物名の情報を取得
for url_number in range(len(Store_name)-10):
    url1 = Url[url_number]
    
    if page == 0:
        time.sleep(3)
    
    start_time = time.time()
    response1 = requests.get(url1, headers=header)
    response1.encoding = 'utf-8'
    soup1 = BeautifulSoup(response1.text, 'lxml')

    elems_number = soup1.select('.number')
    if elems_number:
        First_phone_number = elems_number[0].text
        Phone_number.append(First_phone_number)
    else:
        Phone_number.append("") 

    # メールアドレスを正規表現で検索して抽出
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    text = str(soup1)
    emails = re.findall(email_pattern, text)
    if emails:
        Email.append(emails[0])  # 複数のメールアドレスがある場合、最初のものを取得
    else:
        Email.append("")

    elems_region = soup1.select('.region')
    for elem2 in elems_region:
        address_match = re.match(address_pattern, elem2.text)
        if address_match:
            Prefecture.append(address_match.group(1))
            City.append(address_match.group(2) + address_match.group(3))
            Street.append(address_match.group(4))
        else:
            Prefecture.append("")
            City.append("")
            Street.append("")
    
    elems_locality = soup1.select('.locality')
    if elems_locality:
        for elem3 in elems_locality:
            Locality.append(elem3.text)
    else:
        Locality.append("")

    #課題1-1はURLを取得しないが、そうするとSSLが取得できない。そのため、ぐるなびの店舗ページのURLからSSLを取得した
    if response1.status_code == 200:
        if response1.url.startswith('https://'):
            Ssl.append(True)
        else:
            Ssl.append(False)
    else:
        print("ウェブサイトへのアクセスに問題があります。")

    # アイドリングタイムが3秒になるように
    end_time = time.time()
    idling_time = max(0, 3 - (end_time - start_time))
    time.sleep(idling_time)

# データを整理
min_length = 50
Store_name = Store_name[:min_length]
Phone_number = Phone_number[:min_length]
Email = Email[:min_length]
Prefecture = Prefecture[:min_length]
City = City[:min_length]
Street = Street[:min_length]
Locality = Locality[:min_length]
Ssl = Ssl[:min_length]

# スクレイピングしたデータを保存するためのデータフレームを作成
data = {
    '店舗名': Store_name,
    '電話番号': Phone_number,
    'メールアドレス':Email,
    '都道府県': Prefecture,
    '市区町村': City,
    '番地': Street,
    '建物名': Locality,
    'URL': "",
    'SSL': Ssl,
}

df = pd.DataFrame(data)

# 出力ファイルのパスを指定
output_path = '/Users/kanaru/Final_Answer/Exercise_for_Pool/python/ex1_web-scraping/1-1.csv'  # フルパスを指定

# CSVファイルにデータフレームをエクスポート（Shift-Jisでエンコーディング）
df.to_csv(output_path, index=False, encoding='shift_jis')

print("スクレイプデータは '1-1.csv' に保存されました")