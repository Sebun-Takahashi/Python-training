# ブラウザを自動操作するためseleniumをimport
from selenium import webdriver
# seleniumでヘッドレスモードを指定するためにimport
from selenium.webdriver.chrome.options import Options
# seleniumでEnterキーを送信する際に使用するのでimport
from selenium.webdriver.common.keys import Keys
# HTTPリクエストを送る為にrequestsをimport
import requests
# HTMLから必要な情報を得る為にBeautifulSoupをimport
from bs4 import BeautifulSoup
# グーグルスプレッドシートを操作する為にimport
import gspread
# グーグルスプレッドシートの認証情報設定の為にimport
from google.oauth2.service_account import Credentials

import time

# グーグルのURL
URL = 'https://google.co.jp'
# グーグルのURLタイトルの確認のため
URL_TITLE = 'Google'


# 2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']

# 認証情報設定
# ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
credentials = Credentials.from_service_account_file(
    "", scopes=scope)

# 共有設定したスプレッドシートキーを格納
SPREADSHERET_KEY = ''


def main():
    '''
    メインの処理
    Googleでキーワードを検索
    １ページ目の情報を取得し、Googleスプレッドシートに出力
    '''

    # 検索キーワードが入力されたテキストファイルを読み込む
    with open('google_multi_search\keyword.txt', encoding='utf-8') as f:
        keywords = [s.rstrip() for s in f.readlines()]

    # Options()オブジェクトの生成
    options = Options()
    # options.add_argument('--headless') # ヘッドレスモードを有効にする
    # options.add_argument('--headless')
    # ChromeのWebDriverオブジェクトを作成
    driver = webdriver.Chrome(
        options=options,
        executable_path="google_weak_keyword_search\chromedriver.exe")

    # Googleのトップページを開く
    driver.get(URL)

    # 2秒待機
    time.sleep(2)

    assert URL_TITLE in driver.title  # タイトルにgoogleがついていることを確認
    # Google検索処理
    for keyword in keywords:
        print(f"検索キーワード:{keyword}")
        search(driver, keyword)
    # 情報取得処理
    items = get_info(driver, keyword)
    # Googleスプレッドシート出力処理
    spread_out(items)
    # ブラウザーを閉じる
    driver.quit()


def search(driver, keyword):
    '''
    検索テキストボックスに検索キーワードを入力し、検索する
    '''

    # 検索テキストボックスの要素をname属性から取得
    input_element = driver.find_element_by_name('q')
    # 検索テキストボックスに入力されている文字列を消去
    input_element.clear()
    # 検索テキストボックスにキーワードを入力
    input_element.send_keys(keyword)
    # Enterキーを送信
    input_element.send_keys(Keys.RETURN)
    # 2秒待機
    time.sleep(2)


