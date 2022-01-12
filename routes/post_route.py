# dimport flask
# from flask import Flask, render_template, jsonify, request, Blueprint
# import re
# import pymongo
# from pymongo import MongoClient
# client = MongoClient('localhost', 27017)
# db = client.mini
#
#
# import requests
# from bs4 import BeautifulSoup
#
# NAME = "post"
# bp = Blueprint(NAME, __name__, template_folder='templates', url_prefix="/api/post")
#
# @bp.route('/preview', methods=['POST'])
# def preview():
#     url = request.form['url_give']
#     # res = requests.get(url)
#     # soup = BeautifulSoup(res.text, 'html.parser')
#     #
#     # title = soup.select_one('#main_pack > div.sc_new.cs_common_module._au_music_content_wrap.case_empasis.color_7 > div.cm_top_wrap._sticky._custom_select._header > div.title_area.type_keep._title_area > h2 > span > strong')
#     # singer = soup.select_one('#main_pack > div.sc_new.cs_common_module._au_music_content_wrap.case_empasis.color_7 > div.cm_top_wrap._sticky._custom_select._header > div.title_area.type_keep._title_area > div > span:nth-child(3) > a')
#     # image = soup.select_one('#main_pack > div.sc_new.cs_common_module._au_music_content_wrap.case_empasis.color_7 > div.cm_content_wrap > div.cm_content_area._cm_content_area_song_info > div > div.detail_info > div.play_wrap._sap_item > a > img')
#     # print(title.text, singer.text, image)
#     #
#     # doc = {
#     #     'url':url,
#     #     'image':image,
#     #     'singer':singer
#     # }
#     # print(doc)
#     print(url)
#
#     # db.preview_articles.insert_one(doc)
#
#     return jsonify({'msg': '프리뷰연결!'})