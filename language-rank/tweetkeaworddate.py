import datetime
import pandas as pd
import tweepy

def main():
    '''
    メインの実行部分
    '''
    api = set_tweet_oauth()
    # yesterday =  datetime.date.today() - datetime.timedelta(1)
    today = datetime.date.today()
    
    # 調べる言語のリストの用意
    languages = ["JavaScript","Python","TypeScript","Java","C++","Go","Rust","C","Shell","Vue","Dart","CSS","PHP","C#","Clojure","Assembly","Ruby"]
    like_sum = []

    # for文を使ってリストに入っている言語ごとにデータを取得していく
    for language in languages:
        print(f'{language}を調査中')
        data = get_tweet(api, language, 1000, 1, '2020-08-01_00:00:00_JST', today.strftime('%Y-%m-%d_00:00:00_JST'))
        
        # 取得したデータからデータフレームを作成
        df = make_df(data)
        # いいね数の総和を求めてリストに追加
        like_sum.append(df['いいね数'].sum())
        # 言語ごとのいいね数を出力する
        print(f'{language}の総いいね数は{df["いいね数"].sum()}')
    # 言語名といいね数の情報からデータフレームを作成する
    df = pd.DataFrame({'言語名': languages,
                       'いいね数': like_sum})
    print("集計結果")
    # いいね数の多い順にデータを並べ変える
    print(df.sort_values(by = 'いいね数', ascending=False))

def set_tweet_oauth():
# 各種ツイッターのキーをセット
    consumer_key = "*************************************"
    consumer_secret = "*************************************"
    access_key = "*************************************"
    access_secret = "*************************************"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)  # API利用制限にかかった場合、解除まで待機する
    return api

# ツイートを収集する関数
def get_tweet(api, s, items_count, recount, since, until):
    '''
    今日から過去7日間の期間を指定して、ツイートを収集する関数
    ツイートのデータをapi.searchを使って収集
    '''

    searchkey = s + '-filter:retweets'  # 検索キーワード。 リツイートは除く

    # ツイート取得
    tweet_data = []  # ツイートデータを入れる空のリストを用意
    # APIのtweepy.Cursorのキーワードサーチ(api.search)を使う
    tweets = tweepy.Cursor(api.search, q=searchkey, since=since, until=until, exclude_replies=True, tweet_mode='extended', lang='ja').items(items_count)
    
    for tweet in tweets:
        if tweet.favorite_count + tweet.retweet_count >= recount:  # いいねとリツイートの合計がrecuont以上なら
            tweet_data.append([tweet.user.name, tweet.user.screen_name, tweet.retweet_count,
                               tweet.favorite_count, tweet.created_at.strftime('%Y-%m-%d-%H:%M:%S_JST'), tweet.full_text.replace('\n', '')])
    return tweet_data

def oup_put_tweets(tweetdata):
    '''
    ツイートデータを番号と共に出力
    '''
    for i in range(len(tweetdata)):
        print(str(i) + '番目' + str(tweetdata[i]))
        
def make_df(data):
    """
    ツイートのデータからデータフレームを作成
    """    
    
    # 各ツイートデータを入れるための空のリストを用意
    list_username = []
    list_userid = []
    list_rtcount = []
    list_favorite = []
    list_date = []
    list_text = []

    # ツイートの各アイテムを入れるリストを作成
    for i in range(len(data)):
        list_username.append(data[i][0])
        list_userid.append(data[i][1])
        list_rtcount.append(data[i][2])
        list_favorite.append(data[i][3])
        list_date.append(data[i][4])
        list_text.append(data[i][5])
        
    # 上で作成したリストからツイートを入れるデータフレームの作成
    df = pd.DataFrame({'ユーザー名': list_username,
                       'ユーザーid': list_userid,
                       'RT数': list_rtcount,
                       'いいね数': list_favorite,
                       '日時': list_date,
                       '本文': list_text})
    return df
    
# 実行部分
if __name__ == '__main__':
    main()

    
