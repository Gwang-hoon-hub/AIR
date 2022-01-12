# import flask
# from flask import Flask, render_template, jsonify, request, Blueprint
# import re
# import pymongo
# from pymongo import MongoClient
# client = MongoClient('localhost', 27017)
# db = client.mini

# NAME = "single"
# bp = Blueprint(NAME, __name__, template_folder='templates', url_prefix="/api/single")


# # 댓글작성 (POST) API


# @bp.route('/post_comment', methods=['POST'])
# def post_comment():
#     comment_receive = request.form['comment_give']
#     today_receive = request.form['date_give']
#     # userId_receive = request.form['userID_give']
# # # 유저의 아이디와 이름을 어떻게 가져와야 할지 몰라서 doc에 유저이름이 없습니다! - 연습하고 있는거에는 id를 던지고 있는데 해당 프로젝트에서는 아직 안되서...
# #     doc = {
# #         '_id'
# #         'contents': comment_receive,
# #         'post_date': today_receive,
# #         'commenter_id': userId_receive
# #     }
# #     db.comments.insert_one(doc)

#     print(comment_receive, today_receive)
#     return jsonify({'result': 'success', 'msg': '댓글 저장 route 연결!'})

# # # 유저체크하기
# # @bp.route('/api/single/check_user', methods=['GET'])
# # def checkUser():
# #
# #     user = db.users.find_one({'name': 'bobby'})
# #
# #     title_receive = request.form['title_give']
# #     db.prac12.update_one({'title': title_receive})
# #
# #     # db.users.update_one({'name': 'bobby'}, {'$set': {'age': 19}})
# #
# #     return jsonify({'msg': '수정완료!'})

# # 댓글수정
# @bp.route('/update_comment', methods=['POST'])
# def update_comment():

#     title_receive = request.form['title_give']
#     db.prac12.update_one({'title': title_receive})

#     # db.users.update_one({'name': 'bobby'}, {'$set': {'age': 19}})

#     return jsonify({'msg': '수정완료!'})

# # 댓글삭제
# @bp.route('/delete_comment', methods=['POST'])
# def delete_comment():
#     title_receive = request.form['title_give']
#     # db.prac12.delete_one({'title': title_receive})

#     return jsonify({'msg': '삭제완료!'})