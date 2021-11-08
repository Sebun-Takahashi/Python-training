# プログラム終了のためのsysのimport
import sys
# 正規表現を使うためのreをimport
import re
# HTTPリクエストを送るためのrequestsをimport
import requests
# BeautifulSoupをimport
from bs4 import BeautifulSoup
# URLからドメインを取得する為にurlparseをimport
from urllib.parse import urlparse
# ネットワーク図を作成する為にnetworkxをimport
import networkx as nx
# ネットワーク図を描画する為にmatplotlibをimport
import matplotlib.pyplot as plt


def main():
    """
    メインの実行部分:調べたいURLはanl_urlに入力する
    """

    # 空のセットを用意
    pages = set()
    # 内部リンクを調べたいURL
    anl_url = 'https://hashikake.com/import'
    # https://またはhttp://からはじまる基準のホームページのURL
    match_url = re.match(r'https?://.*?/', anl_url)
    # match_urlはマッチオブジェクトなので、そこからURLだけを取り出す
    base_url = match_url.group()
    # 正規表現で使うためにドメイン名の取得
    base_domain = urlparse(anl_url).netloc
    # 内部リンクの取得
    innerlinks = get_links(base_url, base_domain, anl_url, pages)
    # 内部リンクが存在するなら
    if innerlinks:
        print(f'内部リンクは全部で{len(innerlinks)}個あります')
        # 内部リンクの数を表示
        print(innerlinks)  # 内部リンクの表示
        # 関数内で使われるshort_linksを定義
        short_links = shape_url(innerlinks, base_url, base_domain)
        # 内部リンクとして価値の薄いものの除外
        print(f'価値の高い内部リンクは全部で{len(short_links)}個あります')
        show_network(short_links)
        print(short_links)
        # 内部リンクとして価値が高いものの数を表示
    else:  # 内部リンクが存在しない場合はプログラムの終了
        print('内部リンクを取得できませんでした')
        sys.exit()


def get_links(base_url, base_domain, anl_url, pages):
    """
    /で始まるものと、base_urlから始まるもの//ドメインから始まるもの
    全ての内部リンクを取得して、重複を除去してpagesに収集する＋
    内部リンク数を出力
    """

    # 正規表現の中で変数を使う時はf文字列またはformatを使う
    pattern = rf"^{base_url}.*|^/[^/].*|^//{base_domain}.*"
    # /で始まって//を含まないURLと、https://ドメインから始まるもの、//ドメインから始まるもの
    response = requests.get(anl_url)  # URLにGETリクエストを送る
    # BeautifulSoupによるsoupの作成
    soup = BeautifulSoup(response.content, 'html.parser')
    # URLがパターンに一致するaタグを取得
    for link in soup.find_all('a', href=re.compile(pattern)):
        # re.compileによる正規表現パターンの生成
        link.get('href')  # aタグの中からURLを取得
        if link.get('href') not in pages:
            # セットの中にリンクが入っていないことを確認
            pages.add(link.get('href'))
            # セットの中に内部リンクとして追加
    return pages


def show_network(pages):
    """
    調査URLを中心としたネットワーク図の作成
    """
    # セットをリストにする
    pages = list(pages)
    # indexの0に文字列"start_url"を追加
    pages.insert(0, "start_url")
    # 空のグラフの作成　有向グラフ
    G = nx.DiGraph()
    # リストの最初の要素を中心として放射状に頂点と辺の追加
    nx.add_star(G, pages)
    # レイアウトを決める スプリングレイアウト
    pos = nx.spring_layout(G, k=0.3)
    # ノードの様式の決定
    nx.draw_networkx_nodes(G, pos, node_size=300, node_color='c', alpha=0.6)
    # ラベル文字の様式の決定
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='DejaVu Sans')
    # エッジの様式の決定
    nx.draw_networkx_edges(G, pos, alpha=0.4, edge_color='c')
    # nx.draw_networkx(G, pos)

    # matplotlibの座標軸の非表示
    plt.axis('off')
    # matplotlibによる図の描画
    plt.show()


def shape_url(pages, base_url, base_domain):
    """
    URLのhttp://を省略してネットワーク図を見やすくするための調整
    privacyページやcontactページなどの無駄な内部リンクページの除去
    """
    short_links = []
    # 内部リンクのURLから効果の薄い内部リンクをre.sub()で消していく
    # base_url https://hashikake.com //hashikake.com
    for url in pages:
        rel_path = re.sub(
            rf"^{base_url}|//{base_domain}|.*tag.*|.*feed.*|.*about.*", "", url)
    # short_links（空のリスト）に追加
        short_links.append(rel_path)
    # short_linksをセットに変更(重複の削除)
        s_links = set(short_links)
    # ""を削除　# discardだとキーがなくてもエラーにはならない。removeだとエラーになる
        s_links.discard('')
    return s_links


if __name__ == '__main__':
    main()
