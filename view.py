from flask import Flask, render_template, request, redirect, url_for

# Herokuの環境変数読み込み
import os
# ステータス判定
import requests

# ツイート検索・感情分析
import azure_negaposi_function

# ソート時のJSONリストの処理
import ast

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

app = Flask(__name__)

# ソート用（フォームから値を受け取る）
def request_form_azure_json():
    POSTS = request.form['tweets']
    keyword = request.args.get('search_word')
    
    return POSTS,keyword

#トップページ
@app.route('/')
def index():
    return render_template('index.html')

# フォーム入力
@app.route('/post', methods=['POST'])
def post():
    keyword = str(request.form['search_word'])
    single_json_content_list = azure_negaposi_function.tweet_search(keyword)
    azure_json=azure_negaposi_function.azure_json_transform(single_json_content_list)

    #azure apiのレスポンスを判定（azureの無料枠を超えていたら、200以外が返る）
    response=azure_negaposi_function.nega_posi_azure_is_ok(azure_json)
    if(response.status_code is not requests.codes.ok):
        return render_template('index.html')
    else:
        # 200だったらネガポジ判定
        negaposi_azure_json=azure_negaposi_function.nega_posi_azure(azure_json)
        return render_template('result.html',azure_json=negaposi_azure_json['documents'],search_word=keyword)

# いいね順ソート
@app.route('/post_good', methods=['POST'])
def post_good():
    POSTS, keyword = request_form_azure_json()
    azure_json = ast.literal_eval(POSTS)
    HASHTAG_POSTS_GOOD=True

    return render_template('result.html',HASHTAG_POSTS_GOOD=HASHTAG_POSTS_GOOD,azure_json=azure_json, search_word=keyword)

# ネガティブ順ソート
@app.route('/post_nega', methods=['POST'])
def post_nega():
    POSTS, keyword = request_form_azure_json()
    azure_json = ast.literal_eval(POSTS)
    HASHTAG_POSTS_NEGA=True

    return render_template('result.html',HASHTAG_POSTS_NEGA=HASHTAG_POSTS_NEGA,azure_json=azure_json, search_word=keyword)

# ポジティブ順ソート
@app.route('/post_posi', methods=['POST'])
def post_posi():
    POSTS, keyword = request_form_azure_json()
    azure_json = ast.literal_eval(POSTS)
    HASHTAG_POSTS_POSI=True

    return render_template('result.html',HASHTAG_POSTS_POSI=HASHTAG_POSTS_POSI,azure_json=azure_json, search_word=keyword)

# RT数順ソート
@app.route('/post_RT', methods=['POST'])
def post_RT():
    POSTS, keyword = request_form_azure_json()
    azure_json = ast.literal_eval(POSTS)
    HASHTAG_POSTS_RT=True

    return render_template('result.html',HASHTAG_POSTS_RT=HASHTAG_POSTS_RT,azure_json=azure_json, search_word=keyword)
    

if __name__ == '__main__':
    #app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    #app.jinja_env.filters['debug']=debug

    # debugモード/どこからでもアクセス可能に
    app.run(debug=True, host='0.0.0.0') 