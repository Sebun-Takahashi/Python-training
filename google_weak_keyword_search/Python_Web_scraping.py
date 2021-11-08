# import
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import re

# Googleのページ
URL = 'https://www.google.co.jp'


def main():

    with open('*****', encoding="utf-8") as f:  # 検索ファイルを読み込み、リストにする
        keywords = [s.rstrip() for s in f.readlines()]  # 改行コードを削除してリストにする

    with open('*****', encoding="utf-8") as f:  # 指定するドメインファイルを読み込み、リストにする
        domains = [s.rstrip() for s in f.readlines()]
    # 削除してリストにする
    # １行ずつ読み込んで改行コードを削除してリストにする

    options = Options()  # Optionsオブジェクトを作成
    options.add_argument('--headless')  # ヘッドレスモードを有効にする

    # WebDriverオブジェクトを作成
    driver = webdriver.Chrome(options=options, executable_path=r"C:\Users\****\chromedriver.exe")

    driver.get(URL)  # Googleのトップページを開く

    time.sleep(5)  # 読み込みで待機

    keywordlist = []  # 指定ドメインに含まれていないならキーワードをkeywordlistに追加
    for keyword in keywords:  # 検索キーワードを１つずつ取り出す
        search(keyword, driver)  # search関数実行
        urls = get_url(driver)  # get_url関数を実行し、戻り値をurlsに代入
        weak_keywordlist = checked(urls, domains, keywordlist, keyword)
        # domain_checked関数を実行し、戻り値をok_keywordlistに代入

    # 'result.txt'という名前を付けて、チェックしたキーワードをファイルに書き込む
    with open('\result.txt', 'w') as f:
        f.write('\n'.join(weak_keywordlist))  # ドメインチェック済みのキーワードを１行ずつ保存

    driver.quit()  # ブラウザーを閉じる


def search(keyword, driver):
    '''
    検索テキストボックスに検索キーワードを入力し、検索する
    '''
    # 検索テキストボックスの要素を取得
    input_element = driver.find_element_by_name('q')

    # 検索テキストボックスに入力されている文字列を消去
    input_element.clear()

    # 検索テキストボックスにキーワードを入力
    input_element.send_keys(keyword)

    # Enterキーを送信
    input_element.send_keys(Keys.RETURN)

    # 読み込み待機
    time.sleep(3)


def get_url(driver):
    # 各ページのURLを入れるためのリストを指定
    urls = []
    # a要素（各ページの1位から10位までのURL）取得
    objects = driver.find_elements_by_css_selector('div.yuRUbf > a')
    if objects:
        for object in objects:
            urls.append(object.get_attribute('href'))  # 各ページのURLをリストに追加
    else:
        print('URLが取得できませんでした')  # 各ページのURLが取得できなかった場合は警告を出す
    return urls  # 各ページのURLを戻り値に指定


def checked(urls, domains, keywordlist, keyword):
    '''
    URLリストからドメインを取得し、指定ドメインに含まれているかチェック
    '''
    # URLリストから各ページのURLを１つずつ取り出す
    for url in urls:
        m = re.search(r'//(.*?)/', url)  # 正規表現によるドメインの抜き出し
        domain = m.group(1)  # 抜き出したドメインを、domainに代入
        if 'www.' in domain:  # ドメインに'www.'が含まれているか確認
            domain = domain[4:]  # 'www.'の除去
        if domain in domains:  # ドメインが指定ドメインに含まれているかチェック
            print(f'キーワード「{keyword}」の検索結果には指定ドメインがありました。')  # 含まれているため警告を出す
            break
    else:
        keywordlist.append(keyword)
    return keywordlist  # ドメインチェック済みのキーワードを戻り値に指定


if __name__ == "__main__":
    main()  # 関数を実行
