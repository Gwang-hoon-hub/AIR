import single_route
import home_route
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta

import pymongo
from flask import Flask, render_template, request, redirect, jsonify, url_for

app = Flask(__name__)

##########jwt -호준################################################

SECRET_KEY = '123'
app.config['SECRET_KEY'] = SECRET_KEY  # 임시 번호
app.config['BCRYPT_LEVEL'] = 10
bcrypt = Bcrypt(app)

#################################################################


# TODO EC2랑 연결된 mongoDb로 변경
client = MongoClient('localhost', 27017)
# client = MongoClient('mongodb://test:test@localhost', 27017)

db = client.mini

# 다른 API 경로들 파일 연결

app.register_blueprint(home_route.bp)
app.register_blueprint(single_route.bp)
# app.register_blueprint(post_route.bp)

# 이 조건을 달지 않으면, css같은 사항 변화를 12시간마다 체크한다. 즉 디버깅모드에서는 불편하므로, 디버깅시에는 1초로 변경하는 것.
if app.config['DEBUG']:
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1


# 메인 (+ all articles)
@app.route('/')
def home():
    modified_all_articles = []
    all_articles = list(db.articles.find().sort('like', pymongo.DESCENDING))
    # find 모든 doc의 모든 필드값 가져오는 것 find({},{})이게 왜 이 파일에서는 적용이 안 될까?  (이유 찾아보기!_정현)
    # 덕분에 find()도 작동한다는 걸 알게 되긴 했다.

    for article in all_articles:
        id = article['_id']

        # 글쓴이의 이미지를 userDb에서 가져오기
        writer_id = article['user_id']
        writer_img = db.users.find_one({'user_id': writer_id}, {'user_img': 1})['user_img']
        article['writer_img'] = writer_img

        comments = list(db.comments.find({'article_id': id}, {'contents': 1, 'user_id': 1}).sort(
            'post_date', pymongo.DESCENDING))
        print(comments)
        if len(comments) != 0:
            comment1 = comments[0]['contents']
            commenter1_id = comments[0]['user_id']
            commenter1_img = db.users.find_one(
                {'user_id': commenter1_id}, {'user_img': 1})['user_img']
            article['commenter1_img'] = commenter1_img
            if len(comments) >= 2:
                comment2 = comments[1]['contents']
                commenter2_id = comments[1]['user_id']
                commenter2_img = db.users.find_one(
                    {'user_id': commenter2_id}, {'user_img': 1})['user_img']
                article['commenter2_img'] = commenter2_img
            else:
                comment2 = ""
        else:
            comment1 = ""
            comment2 = ""

        article['comment1'] = comment1
        article['comment2'] = comment2
        print(comment1, comment2)
        modified_all_articles.append(article)

    return render_template('index.html', results=modified_all_articles)


#
###########로그인 추가 - 라우팅파일x -호준###########################################

@app.route('/login', methods=['POST', 'GET'])
def login():
    if (request.method == 'GET'):
        return render_template("login.html")

    elif (request.method == 'POST'):
        id = request.form['id']
        pw = request.form['pw']
        # pw_hash = bcrypt.generate_password_hash(pw);

        user = db.users.find_one({"user_id": id}, {'_id': False})

        if user is None:
            return jsonify({'result': 'fail', 'msg': '우리 회원이 아니다'})
        pw_hash = user['pwd']
        print(bcrypt.check_password_hash(pw_hash, pw))

        # 어떻게 게속 같은 결과를 리턴해줘 ? 내부 알고리즘 찾아보기 1234 리턴값 bool
        if bcrypt.check_password_hash(pw_hash, pw) is False:
            return jsonify({'result': 'fail', 'msg': '비밀번호가 일치하지  않습니다'})

        else:
            payload = {
                'user_id': id,
                'exp': datetime.utcnow() + timedelta(seconds=60)  # 1분
            }
            access_token = jwt.encode(payload, SECRET_KEY)  # Default: "HS256"

            print(access_token)
            return jsonify({"result": "success", "access_token": access_token})

    else:
        return jsonify({'result': '정의되지 않은 접근'})


############################################################################

############현재 로그인한 아이디가 필요한 경우에 요청  ################

