from routes import home_route, single_route, post_route
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
import jwt
import uuid
from datetime import datetime, timedelta
import pymongo
from flask import Flask, render_template, request, redirect, jsonify, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import os 


app = Flask(__name__)

##########jwt -호준################################################

SECRET_KEY = '123'
app.config['SECRET_KEY'] = SECRET_KEY  # 임시 번호
app.config['BCRYPT_LEVEL'] = 10
bcrypt = Bcrypt(app)

#################################################################


# TODO EC2랑 연결된 mongoDb로 변경
client = MongoClient('mongodb://test:test@52.79.250.33', 27017)


db = client.mini

# 다른 API 경로들 파일 연결

app.register_blueprint(home_route.bp)
#app.register_blueprint(single_route.bp)
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
        # print(bcrypt.check_password_hash(pw_hash, pw))

        # 어떻게 게속 같은 결과를 리턴해줘 ? 내부 알고리즘 찾아보기 1234 리턴값 bool
        if bcrypt.check_password_hash(pw_hash, pw) is False:
            return jsonify({'result': 'fail', 'msg': '비밀번호가 일치하지  않습니다'})

        else:
            payload = {
                'user_id': id,
                'exp': datetime.utcnow() + timedelta(seconds=600)  # 1분
            }
            access_token = jwt.encode(payload, SECRET_KEY)  # Default: "HS256"

            # print(access_token)
            return jsonify({"result": "success", "access_token": access_token})

    else:
        return jsonify({'result': '정의되지 않은 접근'})





############################################################################


############현재 로그인한 아이디가 필요한 경우에 요청  ################

@app.route('/api/get_id')
def get_id():
    access_token = request.cookies.get('access_token')

    # print(f"get_id에서 토큰확인 {request.cookies.get('access_token')}")
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

@app.route('/mypage/delete')
def delete():
    article_id = request.args.get('article_id')
    db.articles.delete_one({'_id':article_id})
    return jsonify({'msg':'삭제완료!'})
###############################################################################


###############r권한검증######################################################

def check_token(access_token):
    try:
        user_info = jwt.decode(access_token, SECRET_KEY, "HS256")
        articles = get_data(user_info['user_id'])

        user_img = db.users.find_one({'user_id':user_info['user_id']},{'user_img':1})['user_img']
        user_introduce = db.users.find_one({'user_id':user_info['user_id']},{'introduce':1})['introduce']


        return render_template("mypage.html", results=articles, user_id=user_info['user_id'], user_img=user_img, user_introduce=user_introduce)

    except jwt.ExpiredSignatureError:
        print('로그인만료')

    except jwt.exceptions.DecodeError:
        print('디코딩에러/잘못된 정보')

    except jwt.InvalidSignatureError:
        print('잘못된서명')

    return redirect(url_for("login"))


###############################################################################


#########회원가입 추가 #########################################################
@app.route('/register',methods=['GET' ,'POST'] )
def register():
    if(request.method == 'GET'):
        return render_template("register.html")


    elif (request.method == 'POST'):
         #postman 같은걸로 보내면 회원가입이 가능함 > 서버에서도 정규식 검사가 필요한듯 ? 일단 생략 
         input_id= request.form['user_id']
         result =list(db.users.find({'user_id' : input_id}))

         if (len(result)!=0):
            return jsonify({'result':'fail' ,'msg':'중복된 아이디입니다'})


         input_pw= request.form['pwd']
         hashpw=bcrypt.generate_password_hash(input_pw);

         user_img= request.form['user_img']
         introduce = request.form['introduce']
    
         user = {
             "_id" : uuid.uuid4().hex,
             "user_id":input_id,
             "pwd":hashpw,
             'user_img':"none",
             'introduce':"none",
         }

         db.users.insert_one(user);
         return jsonify({'result':'success'})
         

