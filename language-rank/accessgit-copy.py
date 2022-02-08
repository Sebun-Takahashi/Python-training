# 必要なライブラリのimport
import json
import requests
import pandas as pd


def main():
    '''
    メインの実行部分
    '''
    # Github APIを使って言語とスター数のデータフレームの作成
    df = get_stars_repos()
    # 言語でグループ化して、スター数の和を求め、スター数の多さで並べ替え
    grop = df.groupby('language')
    df = grop.sum().sort_values(by='stars', ascending=False)
    # 並べ替えたデータフレームを出力
    print(df)


def get_api_repos(endpoint):
    '''
    エンドポイントにGETリクエストを送って得られたデータから
    言語ごとのスター数をまとめたデータフレームを作る
    '''
    # エンドポイントにGETリクエストを送ってデータを取得
    r = requests.get(endpoint)
    # ステータスコードが200じゃない（アクセスできない）場合の
    if r.status_code != 200:
        print('エンドポイントにアクセスできません')
    # json文字列をjson.loads()でPythonで扱える辞書形式に変換する
    repos_dict = json.loads(r.content)
    # 辞書からアイテムを取り出す
    repos_list = repos_dict['items']  # リポジトリのデータが入った100個の辞書を要素に持つリストを取り出す
    # language(言語)とstargazers_count(スター数)のリストを作成する
    stars = []
    language = []
    for repo_dict in repos_list:
        stars.append(repo_dict['stargazers_count'])
        language.append(repo_dict['language'])
    # languagesとstarsのリストからデータフレームの作成
    df = pd.DataFrame({'language': language, 'stars': stars})
    return df


def get_access_token():
    '''
    アクセストークンをテキストファイルから取得する
    '''
    with open(r'', 'r') as f:
        return f.read().strip()


def get_stars_repos():
    '''
    アクセストークンを取得して、エンドポイントを指定して、
    get_api_repos関数を使ってスター数が多いリポジトリから言語とスター数の
    スター数が多い順のデータフレームを作成
    '''

    # アクセストークンの取得
    token = get_access_token()
    # リポジトリーを検索するエンドポイントを指定する
    repo_stars_api_point = f'https://api.github.com/search/repositories?q=stars:>0&sort=stars&per_page=100&access_token={token}'
    # エンドポイントを引数にget_api_repos関数でスターが多いリポジトリ数のデータフレームを取得
    repos_df = get_api_repos(repo_stars_api_point)
    return repos_df


if __name__ == '__main__':
    main()