def get_info(driver, keyword):
    '''
    タイトル、URL、説明文、H1からH5までの情報を取得
    '''

    # 辞書を使って複数のアイテムを整理 -> 引数が減る＋返り値が減る
    items = {
        'keyword': keyword,
        'title': ['タイトル'],
        'url': [],
        'description': ['説明文'],
        'h1': [],
        'h2': [],
        'h3': [],
        'h4': [],
        'h5': []
    }
    # seleniumによる検索結果のurlの取得
    urls = driver.find_elements_by_css_selector('div.yuRUbf > a')
    if urls:
        for url in urls:
            items['url'].append(url.get_attribute('href').strip())

    # seleniumによるtitleの取得
    titles = driver.find_elements_by_css_selector('div.yuRUbf > a > h3')
    if titles:
        for title in titles:
            items['title'].append(title.text.strip())

    # seleniumによるdescription（説明文）の取得
    descriptions = driver.find_elements_by_css_selector(
        'div.IsZvec > div > span')
    if descriptions:
        for description in descriptions:
            items['description'].append(description.text.strip())

    # h1?h5見出しの取得

    for url in items['url']:
        try:
            # URLにGETリクエストを送る
            response = requests.get(url)  # GETリクエスト
            soup = BeautifulSoup(response.content, 'html.parser')
            # HTMLから情報を取り出す為にBeautifulSoupオブジェクトを得る
            time.sleep(1)  # 1秒待機

        except requests.exeption.SSLError:  # SSlエラーが起こった時の処理を記入
            response = requests.get(url, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            time.sleep(1)  # 1秒待機

        # h1
        # h1タグを全てリストとして取得
        h1s = soup.find_all('h1')
        # h1タグからテキストを取得してリストに入れる
        h1_list = []
        for h1 in h1s:
            if h1.get_text().strip():
                h1_list.append(h1.get_text())
        items['h1'].append(h1_list)

        # h2
        # h2タグを全てリストとして取得
        h2s = soup.find_all('h2')
        # h2タグからテキストを取得してリストに入れる
        h2_list = []
        for h2 in h2s:
            if h2.get_text().strip():
                h2_list.append(h2.get_text())
        items['h2'].append(h2_list)

        # h3
        h3s = soup.find_all('h3')
        h3_list = []
        for h3 in h3s:
            if h3.get_text().strip():
                h3_list.append(h3.get_text())
        items['h3'].append(h3_list)

        # h4
        h4s = soup.find_all('h4')
        h4_list = []
        for h4 in h4s:
            if h4.get_text().strip():
                h4_list.append(h4.get_text())
        items['h4'].append(h4_list)

        # h5
        h5s = soup.find_all('h5')
        h5_list = []
        for h5 in h5s:
            if h5.get_text().strip():
                h5_list.append(h5.get_text())
        items['h5'].append(h5_list)
    return items


def spread_out(items):
    '''
    Googleスプレッドシートに情報を出力
    '''

    # 制限
    # ①ユーザーごとに100秒あたり100件のリクエスト
    # ②1秒あたり10件まで

    # OAuth2の資格情報を使用してGoogleAPIにログイン
    gc = gspread.authorize(credentials)

    # シートが作成されているか確認するためのフラグ
    flag = False

    try:
        # 共有設定したスプレッドシートのシート1を開く
        workbook = gc.open_by_key(SPREADSHERET_KEY)
        # ワークシートを作成（タイトルがkeywordで、50行、50列）
        worksheet = workbook.add_worksheet(
            title=items['keyword'], rows='50', cols='50')

        # シートが作成されたらフラグを立てる
        flag = True

        # スプレッドシート書き込み処理
        # キーワードの書き込み
        worksheet.update_cell(1, 1, '検索キーワード')
        worksheet.update_cell(1, 2, items['keyword'])
        # 1秒待機
        time.sleep(1)

        # 順位の書き込み
        column = 2
        worksheet.update_cell(2, 1, '順位')
        for ranking in range(1, 11):
            worksheet.update_cell(2, column, ranking)
            column += 1

        # 3秒待機
        time.sleep(3)

        # 「タイトル」の書き込み
        column = 1
        for title in items['title']:
            worksheet.update_cell(3, column, title)
            column += 1

        # 3秒待機
        time.sleep(3)

        # 「URL」の書き込み
        column = 2
        worksheet.update_cell(4, 1, 'URL')
        for url in items['url']:
            worksheet.update_cell(4, column, url)
            column += 1

        # 3秒待機
        time.sleep(3)

        # 「ディスクリプション」の書き込み
        column = 1
        for description in items['description']:
            worksheet.update_cell(5, column, description)
            column += 1

        # 3秒待機
        time.sleep(3)

        # 「h1」の書き込み
        worksheet.update_cell(6, 1, 'H1タグ')
        column = 2
        for h1_list in items['h1']:
            if h1_list:
                h1_str = '***'.join(h1_list)
                worksheet.update_cell(6, column, h1_str)
                column += 1
            else:
                worksheet.update_cell(6, column, '無し')
                column += 1
        # 3秒待機
        time.sleep(3)

        # 「h2」の書き込み
        worksheet.update_cell(7, 1, 'H2タグ')
        column = 2
        for h2_list in items['h2']:
            if h2_list:
                h2_str = '***'.join(h2_list)
                worksheet.update_cell(7, column, h2_str)
                column += 1
            else:
                worksheet.update_cell(7, column, '無し')
                column += 1
        # 3秒待機
        time.sleep(3)

        # 「h3」の書き込み
        worksheet.update_cell(8, 1, 'H3タグ')
        column = 2
        for h3_list in items['h3']:
            if h3_list:
                h3_str = '***'.join(h3_list)
                worksheet.update_cell(8, column, h3_str)
                column += 1
            else:
                worksheet.update_cell(8, column, '無し')
                column += 1
        # 3秒待機
        time.sleep(3)

        # 「h4」の書き込み
        worksheet.update_cell(9, 1, 'H4タグ')
        column = 2
        for h4_list in items['h4']:
            if h4_list:
                h4_str = '***'.join(h4_list)
                worksheet.update_cell(9, column, h4_str)
                column += 1
            else:
                worksheet.update_cell(9, column, '無し')
                column += 1
        # 3秒待機
        time.sleep(3)

        # 「h5」の書き込み
        worksheet.update_cell(10, 1, 'H5タグ')
        column = 2
        for h5_list in items['h5']:
            if h5_list:
                h5_str = '***'.join(h5_list)
                worksheet.update_cell(10, column, h5_str)
                column += 1
            else:
                worksheet.update_cell(10, column, '無し')
                column += 1
        # 3秒待機
        time.sleep(3)
    # エラー処理
    except Exception as e:
        print('エラー内容', e)
        if '429' in str(e):
            # グーグルスプレッドシートのAPIの制限に達した場合
            if flag:
                workbook.del_worksheet(worksheet)
                # 100秒待機
                time.sleep(100)
        if '400' in str(e):
            print("すでに同じ名前のシートが存在するため次のキーワードを実行します。")
            # スプレッドシートに既にデータが存在している場合


if __name__ == '__main__':
    main()