@app.route('/api/get_id')
def get_id():
    access_token = request.cookies.get('access_token')

    print(f"get_id에서 토큰확인 {request.cookies.get('access_token')}")
    try:
        user_info = jwt.decode(access_token, SECRET_KEY, "HS256")
        print(user_info)

        return jsonify({'result': 'success', 'user_id': user_info['user_id']})

    except jwt.ExpiredSignatureError:
        print('로그인만료')
        msg = "로그인만료";

    except jwt.exceptions.DecodeError:
        print('디코딩에러/잘못된 정보')
        msg = "디코딩에러/잘못된 정보";

    except jwt.InvalidSignatureError:
        print('잘못된서명')
        msg = "잘못된서명"

    return jsonify({'result': 'fail', 'msg': msg})


###############마이페이지######################################################

@app.route('/mypage', methods=['POST', 'GET'])
def mypage():
    access_token = request.cookies.get('access_token')

    if (request.method == 'GET'):
        return check_token(access_token)


# 만약 권한이 있다면 render_template("mypage");
# 없다면 redirect("/login");


###############################################################################


###############r권한검증######################################################

def check_token(access_token):
    try:
        user_info = jwt.decode(access_token, SECRET_KEY, "HS256")
        print(user_info)
        articles = get_data(user_info['user_id'])

        return render_template("mypage.html", results=articles, user_id=user_info['user_id'])

    except jwt.ExpiredSignatureError:
        print('로그인만료')

    except jwt.exceptions.DecodeError:
        print('디코딩에러/잘못된 정보')

    except jwt.InvalidSignatureError:
        print('잘못된서명')

    return redirect(url_for("login"))


###############################################################################


##############데이터 처리 ####################################################
def get_data(user_id):
    articles = list(db.articles.find({'user_id': user_id}))
    comments = list(db.comments.find({'article_id': user_id}))
    return articles


# 아직 작성중
def make_doc(articles, comments):
    articles = list(db.articles.find({'user_id': "jun"}))
    comments = list(db.comments.find({'user_id': "jun"}))
    doc = []

    for article in articles:
        article_id = article['user_id']
        article_comment = []

        for comment in comments:
            if article_id == comment['article_id']:
                article_comment.insert(comment)
        doc.insert({"article": article, "comment": comment})


##########################################################################
# 한솔님 크롤링
from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
# driver = webdriver.Chrome(ChromeDriverManager().install())
import time

options = webdriver.ChromeOptions()
options.add_argument("headless") # 화면 띄우기 없음


@app.route('/api/post/preview', methods=['POST'])
def preview():
    url_receive = request.form['url_give']
    driver = webdriver.Chrome('./chromedriver')
    driver.implicitly_wait(1)
    url = url_receive
    driver.get(url)
    time.sleep(3)

    temp_title = ''
    temp_singer = ''

    for i in driver.find_elements_by_css_selector(
            '#content > div.summary_section > div.summary > div.text_area > h2 > span.title'):
        title = (i.text)
        temp_title = title

    for i in driver.find_elements_by_css_selector(
            '#content > div.summary_section > div.summary > div.text_area > h2 > span.sub_title > span:nth-child(2) > span > a > span'):
        singer = (i.text)
        temp_singer = singer

    temp_img = driver.find_element_by_css_selector("#content > div.summary_section > div.summary_thumb > img").get_attribute(
        'src')

    return jsonify({'img': temp_img, 'title':temp_title, 'singer':temp_singer})

@app.route('/api/post/post_article', methods=['POST'])
def post_article():
    url_receive = request.form['url_give']
    desc_receive = request.form['desc_give']
    #user_id_receive = request.form['user_id_give']


    driver = webdriver.Chrome('./chromedriver')
    driver.implicitly_wait(1)
    url = url_receive
    driver.get(url)
    time.sleep(3)

    temp_title = ''
    temp_singer = ''

    for i in driver.find_elements_by_css_selector(
            '#content > div.summary_section > div.summary > div.text_area > h2 > span.title'):
        title = (i.text)
        temp_title = title

    for i in driver.find_elements_by_css_selector(
            '#content > div.summary_section > div.summary > div.text_area > h2 > span.sub_title > span:nth-child(2) > span > a > span'):
        singer = (i.text)
        temp_singer = singer

    temp_img = driver.find_element_by_css_selector(
        "#content > div.summary_section > div.summary_thumb > img").get_attribute(
        'src')

    doc = {
        'url' : url_receive,
        'description' : desc_receive,
        'img' : temp_img,
        'title':temp_title,
        'singer':temp_singer
        #'user_id' : user_id_receive
    }

    db.Article.insert_one(doc)

    return jsonify({'msg':'포스팅 완료'})



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5008, debug=True)
