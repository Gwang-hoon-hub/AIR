# import flask
# from flask import Flask, render_template, jsonify, request, Blueprint
# import re
# import pymongo
# from pymongo import MongoClient
# client = MongoClient('localhost', 27017)
# db = client.mini
#
# import jwt
#
#
# NAME = "home"
# bp = Blueprint(NAME, __name__, template_folder='templates', url_prefix="/api/home")
#
# # API
# # 검색
# @bp.route('/search_article')
# def keyword_search():
#     keyword = request.args.get('keyword')
#     print(keyword)
#     modified_all_articles = []
#
#     found_articles = list(db.articles.find({'$or': [{'album_singer':{'$regex': keyword}}, {'album_title':{'$regex': keyword}}]}))
#     print(found_articles)
#
#     for article in found_articles:
#         id = article['_id']
#
#         # 글쓴이의 이미지를 userDb에서 가져오기
#         writer_id = article['user_id']
#         writer_img = db.users.find_one({'user_id': writer_id}, {'user_img': 1})['user_img']
#         article['writer_img'] = writer_img
#
#         comments = list(db.comments.find({'article_id': id}, {'contents': 1, 'user_id': 1}).sort(
#             'post_date', pymongo.DESCENDING))
#         # print(comments)
#         if len(comments) != 0:
#             comment1 = comments[0]['contents']
#             commenter1_id = comments[0]['user_id']
#             commenter1_img = db.users.find_one({'user_id': commenter1_id}, {'user_img': 1})['user_img']
#             article['commenter1_img'] = commenter1_img
#             if len(comments) >= 2:
#                 comment2 = comments[1]['contents']
#                 commenter2_id = comments[1]['user_id']
#                 commenter2_img = db.users.find_one(
#                     {'user_id': commenter2_id}, {'user_img': 1})['user_img']
#                 article['commenter2_img'] = commenter2_img
#             else:
#                 comment2 = ""
#         else:
#             comment1 = ""
#             comment2 = ""
#
#         article['comment1'] = comment1
#         article['comment2'] = comment2
#         # print(comment1, comment2)
#         modified_all_articles.append(article)
#     # comments = db.comments.find({'article_id':})
#     return jsonify({'found_articles': modified_all_articles})
#     # return render_template('templates/index.html', results = found_articles)
#
# # 좋아요
# @bp.route('/like', methods=['POST'])
# def like():
#     clicked_article_id = request.form['article_id']
#
#     SECRET_KEY = '123'
#     access_token = request.cookies.get('access_token')
#     user_info = jwt.decode(access_token, SECRET_KEY, "HS256")
#     user_id = user_info['user_id']
#
#     liked_articles = list(db.users.find_one({'user_id':user_id},{'_id':0, 'liked_articles':1})['liked_articles'])
#     print(f"기존 좋아요 리스트 : {liked_articles}")
#
#     for article_id in liked_articles:
#         if article_id == clicked_article_id:
#             return jsonify({'message': '이미 좋아요한 글입니다'})
#
#     # 아티클 디비에서 좋아요 수 +1
#     target_like = db.articles.find_one({'_id':clicked_article_id}, {'like':1})['like']
#     target_like += 1
#     db.articles.update_one({'_id':clicked_article_id}, {'$set': {'like': target_like}})
#
#     # 유저 디비에서 좋아요한 아티클 리스트에 추가
#     liked_articles.append(clicked_article_id)
#     db.users.update_one({'user_id':user_id}, {'$set': {'liked_articles': liked_articles}})
#
#     return jsonify({'message': '좋아요 완료!'})
#
# # 단일 아티클 팝업창에 데이터 담기
