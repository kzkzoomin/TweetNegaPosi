import requests
import json
from requests_oauthlib import OAuth1Session
import ast
import os

# ログイン情報（ローカル確認用　デプロイ時にコメントアウト）
#import info_val
#CK = info_val.CK
#CKS = info_val.CKS
#AT = info_val.AT
#ATS = info_val.ATS
#subscription_key = info_val.subscription_key
#text_analytics_base_url = info_val.text_analytics_base_url
#sentiment_api_url = info_val.sentiment_api_url

# ログイン情報（公開用）
CK = os.environ["CK"]
CKS = os.environ["CKS"]
AT = os.environ["AT"]
ATS = os.environ["ATS"]
subscription_key = os.environ["subscription_key"]
text_analytics_base_url = os.environ["text_analytics_base_url"]
sentiment_api_url = text_analytics_base_url + "/text/analytics/v2.1/sentiment"

################################################################
# キーワード検索して投稿ごとのJSONのリストを取得
################################################################
def tweet_search(keyword):
    # 認証
    twitter = OAuth1Session(CK, CKS, AT, ATS)
    # Twitter Endpoint(検索結果を取得する)
    url = 'https://api.twitter.com/1.1/search/tweets.json'
    
    params ={
            'count' : 100,      # 取得するtweet数
            'q'     : keyword  # 検索キーワード
            }
    
    # 取得したJSON格納用
    contents_list = []
    single_json_content_list = []
    
    req = twitter.get(url, params = params)
    if req.status_code == 200:
        res = json.loads(req.text)  # 取得内容をJSONで格納(Ch7-4のjson_dict)
        contents_list.append(res)
    else:
        print("Failed: %d" % req.status_code)    
    
    # JSONデータを個別の投稿に分ける
    for json_content in contents_list:
        for single_json_content in json_content['statuses']:
            single_json_content_list.append(single_json_content)  # 投稿を１つずつリストに格納
    
    return single_json_content_list

################################################################
# TextAnalyticsへの入力形式に変換
################################################################
def azure_json_transform(single_json_content_list):
    azure_json=''
    for single_json_for_azure in single_json_content_list:
        try:
            azure_json_single=str({
                'created_at':single_json_for_azure['created_at'],
                'id':single_json_for_azure['id'],
                'id_str':single_json_for_azure['id_str'],
                'text':single_json_for_azure['text'],
                'truncated':single_json_for_azure['truncated'],
                'entities':single_json_for_azure['entities'],
                'metadata':single_json_for_azure['metadata'],
                'source':single_json_for_azure['source'],
                'in_reply_to_status_id':single_json_for_azure['in_reply_to_status_id'],
                'in_reply_to_status_id_str':single_json_for_azure['in_reply_to_status_id_str'],
                'in_reply_to_user_id':single_json_for_azure['in_reply_to_user_id'],
                'in_reply_to_user_id_str':single_json_for_azure['in_reply_to_user_id_str'],
                'in_reply_to_screen_name':single_json_for_azure['in_reply_to_screen_name'],
                'user':single_json_for_azure['user'],
                'geo':single_json_for_azure['geo'],
                'coordinates':single_json_for_azure['coordinates'],
                'place':single_json_for_azure['place'],
                'contributors':single_json_for_azure['contributors'],
                'is_quote_status':single_json_for_azure['is_quote_status'],
                'retweet_count':single_json_for_azure['retweet_count'],
                'favorite_count':single_json_for_azure['favorite_count'],
                'favorited':single_json_for_azure['favorited'],
                'retweeted':single_json_for_azure['retweeted'],
                'language':single_json_for_azure['lang'],
                'tweet_url':'https://twitter.com/' + single_json_for_azure['user']['screen_name'] + '/status/' + single_json_for_azure['id_str']
            })
            azure_json +=azure_json_single+','
        
        except KeyError:
            azure_json_single=str({
                'created_at':single_json_for_azure['created_at'],
                'id':single_json_for_azure['id'],
                'id_str':single_json_for_azure['id_str'],
                'text':single_json_for_azure['text'],
                'truncated':single_json_for_azure['truncated'],
                'entities':single_json_for_azure['entities'],
                'metadata':single_json_for_azure['metadata'],
                'source':single_json_for_azure['source'],
                'in_reply_to_status_id':single_json_for_azure['in_reply_to_status_id'],
                'in_reply_to_status_id_str':single_json_for_azure['in_reply_to_status_id_str'],
                'in_reply_to_user_id':single_json_for_azure['in_reply_to_user_id'],
                'in_reply_to_user_id_str':single_json_for_azure['in_reply_to_user_id_str'],
                'in_reply_to_screen_name':single_json_for_azure['in_reply_to_screen_name'],
                'user':single_json_for_azure['user'],
                'geo':single_json_for_azure['geo'],
                'coordinates':single_json_for_azure['coordinates'],
                'place':single_json_for_azure['place'],
                'contributors':single_json_for_azure['contributors'],
                'is_quote_status':single_json_for_azure['is_quote_status'],
                'retweet_count':single_json_for_azure['retweet_count'],
                'favorite_count':single_json_for_azure['favorite_count'],
                'favorited':single_json_for_azure['favorited'],
                'retweeted':single_json_for_azure['retweeted'],
                'language':single_json_for_azure['lang'],
                'tweet_url':'https://twitter.com/' + single_json_for_azure['user']['screen_name'] + '/status/' + single_json_for_azure['id_str']
            })            
    # 最後だけカンマ抜く
    azure_json=azure_json[:-1]
    azure_json="{'documents':[" + azure_json + "]}"
    # str型をdictに変換
    azure_json=ast.literal_eval(azure_json)

    return azure_json

