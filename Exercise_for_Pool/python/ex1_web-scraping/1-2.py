from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import re
import time

# ChromeOptionsを作成してユーザーエージェントを設定
chrome_options = Options()
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")

# WebDriverのセットアップ
driver = webdriver.Chrome()

# 初期設定
base_url = "https://r.gnavi.co.jp/area/jp/rs/?curLoc=1&fw=焼肉&loc=34.72904365956014%2C135.33851831927623&r=2500&p={}"

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
Official_Url = []
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
    driver.get(url)

    elems_Store_name = driver.find_elements(By.CSS_SELECTOR, '.style_title___HrjW')
    for elem in elems_Store_name:
        Store_name.append(elem.text)

    elems_Url = driver.find_elements(By.CSS_SELECTOR, '.style_titleLink__oiHVJ')
    for elem1 in elems_Url:
        value = elem1.get_attribute('href')
        if value is not None and "https://r.gnavi.co.jp/" in value:
            Url.append(value)
    
    if page < num_pages:
        # "style_nextIcon__M_Me_"要素がクリック可能になるまで待機
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "style_nextIcon__M_Me_"))
        )

        # アイドリングタイムが3秒になるように
        end_time = time.time()
        idling_time = max(0, 3 - (end_time - start_time))
        time.sleep(idling_time)

        next_button.click()  # "style_nextIcon__M_Me_"要素をクリックしてページ遷移

# URLごとにメールアドレス、電話番号、住所(都道府県、市区町村、番地)、建物名、SSLの情報を取得
for url_number in range(len(Url)-10):
    
    if url_number == 0:
        time.sleep(3)

    start_time = time.time()
    driver.get(Url[url_number])

    elems_number = driver.find_elements(By.CSS_SELECTOR, '.number')
    if elems_number:
        Phone_number.append(elems_number[0].text)
    else:
        Phone_number.append("")

    # メールアドレスを正規表現で検索して抽出
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    text = driver.page_source
    emails = re.findall(email_pattern, text)
    if emails:
        Email.append(emails[0])  # 複数のメールアドレスがある場合、最初のものを取得
    else:
        Email.append("")

    elems_region = driver.find_elements(By.CSS_SELECTOR, '.region')
    for elem3 in elems_region:
        address_match = re.match(address_pattern, elem3.text)
        if address_match:
            Prefecture.append(address_match.group(1))
            City.append(address_match.group(2) + address_match.group(3))
            Street.append(address_match.group(4))
        else:
            Prefecture.append("")
            City.append("")
            Street.append("")

    elems_locality = driver.find_elements(By.CSS_SELECTOR, '.locality')
    if elems_locality:
        for elem4 in elems_locality:
            Locality.append(elem4.text)
    else:
        Locality.append("")

    # オフィシャルサイトのURLを取得
    official_url_elements = driver.find_elements(By.CSS_SELECTOR, 'a[title="オフィシャルページ"]')
    if official_url_elements:
        official_url = official_url_elements[0].get_attribute('href')
        Official_Url.append(official_url)
    # オフィシャルサイトのURLがhttps://で始まっているかどうかを確認し、SSL対応かどうかを判断
        if official_url.startswith('https://'):
            Ssl.append(True)
        else:
            Ssl.append(False)
    else:
        Official_Url.append("")
        Ssl.append(False)  # オフィシャルサイトのURLがない場合はSSL非対応として扱う

# データを整理
min_length = 50
Store_name = Store_name[:min_length]
Phone_number = Phone_number[:min_length]
Email = Email[:min_length]
Prefecture = Prefecture[:min_length]
City = City[:min_length]
Street = Street[:min_length]
Locality = Locality[:min_length]
Official_Url = Official_Url[:min_length]
Ssl = Ssl[:min_length]

# スクレイピングしたデータを保存するためのデータフレームを作成
data = {
    '店舗名': Store_name,
    '電話番号': Phone_number,
    'メールアドレス': Email,
    '都道府県': Prefecture,
    '市区町村': City,
    '番地': Street,
    '建物名': Locality,
    'URL': Official_Url,
    'SSL': Ssl,
}

df = pd.DataFrame(data)

# 出力ファイルのパスを指定
output_path = '/Users/kanaru/Final_Answer/Exercise_for_Pool/python/ex1_web-scraping/1-2.csv'  # フルパスを指定

# CSVファイルにデータフレームをエクスポート（Shift-Jisでエンコーディング）
df.to_csv(output_path, index=False, encoding='shift_jis')

# WebDriverを終了
driver.quit()

print("スクレイプデータは '1-2.csv' に保存されました")