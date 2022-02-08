# 必要なモジュールのimport
import pandas as pd
import tweepy
# 各種ツイッターのキーをセット
# 各種ツイッターのキーをセット　consumer_key, consumer_secret, access_key, access_secret
consumer_key = ""
consumer_secret = ""
access_key = ""
access_secret = ""
# 認証のためのAPIキーをセット
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)  # API利用制限にかかった場合、解除まで待機する


def main():
    '''
        メインの実行部分
        '''

    # 調べる言語のリストの用意
    languages = ["JavaScript", "Python", "TypeScript", "Java", "C++", "Go",
                 "Rust", "C", "Shell", "Vue", "Dart", "CSS", "C#", "PHP",
                 "Clojure", "Assembly", "Ruby"]
    like = []
    # for文を使ってリストに入っている言語ごとにデータを取得していく 取得するデータは今日から過去7日以内
    for language in languages:
        tweet_data = get_search_tw(language, '2021-03-20_00:00:00_JST',
                                   '2021-03-21_00:00:00_JST', 1, 50)
        # 取得したデータからデータフレームを作成
        df = make_df(tweet_data)
        # いいね数の総和を求めてリストに追加
        like.append(df['いいね数'].sum())
        # 言語ごとのいいね数を出力する
        print(f'{language}の合計いいね数は{df["いいね数"].sum()}')
        # 言語名といいね数の情報からデータフレームを作成する
    df = pd.DataFrame({'言語': languages, 'いいね数': like})
    # いいね数の多い順にデータを並べ変える
    print('結果')
    print(df.sort_values(by='いいね数', ascending=False))
    # 期間を指定して、ツイートを収集する関数


def get_search_tw(search, since, until, recount, count):
    '''
        今日から過去7日間の期間を指定して、ツイートを収集する関数
        ツイートのデータをapi.searchを使って収集
        '''

    # 検索キーワード。 リツイートは除く
    searchkey = search + '-filter:retweets'
    # ツイート取得
    # APIのtweepy.Cursorのキーワードサーチ(api.search)を使う
    tweets = tweepy.Cursor(api.search, q=searchkey, since=since,
                           until=until, tweet_mode="extended", lang='ja'
                           ).items(count)
    # ツイートデータを入れる空のリストを用意
    tweet_data = []
    # いいねとリツイートの合計がrecuont以上なら次からの処理をする
    for tweet in tweets:
        if tweet.retweet_count + tweet.favorite_count >= recount:
            tweet_data.append([search, tweet.favorite_count])
    return tweet_data


'''
    ツイートデータを番号と共に出力
    '''


def make_df(tweet_data):
    '''
        ツイートのデータからデータフレームを作成
        '''

    # 各ツイートデータを入れるための空のリストを用意
    list_language = []
    list_favorite = []
    i = 0
    # ツイートの各アイテムを入れるリストを作成
    for i in range(len(tweet_data)):
        list_language.append(tweet_data[i][0])
        list_favorite.append(tweet_data[i][1])
        i += 1
    # 上で作成したリストからツイートを入れるデータフレームの作成
    df = pd.DataFrame({'言語': list_language, 'いいね数': list_favorite})
    return df


# 実行部分
if __name__ == '__main__':
    main()