################################################################
    #取得したデータに、ネガポジをつけ、json形式で保存
    #保存の際はキャッシュ対策にcash_bastingを画面側で行う
################################################################
def nega_posi_azure(azure_json):
    global subscription_key
    global text_analytics_base_url
    #APIキー
    subscription_key = subscription_key
    assert subscription_key

    #APIのエンドポイントの基盤を入力する
    text_analytics_base_url = text_analytics_base_url

    #感情分析を行うAPIのエンドポイントをセット
    sentiment_api_url = text_analytics_base_url + "text/analytics/v2.1/sentiment"

    #ドキュメントのセンチメント スコアを0〜1 の間で取得（高いスコアは肯定的なセンチメントを示します。）
    headers   = {"Ocp-Apim-Subscription-Key": subscription_key}
    response  = requests.post(sentiment_api_url, headers=headers, json=azure_json)
    sentiments = response.json()

    #念のため、ID順に、azure_json['documents']とsentiments['documents']をソートする
    sentiments['documents'].sort(key=lambda x: x['id'], reverse=False)
    azure_json['documents'].sort(key=lambda x: x['id'], reverse=False)

    print(len(sentiments['documents']))
    print(len(azure_json['documents']))

    #azure_jsonにネガポジスコアを格納
    for num,sentiments_single in enumerate(sentiments['documents']):
        #print(azure_json['documents'][num])
        azure_json['documents'][num]['score']=sentiments['documents'][num]['score']
    
    return(azure_json)

################################################################
#azure apiのレスポンスを判定（azureの無料枠を超えていたら、200以外が返る）
################################################################
def nega_posi_azure_is_ok(azure_json):
    global subscription_key
    global text_analytics_base_url    
    #azure negaposi分析(まずは、free tierを超えてなないか確認)
    subscription_key = subscription_key
    assert subscription_key

    #APIのエンドポイントの基盤を入力する
    text_analytics_base_url = text_analytics_base_url

    #感情分析を行うAPIのエンドポイントをセット
    sentiment_api_url = text_analytics_base_url + "text/analytics/v2.1/sentiment"

    #ドキュメントのセンチメント スコアを0 ?1 の間で取得（高いスコアは肯定的なセンチメントを示します。）
    headers   = {"Ocp-Apim-Subscription-Key": subscription_key}
    response  = requests.post(sentiment_api_url, headers=headers, json=azure_json)
    return response