@app.route('/api/check_id',methods=['POST'])
def check_id():
    input_id=request.values.get("input_id")
    user = list(db.users.find({'user_id' : input_id}))
    print(user);
    if(user == [] ):
        return jsonify({'result':'success'})
    else:
        return jsonify({'resuly': 'fail'}) 


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

    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    driver = webdriver.Chrome('./chromedriver', options=options)
    driver.implicitly_wait(1)
    url = url_receive
    driver.get(url)
    time.sleep(3)

    temp_title = ''
    temp_singer = ''


    for i in driver.find_elements_by_css_selector(
            '#content > div.summary_section > div.summary > div.text_area > h2 > span.title'):
        title = (i.text)
        temp_title = title[3:]

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

    options = webdriver.ChromeOptions()
    options.add_argument("headless")


    driver = webdriver.Chrome('./chromedriver', options=options)
    driver.implicitly_wait(1)
    url = url_receive
    driver.get(url)
    time.sleep(3)

    temp_title = ''
    temp_singer = ''

    for i in driver.find_elements_by_css_selector(
            '#content > div.summary_section > div.summary > div.text_area > h2 > span.title'):
        title = (i.text)
        temp_title = title[3:]

    for i in driver.find_elements_by_css_selector(
            '#content > div.summary_section > div.summary > div.text_area > h2 > span.sub_title > span:nth-child(2) > span > a > span'):
        singer = (i.text)
        temp_singer = singer

    temp_img = driver.find_element_by_css_selector(
        "#content > div.summary_section > div.summary_thumb > img").get_attribute(
        'src')

    # 현재 로그인한 사용자의 아이디 가져오기
    # SECRET_KEY = '123'
    access_token = request.cookies.get('access_token')
    user_info = jwt.decode(access_token, SECRET_KEY, "HS256")
    user_id = user_info['user_id']


    # 날짜 가져오기
    time_now = datetime.now()
    now_text = time_now.strftime("%Y{} %m{} %d{} %H{} %M{}")
    now_text = now_text.format('년', '월', '일', '시', '분')

    # 아티클 doc 생성
    #todo 회원가입시 이름도 받는다면, 토큰에서 찾은 id를 가지고 userDB에서 이름도 찾아올 수 있을 것.
    doc = {
        "_id": uuid.uuid4().hex,
        "user_id": user_id,
        # "writer_name": user_nick,
        'article_url' : url_receive,
        'article_description' : desc_receive,
        'album_image' : temp_img,
        'album_title':temp_title,
        'album_singer':temp_singer,
        'post_date': now_text,
        'like':0
        #'user_id' : user_id_receive
    }

    db.articles.insert_one(doc)

    return jsonify({'msg':'포스팅 완료'})



###########광훈님 ###################################
@app.route('/api/single')
def single():
   
    article_id =request.args.get("article_id")
    comments = list(db.comments.find({'article_id':article_id}))
    article = list( db.articles.find( {'_id':article_id}))[0]

    if len(comments) != 0:
        comments_res = comments
    else:
        comments_res = [{'user_id':"인에어팟", 'contents':"아직 댓글이 없어요~ 첫 댓글을 달아주세요~"}]

    # return jsonify({'all_comments': comments})
   # return render_template("index.html", comment_give=comments, articles_give=article)
    return jsonify({'comments':comments_res , 'article': article })

# 카드 클릭 시 단일 게시물 보여주기





# 댓글작성 (POST) API
@app.route('/api/single/post_comment', methods=['POST'])
def post_comment():
    comment_receive = request.form['comment_give']
    today_receive = request.form['date_give']

    # userid_receive = request.form['user_id']
    # 현재 로그인한 사용자의 아이디 가져오기
    # SECRET_KEY = '123'
    access_token = request.cookies.get('access_token')
    user_info = jwt.decode(access_token, SECRET_KEY, "HS256")
    user_id = user_info['user_id']
    article_id = request.form['article_id']

    # 날짜 가져오기
    time_now = datetime.now()
    now_text = time_now.strftime("%Y{} %m{} %d{} %H{} %M{}")
    now_text = now_text.format('년', '월', '일', '시', '분')

    doc = {
        '_id': uuid.uuid4().hex,
        'contents': comment_receive,
        'post_date': now_text,
        'user_id': user_id,
        'article_id': article_id,
        'commenter_name': "임시"
    }
    print(doc);
    db.comments.insert_one(doc)

    return jsonify({'result': 'success', 'msg': '저장 완료!'})



# 카드 클릭 시 단일 게시물 보여주기

# # 댓글리스트로 보여주기
# @app.route('/api/single/showComment', methods=['GET'])
# def listing():
#     comments = list(db.comments.find({    },{'_id':False}))

#     return jsonify({'all_comments':comments})

#댓글



# 댓글수정
@app.route('/api/single/update_comment', methods=['POST'])
def update_comment():
    comment_id = request.form['comment_id']
    update_comment = request.form['updateComment_give']
    updateDate_receive = request.form['updateDate_give']

    db.comments.update_one({'_id': comment_id}, {'$set': {'comment': update_comment,
    'updateDate':updateDate_receive}})

    # db.users.update_one({'name': 'bobby'}, {'$set': {'age': 19}})

    return jsonify({'result': 'success', 'msg': '수정완료!'})

# 댓글삭제
@app.route('/api/single/delete_comment', methods=['POST'])
def delete_comment():
    userID_receive = request.form['userID_give']
    print(userID_receive)
    db.prac12.delete_one({'userID': userID_receive})

    return jsonify({'result': 'success','msg': '삭제완료!'})



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5008, debug=True)