# 必要なモジュールのimport
import datetime
from os import replace
import pandas as pd
import tweepy
# 形態素解析をするためのjanomeをimport
from janome.tokenizer import Tokenizer
# pandas
# 各種ツイッターのキーをセット　consumer_key, consumer_secret, access_key, access_secret
consumer_key = "B925YvNgSiiG6odErMBCO3mDk"
consumer_secret = "AfKI707H8eB7CYO2DBxmSd8EskdJj3LWMek1PKaDkVk40qbB3c"
access_key = "1206923034830860289-F0uZXitPOy6YUNT9Amar1uw6Q93OdI"
access_secret = "vbW3ViVYrqukWZ24OVl8AwyL22nYQ9g8g31HmWM18pvJb"

# 認証のためのAPIキーをセット
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

# API利用制限にかかった場合、解除まで待機する


def main():
    '''
    メインの実行部分
    ツイートデータの取得からデータの出力まで
    '''
    # ツイートデータの取得 日付の指定は 2020-7-30のみでもOK,
    # 日本時間で取得したい場合は2020-7-30_00:00:00_JSTのように指定
    # JSTをつけないと時間がUTCになる UTCは協定世界時間-> JST＋9:00(日本時間よりも9時間進んでいる)
    tweet_data = get_search_tweet('Python',
                                  '2021-03-01_00:00:00_JST',
                                  '2021-03-03_00:00:00_JST',
                                  100, 1)
    # ツイートデータを番号順に出力
    out_put_tweets(tweet_data)
    # ツイートデータをDataframeにする
    df = make_df(tweet_data)
    posi_nega_check(df)
    # ツイートデータのCSVへの出力
    df.to_csv('tweet_data.csv', encoding='utf-8-sig')


# ツイートを収集する関数
def get_search_tweet(search, since, until, count, rlcount):
    '''
    ツイート情報を特定のキーワードで、期間を指定して収集
    取得できるデータは1週間以内のデータだけ
    リツイート数＋いいね数の合計でツイートを絞り込める
    '''

    # 検索キーワードの設定、 リツイートは除く
    searchkey = search + '-filter:retweets'
    # ツイートデータ取得部分
    # tweepy.CursorのAPIのキーワードサーチを使用(api.search)

    # untilがいつまで, tweet_modeでつぶやきの省略ありなし, langで言語
    # .items(数)と書いてツイート数を指定
    # qがキーワード, sinceがいつから
    tweets = tweepy.Cursor(api.search, q=searchkey, since=since,
                           until=until, tweet_mode="extended", lang='ja'
                           ).items(count)
    # ツイートのデータを取り出して、リストにまとめていく部分
    # ツイートデータを入れる空のリストを用意
    tweet_data = []
    for tweet in tweets:
        # いいねとリツイートの合計がrlcuont以上の条件
        if tweet.retweet_count + tweet.favorite_count >= rlcount:
            # 空のリストにユーザーネーム、スクリーンネーム、RT数、いいね数、日付などを入れる
            tweet_data.append([tweet.user.name, tweet.user.screen_name,
                               tweet.retweet_count, tweet.favorite_count,
                               tweet.created_at.strftime("%Y-%m-%d-%H:%M:%S"),
                               tweet.full_text.replace('\n', '')])
    return tweet_data


def out_put_tweets(tweet_data):
    '''
    ツイートのリストを順番をつけて出力する関数の作成
    '''
    i = 1
    for tweet in tweet_data:
        print(f'{i}番目のつぶやき{tweet}')
        i += 1


def make_df(tweet_data):
    '''
    ツイートデータからDataFrameを作成する
    '''

    # データを入れる空のリストを用意(ユーザー名、ユーザーid、RT数、いいね数、日付け、ツイート本文)
    list_username = []
    list_userid = []
    list_rtcount = []
    list_favorite = []
    list_date = []
    list_text = []
    i = 0
    # ツイートデータからユーザー名、ユーザーid、RT数、いいね数、日付け、ツイート本文のそれぞれをデータごとにまとめたリストを作る
    for i in range(len(tweet_data)):
        list_username.append(tweet_data[i][0])
        list_userid.append(tweet_data[i][1])
        list_rtcount.append(tweet_data[i][2])
        list_favorite.append(tweet_data[i][3])
        list_date.append(tweet_data[i][4])
        list_text.append(tweet_data[i][5])
        i += 1
    # 先ほど作ったデータごとにまとめたリストからDataframeの作成
    df = pd.DataFrame({'ユーザー名': list_username,
                       'ユーザーID': list_userid,
                       'リツイート数': list_rtcount,
                       'いいね数': list_favorite,
                       '日時': list_date,
                       '本文': list_text})

    print(df)
    return df


def posi_nega_check(df):
    '''
    データフレームを引数に受け取り、
    ネガポジ分析をする関数
    '''
    # 極性辞書をPythonの辞書にしていく
    np_dic = {}

    with open("pn.csv.m3.120408.trim", "r", encoding="utf-8")as f:
        # 日本語評価極性辞書のファイルの読み込み
        lines = [line.replace('\n', '').split('\t') for line in f.readlines()]
        # 1行1行を読み込み、文字列からリスト化。リストの内包表記の形に

    posi_nega_df = pd.DataFrame(lines, columns=['word', 'score', 'explain'])
    # リストからデータフレームの作成
    np_dic = dict(zip(posi_nega_df['word'], posi_nega_df['score']))
    # データフレームの2つの列から辞書の作成　zip関数を使う

    # 形態素解析をするために必要な記述を書いていく
    tokenizer = Tokenizer()
    # ツイート一つ一つを入れてあるデータフレームの列（本文の列）をsentensesと置く
    sentences = df['本文']
    # p,n,e,?p?nを数えるための辞書を作成
    result = {'p': 0, 'n': 0, '?p?n': 0}

    for sentence in sentences:  # ツイートを一つ一つ取り出す
        for token in tokenizer.tokenize(sentence):  # 形態素解析をする部分
            word = token.surface  # ツイートに含まれる単語を抜き出す
            if word in np_dic:
                # 辞書のキーとして単語があるかどうかの存在確認
                value = np_dic[word]  # 値(pかnかeか?p?nのどれか)をvalueという文字で置く
                if value in result:  # キーの存在確認
                    result[value] = result[value] + 1  # p,n,e,?p?nの個数を数える
    # 総和を求める
    summary = result['p'] + result['n'] + result['?p?n']

    # ネガポジ度の平均（pの総数 / summary, nの総数 / summary）を数値でそれぞれ出力
    # summaryが0の場合もあるので、try-exceptで例外処理
    try:
        print('ポジティブ度:', result['p'] / summary)  # ポジティブ度の平均
        print('ネガティブ度:', result['n'] / summary)  # ネガティブ度の平均
    except ZeroDivisionError:
        print('summaryが0です。')
    # summaryが0の場合


if __name__ == '__main__':
    main()
