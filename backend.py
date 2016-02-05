#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import *
# Flask, url_for, render_template, request, session, redirect, abort, Response
import subprocess
import json
import traceback
import os
import time
import json
from flask.ext.login import LoginManager
from flask import render_template
# import app, db, login_manager, bcrypt
from flask.ext.login import current_user, login_required, login_user, logout_user
from flask import Flask, session
from flask.ext.session import Session
from models import User, User_Fa, sqlalchemy_, Posts, Board_Tags, Tags
from nocache import nocache
from flask.ext.sqlalchemy import SQLAlchemy
from bcrypt import *
import bcrypt
from instance import config
from flask.ext.cors import CORS
from flask import jsonify
from nullpool_sqlalchemy import nullpool_SQLAlchemy
from database import db_session
from flask import session
from pprintpp import pprint as pp
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import hashlib
from bson import json_util
from feedgen.feed import FeedGenerator
import datetime
import pytz
import sys
from flask import request
from ConfigParser import SafeConfigParser
from lxml import etree
import random

app = Flask(__name__)
# app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'super secret key'

db_drive = 'mysql+pymysql://%s:%s@%s:%s/%s' % (config.DB_ID, \
                                               config.DB_PW, config.DB_HOST, config.DB_PORT, config.DB_DATABASE)
app.config['SQLALCHEMY_DATABASE_URI'] = db_drive
app.config['SQLALCHEMY_POOL_SIZE'] = 0
app.config['SQLALCHEMY_POOL_RECYCLE'] = 5
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# https://mofanim.wordpress.com/2013/01/02/sqlalchemy-mysql-has-gone-away/
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

color_idx = 0

# app.register_blueprint(api)

alchemy = sqlalchemy_()

cors = CORS(app)
db = nullpool_SQLAlchemy()
# SQLAlchemy()
db.init_app(app)
sess = Session()
sess.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
	try:
		user = User.query.filter_by(id=id).first()
	except:
		import logging
		logger = logging.getLogger(__name__)
		hdlr = logging.FileHandler('/tmp/flask.log')
		formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		hdlr.setFormatter(formatter)
		logger.addHandler(hdlr)
		logger.setLevel(logging.WARNING)

		logger.error('%s login error ' % id)
		return redirect(url_for('logout'))
	return user


@app.route("/")
@login_required
def index():
	return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
@nocache
def login():
	if request.method == 'POST':
		# return value to frontend
		user = User.query.filter_by(username=request.form['username']).first()
		if user and (user.password == request.form['password']):
			# if user and bcrypt.check_password_hash(user.password, request.form['password']):
			# print user.password, request.form['password']
			if user.activated == 1:
				login_user(user)
				f = {"result": "success"}
			else:
				print "user is not activated."
				f = {"result": "not_activated"}
		else:
			print "Wrong ID / Password !!!"
			f = {"result": "fail"}
		return generate_json(f)
	else:
		return render_template('login.html')


@app.route('/boardstatus', methods=['GET', 'POST'])
@nocache
def boardstatus():
	return render_template("boardstatus.html")


@app.route('/register', methods=['GET', 'POST'])
@nocache
def register():
	# other resources are GET, so need to return register page
	if request.method != 'POST':
		return render_template('register.html')
	# register form is POST
	name = request.form['name']
	email = request.form['email']
	password = request.form['password']
	# xxx@ebc.net.tw will be split to ["xxx", "ebc.net.tw"]
	email_check = email.split('@')
	# check email is not xxx@ebc.net.tw or use tool to push POST
	if email_check[0] != name or email_check[1] != "ebc.net.tw":
		print "this is an illegal email"
		return redirect(url_for('login', _external=True))
	# if email is valid, check whether user is register before
	user_check = User.query.filter_by(username=name).first()
	# if user is matched
	if user_check:
		f = {"result": "used"}
	# if user user is new, hash name
	hash_object = hashlib.sha256(name)
	name_sha = hash_object.hexdigest()
	# send user info to add_user
	user_form = {"username": name, "email": email, "password": password, "name_sha": name_sha}
	f = {"result": alchemy.add_user(user_form)}
	# if add_user is success, then send him the activation mail
	if f == {"result": "success"}:
		try:
			send_reg_mail(name, email, name_sha)
		except Exception as e:
			print "other fail: " + str(e)
			f = {"result": "fail"}
	return generate_json(f)


def send_reg_mail(name, email, name_sha):
	# mail info
	sender = config.GMAIL_USERNAME
	msg = MIMEMultipart('alternative')
	msg['Subject'] = 'EBC Insight activating mail for ' + name
	msg['From'] = sender
	msg['To'] = email

	# mail content
	# this is important: insight testing is: http://insight.ebcbuzz.com:8070
	# insight production is: http://insight.ebcbuzz.com:8070
	# make sure you are using correct site name when testing and releasing
	html = """\
		<html>
			<head></head>
			<body>
			<p>Hi!<br>
				Please click this <a href="http://insight.ebcbuzz.com/activate_user?name_sha=%s">link</a> to active your account.<br>
				Thank you! <br>
			</p>
			</body>
		</html>
	""" % name_sha
	content = MIMEText(html, 'html')
	msg.attach(content)

	# Gmail config
	username = config.GMAIL_USERNAME
	password = config.GMAIL_PASSWORD

	# The actual mail send
	try:
		server = smtplib.SMTP('smtp.gmail.com:587')
		server.ehlo()
		server.starttls()
		server.login(username, password)
		server.sendmail(sender, email, msg.as_string())
		server.quit()
		print "register mail is sent"
	except Exception as e:
		print "register mail can't be sent: " + str(e)


@app.route('/activate_user')
def activate_user():
	name_sha = request.args['name_sha']
	check_sha = User.query.filter_by(name_sha=name_sha).first()
	if check_sha:
		alchemy.activate_user(name_sha)
	return redirect(url_for('index', _external=True))


@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('index', _external=True))


@app.route("/user_info", methods=['GET'])
@login_required
@nocache
def user_info_get():
	args = request.args

	# check form information is complete
	if 'username' not in args:
		print "Error! Requests does not have complete information"
		print args
		return render_template('index.html')

	# check user exists or not
	user = User.query.filter_by(username=args['username']).first()
	# if user exists
	if user:
		try:
			user_info = alchemy.return_user_info(args['username'])
			favorite = alchemy.return_user_fa(args['username'])
			f = combine_user_info(user_info, favorite)
		except Exception as e:
			print "return user info or favorite has exception: " + str(e)
			return render_template('index.html')
	else:
		print "Error! User is not register!"
		return render_template('index.html')

	return generate_json(f)


def combine_user_info(user_info, favorite):
	# user_info is a list, need to pick up the dict'value in list: user_info[0].get('key name')
	f = {"username": user_info[0].get('username'), "is_admin": user_info[0].get('is_admin'), "favorite": favorite,
	     "reload_sw": user_info[0].get('reload_sw'), "fa_mode": user_info[0].get('fa_mode')}
	pp(f)
	return f


@app.route("/user_info", methods=['POST'])
@login_required
@nocache
def user_fav_add():
	# check method
	if request.method != 'POST':
		return render_template('index.html')

	# check form information is complete
	if 'username' and 'fa_order' and 'fa_name' and 'sel_time' and 'sel_source' and 'sel_tags' and 'sel_boards' \
			and 'sel_word' and 'sel_orderby' in request.form:
		# user favorite form
		username = request.form['username']
		fa_order = request.form['fa_order']
		fa_name = request.form['fa_name']
		sel_time = request.form['sel_time']
		sel_source = request.form['sel_source']
		sel_tags = request.form['sel_tags']
		sel_boards = request.form['sel_boards']
		sel_word = request.form['sel_word']
		sel_orderby = request.form['sel_orderby']
		fa_form = {"username": username, "fa_order": fa_order, "fa_name": fa_name, "sel_time": sel_time,
		           "sel_source": sel_source, "sel_tags": sel_tags, "sel_boards": sel_boards, "sel_word": sel_word,
		           "sel_orderby": sel_orderby}

		# if user is registered
		if User.query.filter_by(username=username).first():
			try:
				f = {"result": alchemy.add_user_favorite(fa_form)}
			except Exception as e:
				print "add user favorite has exception: " + str(e)
				return render_template('index.html')
			if f == {"result": "success"}:
				try:
					user_info = alchemy.return_user_info(username)
					favorite = alchemy.return_user_fa(username)
					f = combine_user_info(user_info, favorite)
				except Exception as e:
					print "return user favorite has exception: " + str(e)
					return render_template('index.html')
		else:
			print "Error! User is not register!"
			return render_template('index.html')
	else:
		print "Error! Requests does not have complete information"
		print request.form
		return render_template('index.html')

	return generate_json(f)


@app.route("/user_info", methods=['PUT'])
@login_required
@nocache
def user_info_update():
	# check method
	if request.method != 'PUT':
		return render_template('index.html')

	# check form information is complete
	if 'username' not in request.form:
		print "Error! Requests does not have complete information"
		return render_template('index.html')

	# user favorite form
	username = request.form['username']

	# if user is registered
	if User.query.filter_by(username=username).first():
		if 'reload_sw' in request.form:
			reload_sw = request.form['reload_sw']
			try:
				f = {"result": alchemy.reload_switch(username, reload_sw)}
			except Exception as e:
				print "reload_switch has exception: " + str(e)
				return render_template('index.html')
			if f == {"result": "success"}:
				try:
					user_info = alchemy.return_user_info(username)
					favorite = alchemy.return_user_fa(username)
					f = combine_user_info(user_info, favorite)
				except Exception as e:
					print "return user favorite has exception: " + str(e)
					return render_template('index.html')

		elif 'fa_mode' in request.form:
			fa_mode = request.form['fa_mode']
			try:
				f = {"result": alchemy.fa_mode_switch(username, fa_mode)}
			except Exception as e:
				print "fa_mode switch has exception: " + str(e)
				return render_template('index.html')
			if f == {"result": "success"}:
				try:
					user_info = alchemy.return_user_info(username)
					favorite = alchemy.return_user_fa(username)
					f = combine_user_info(user_info, favorite)
				except Exception as e:
					print "return user favorite has exception: " + str(e)
					return render_template('index.html')

		# when form not only sent "username + reload_sw" or "username + fa_mode"
		elif len(request.form) > 2:
			# check favorite columns are complete
			if 'fa_id' and 'fa_order' and 'fa_name' and 'sel_time' and 'sel_source' and 'sel_tags' and 'sel_boards' \
					and 'sel_word' and 'sel_orderby' in request.form:
				try:
					fa_id = request.form['fa_id']
					if User_Fa.query.filter_by(id=fa_id).first() is None:
						print "No such favorite ID!"
						return render_template('index.html')
					fa_order = request.form['fa_order']
					fa_name = request.form['fa_name']
					sel_time = request.form['sel_time']
					sel_source = request.form['sel_source']
					sel_tags = request.form['sel_tags']
					sel_boards = request.form['sel_boards']
					sel_word = request.form['sel_word']
					sel_orderby = request.form['sel_orderby']
					f = {
						"result": alchemy.update_user_favorite(fa_id, fa_order, fa_name, sel_time, sel_source, sel_tags,
						                                       sel_boards, sel_word, sel_orderby)}
				except Exception as e:
					print "modify user favorite has exception: " + str(e)
					return render_template('index.html')

				if f == {"result": "success"}:
					try:
						user_info = alchemy.return_user_info(username)
						favorite = alchemy.return_user_fa(username)
						f = combine_user_info(user_info, favorite)
					except Exception as e:
						print "return user favorite has exception: " + str(e)
						return render_template('index.html')
			else:
				print "Error! Requests does not complete information"
				print request.form
				return render_template('index.html')
		else:
			print "Error! Requests does not complete information"
			print request.form
			return render_template('index.html')
	else:
		print "Error! User is not register!"
		return render_template('index.html')

	return generate_json(f)


@app.route("/user_info", methods=['DELETE'])
@login_required
@nocache
def user_fav_del():
	# check method
	if request.method != 'DELETE':
		return render_template('index.html')

	args = request.args
	# check form information is complete
	if 'username' and 'fa_id' not in request.form:
		print "Error! Requests does not complete information"
		return render_template('index.html')

	# user favorite form
	username = request.form['username']
	fa_id = request.form['fa_id']
	if User_Fa.query.filter_by(id=fa_id).first() is None:
		print "No such favorite ID!"
		return render_template('index.html')

	# if user is registered
	if User.query.filter_by(username=username).first():
		try:
			f = {"result": alchemy.del_user_favorite(fa_id)}
		except Exception as e:
			print "delete favorite has exception: " + str(e)
			return render_template('index.html')
		if f == {"result": "success"}:
			try:
				user_info = alchemy.return_user_info(username)
				favorite = alchemy.return_user_fa(username)
				f = combine_user_info(user_info, favorite)
			except Exception as e:
				print "return user favorite has exception: " + str(e)
				return render_template('index.html')
	else:
		print "Error! User is not register!"
		return render_template('index.html')

	return generate_json(f)


@app.route("/boards")
@nocache
def query_distinct_board():
	args = request.args

	f = {'result': alchemy.query_distinct_board(args)}
	result = json.dumps(f, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None,
	                    indent=True, separators=None, encoding="utf-8", sort_keys=False,
	                    default=json_util.default)

	resp = make_response(result)
	if request.headers.get('Accept', '').find('application/json') > -1:
		resp.mimetype = 'application/json'
	else:
		resp.mimetype = 'text/plain'
	return resp


@app.route("/tags")
@nocache
def query_tags():
	args = request.args

	f = {'result': alchemy.query_tags(args)}
	return generate_json(f)


@app.route("/get_boards_statistics")
@nocache
def get_boards_statistics():
	args = request.args

	f = {'result': alchemy.get_boards_statistics(args)}
	return generate_json(f)


@app.route("/posts_test")
@nocache
def posts_test():
	args = request.args
	print ">>>>>>>>>>>> ", args
	# .get('user')

	with open('sample.json') as data_file:
		data = json.load(data_file)

	f = {'result': alchemy.query_test(args)}
	return generate_json(f)


def poplulate_attachment(post, color):
	board_tags = Board_Tags.query.filter_by(board_id=post.board_id).all()
	tags = []
	for board_tag in board_tags:
		tag = Tags.query.filter_by(id=board_tag.tag_id).first()
		tags.append(tag.title)
		if post.viewCount == -1:
			post.viewCount = "--"

	tmp = {"fallback": "Required plain-text summary of the attachment.",
	       "color": color,
	       # "pretext": "Optional text that appears above the attachment block",
	       "author_name": "",
	       "author_link": "http://flickr.com/bobby/",
	       "author_icon": "http://www.ebcbuzz.com/images/logo.png",
	       "title": post.title,
	       "title_link": post.link,
	       "text": post.description[:80],
	       # "image_url": "http://my-website.com/path/to/image.jpg",
	       "thumb_url": post.thumbnail,
	       "fields": [
		       {"title": "tags", "value": ", ".join(tags), "short": True},
		       {"title": "likes", "value": post.likeCount, "short": True},
		       {"title": "shares", "value": post.shareCount, "short": True},
		       {"title": "PV", "value": post.viewCount, "short": True}
	       ]
	       }
	return tmp


# 'board_id':""
# 'tags':[]

# return success/fail
def get_board_link(url, source_type, board_id):
	if source_type == "Ptt":
		return "https://www.ptt.cc/bbs/" + board_id + "/index.html"
	if source_type == "Youtube":
		if "channel" in url:
			return "https://www.youtube.com/channel/" + board_id
		if "user" in url:
			return "https://www.youtube.com/user/" + board_id

	if source_type == "Facebook":
		return "https://www.facebook.com/" + board_id


@app.route("/query_board_link", methods=['GET', 'POST'])
@nocache
def query_board_link():
	args = request.args
	url = args['url']
	try:
		source_type = alchemy.get_board_source_by_link(url)
		board_title = alchemy.get_board_by_link(url)
		board_id = alchemy.get_board_id_by_link(url)
		board_link = get_board_link(url, source_type, board_id)
		tags = Board_Tags.query.filter_by(board_id=board_id).all()
		_tags = []
		for tag in tags:
			_tags.append(tag.tag_id)
		_tags = list(set(_tags))
		f = {
			'result': {
				'source': source_type,
				'board': board_title,
				'board_id': board_id,
				'link': board_link,
			},
			'tags': _tags
		}
		pp(f)

		# add error handle when user add a url which insight is not supported
		for value in f.values():
			if value == {'board_id': None, 'source': 'Not-supported', 'link': None, 'board': ''}:
				f = {'result': 'fail', 'type': 1}
		# process correct url
		session[board_link] = f

	except Exception as e:
		print str(e)
		# [803] (#803) Cannot query users by their username
		if "803" in str(e):
			f = {'result': 'fail', 'type': 803}
		# other unknown reasons
		elif "100" in str(e):
			f = {'result': 'fail', 'type': 100}
		else:
			f = {'result': 'fail', 'type': 0}
	return generate_json(f)


def generate_json(f):
	result = json.dumps(f, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None,
	                    indent=True, separators=None, encoding="utf-8", sort_keys=False, default=json_util.default)
	resp = make_response(result)
	if request.headers.get('Accept', '').find('application/json') > -1:
		resp.mimetype = 'application/json'
	else:
		resp.mimetype = 'text/plain'
	return resp


@app.route("/add_board", methods=['GET', 'POST'])
@nocache
def add_board():
	from pprintpp import pprint as pp
	# url = args['url' ]
	url = ""
	tags = []
	if request.method == 'POST':
		print "POST"
		url = request.form.get('url', None)
		tags = request.form.getlist('tags[]')
		print url
		pp(tags)
		pp(request.form)
	elif request.method == "GET":
		args = request.args
		print "GET"
		url = args['url']
		tags = args.get('tags', "").split(",")
		pp(args)
	else:
		print "!!!!!"
	for tag in tags:
		print "<<", tag

	pp(session)
	print "session key url", url
	# , session[url]
	if url in session:
		# pp(session)
		pp("url in session")
		session_var = session[url]
		try:
			source_type = session_var['result']['source']
			board_title = session_var['result']['board']
			board_id = session_var['result']['board_id']
			board_link = session_var['result']['link']
			pp(session_var['result'])
			pp(tags)
			f = {'result': alchemy.add_board(session_var['result'], tags)}
		except Exception as e:
			print str(e)
			# [803] (#803) Cannot query users by their username
			if "803" in str(e):
				f = {'result': 'fail', 'type': 803}
			# other unknown reason
			elif "100" in str(e):
				f = {'result': 'fail', 'type': 100}
			else:
				f = {'result': 'fail', 'type': 0}

	else:
		pp("url not in session")

	# 'result': 'fail'
	return generate_json(f)


@app.route("/share_to_facebook", methods=['GET', 'POST'])
@nocache
def share_to_facebook():
	args = request.args
	url = args['url']
	import requests
	# if "facebook" in url_to_share:
	r = requests.head(url, allow_redirects=True)
	f = {'result': r.url}
	return generate_json(f)


@app.route("/cart_to_email", methods=['GET', 'POST'])
@login_required
@nocache
def cart_to_email():
	if request.method != 'POST':
		return render_template('/index.html')
	# mail info
	sender = config.GMAIL_USERNAME
	email = request.form['email']
	msg = MIMEMultipart('alternative')
	# set header to utf-8
	msg['Subject'] = Header('EBC Insight 報馬仔', 'utf-8')
	msg['From'] = sender
	msg['To'] = email

	# content process
	# part 1
	html_part1 = """\
				<html>
					<head>
						<title>EBC Insight 報馬仔</title>
						<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
					</head>
					<style>
						td{border:transparent solid 10px;}
						a{border:transparent solid 10px;}
					</style>
					<body>
					"""

	# part 2
	html_part2 = ""
	post_ids = []
	content = request.form.getlist('content[]')
	# counters
	obj_counter = 0
	post_counter = 0
	# get content[](post.id) in POST
	for object_id in content:
		pp(object_id)
		post_ids.append(object_id)
		obj_counter += 1
	# insert post to html_part2
	for post_id in post_ids:
		try:
			post = Posts.query.filter_by(id=post_id).first()
			pp(post.__dict__)

			# print post.__dict__['link']
			# thumbnail link decision
			def get_thumbnail_link(post):
				if post.__dict__['source'] == 'Ptt' and post.__dict__['thumbnail'].encode('utf-8') == "":
					thumbnail_link = "http://insight.ebcbuzz.com/static/assets/pics/ptt.png"
				elif post.__dict__['source'] != 'Ptt' and post.__dict__['thumbnail'].encode('utf-8') == "":
					thumbnail_link = "http://insight.ebcbuzz.com/static/assets/pics/pic_none.png"
				else:
					thumbnail_link = post.__dict__['thumbnail'].encode('utf-8')
				return thumbnail_link

			thumbnail_link = get_thumbnail_link(post)

			# check and decide how to return viewCount
			def get_viewCount(post):
				if post.__dict__['viewCount'] >= 0:
					viewCount = str(post.__dict__['viewCount'])
				elif post.__dict__['viewCount'] == -1:
					viewCount = "--"
				else:
					viewCount = "error"
				return viewCount

			viewCount = get_viewCount(post)

			# check and decide how to return dislikeCount
			def get_dislikeCount(post):
				if post.__dict__['dislikeCount'] >= 0:
					dislikeCount = str(post.__dict__['dislikeCount'])
				elif post.__dict__['dislikeCount'] == -1:
					dislikeCount = "--"
				else:
					dislikeCount = "error"
				return dislikeCount

			dislikeCount = get_dislikeCount(post)

			def get_additional_insight(post):
				content = ""
				pp(post)
				# if post is ebc's post
				post_dic = post.__dict__
				post_board_id = post_dic['board_id']
				post_id = post_dic['link'].split("=")[-1]
				pp(post_board_id)
				if post_board_id != '124616330906800':
					return content
				insight = {}
				import get_insight_data
				_insight = get_insight_data.get_insight_data(post_id=post_id)

				insight_dict = {
					'post_impressions_unique': 'People Reached',
					'post_video_views': 'Video Views',
					'post_video_views_organic': 'Video Views (Organic)',
					'post_video_views_paid': 'Video Views (Paid)',
					'post_video_complete_views_30s': '30-Second Views',
					'post_video_complete_views_30s_organic': '30-Second Views (Organic)',
					'post_video_complete_views_30s_paid': '30-Second Views (Paid)',
					'post_video_retention_graph': 'Average View Duration',
					'post_story_adds_by_action_type': 'Likes, Comments & Shares',
					# 'post_impressions': 'post_impressions',
					# 'post_consumptions': 'post_consumptions',
					'post_engaged_users': 'Engagement User'
				}

				for _ in _insight['data']:
					if _['name'] in insight_dict.keys():
						key = _['name']
						insight[insight_dict[key]] = _['values'][0]['value']

						if _['name'] == 'post_video_retention_graph':
							max_sec = 0
							counter = 0
							print key, "\n", _['name']
							pp(_['id'])
							print type(_['values'][0]['value'])
							for k, v in _['values'][0]['value'].items():
								k = float(k)
								counter += float(v)
								if k >= max_sec:
									max_sec = k
							avg_percent = counter / max_sec
							print "avg_percent:", avg_percent, "counter:", counter, "max_sec:", max_sec
							for k, v in _['values'][0]['value'].items():
								if v < avg_percent:
									insight['Average View Duration'] = int(k)
									break
				insight['Engagement Rate'] = str(
						int(round((float(insight['Engagement User']) / insight['People Reached']) * 100))) + "%"

				def get_round_number(num):
					return_val = num
					if num / 1000 >= 1:
						return_val = str(round(num / float(1000), 1)) + "k"
					if num / 1000000 >= 1:
						return_val = str(round(num / float(1000000), 1)) + "m"
					return return_val

				insight['Engagement User'] = get_round_number(insight['People Reached'])

				import collections
				for k, v in collections.OrderedDict(sorted(insight.items())).iteritems():
					content += "<span>%s--------:  </span><span>%s</span><br/>" % (k, v)
				return content

			additional_insight = get_additional_insight(post)
			# email html content
			html_post = """\
				<a href="%s" target="_blank"><b>%s</b></a>
				<br/>
				<table border=0 cellpadding=0>
					<tr>
						<td>
							<img src="%s" height="120">
						</td>
						<td>
							<span>view--------:  </span><span>%s</span><br/>
							<span>comment--:  </span><span>%s</span><br/>
							<span>share-------:  </span><span>%s</span><br/>
							<span>like---------:  </span><span>%s</span><br/>
							<span>dislike-----:  </span><span>%s</span><br/>
							%s
						</td>
					</tr>
				</table>
				<br/>
				""" % (post.__dict__['link'].encode('utf-8'), post.__dict__['title'].encode('utf-8'), \
			           thumbnail_link, viewCount, post.__dict__['commentCount'], post.__dict__['shareCount'], \
			           post.__dict__['likeCount'], dislikeCount, additional_insight)
			# append post to html_part2
			html_part2 += html_post
			post_counter += 1
		except Exception as e:
			print "error id:" + str(post_id)
			print e

	# debug use only, print how many content[] and posts
	print "how many content[] from frontend:" + str(obj_counter)
	print "how many posts insert to mail:" + str(post_counter)

	# part 3
	html_part3 = """\
						</body>
					</html>
				"""

	html = html_part1 + html_part2 + html_part3
	# set content to utf-8
	content = MIMEText(html, 'html', 'utf-8')
	msg.attach(content)
	return send_mail(msg, sender, email)


def send_mail(msg, sender, email):
	# Gmail config
	username = config.GMAIL_USERNAME
	password = config.GMAIL_PASSWORD

	# The actual mail send
	try:
		server = smtplib.SMTP('smtp.gmail.com:587')
		server.ehlo()
		server.starttls()
		server.login(username, password)
		server.sendmail(sender, email, msg.as_string())
		server.quit()
		f = {"result": "success"}
		print "mail is sent"
	except Exception as e:
		f = {"result": "fail"}
		print "mail can't be sent: " + str(e)
	return generate_json(f)


@app.route("/make_order", methods=['GET', 'POST'])
@nocache
def make_order():
	args = request.args
	print "<<<<<<<<<<<<<<<<<<<<<<<<<"
	from pprintpp import pprint as pp
	post_ids = []
	if request.method == 'POST':
		print ">>>>>>>>>>>>>>>>>>>>>>>>>>>> you got a post"
		data = request.form.getlist('data[]')
		for object_id in data:
			pp(object_id)
			post_ids.append(object_id)
	print ">>>>>>>>>>>> ", args
	urls = ["https://hooks.slack.com/services/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",
	        "https://hooks.slack.com/services/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"]
	f = {'result': 'Success'}
	colors = ["good", "warning", "danger", "#439FE0", "red", "yellow", "black"]
	global color_idx
	color_idx += 1
	color_idx = color_idx % len(colors)
	color = colors[color_idx]
	# post_ids = ["2291967", "2749951", "3194367", "1169919", "2678527"]
	attachments = []
	for post_id in post_ids:
		try:
			post = Posts.query.filter_by(id=post_id).first()
			attachments.append(poplulate_attachment(post, color))
		except:
			print "error id:", post_id
			pass

	data = {  # "channel": "#ebcinsight", # remove channel to support various channel
		"attachments": attachments
	}
	data["username"] = "Insight報馬仔"
	data["text"] = "Selected %s posts from ebc_insight by %s <http://insight.ebcbuzz.com>" % (
		str(len(post_ids)), "")
	data["markdwn"] = True
	data["icon_emoji"] = ":chart_with_upwards_trend:"

	data2 = json.dumps(data, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None,
	                   indent=False, separators=None, encoding="utf-8", sort_keys=False, default=json_util.default)
	# requests.post(url, json=data)
	import subprocess
	for url in urls:
		cmd = "curl  -X POST --data-urlencode 'payload=%s' %s" % (str(data2), url)
		pingPopen = subprocess.Popen(args=cmd, shell=True)

	resp = make_response(data2)
	if request.headers.get('Accept', '').find('application/json') > -1:
		resp.mimetype = 'application/json'
	else:
		resp.mimetype = 'text/plain'
	return resp


@login_manager.unauthorized_handler
def unauthorized():
	return redirect(url_for('login', _external=True))


@app.teardown_appcontext
def shutdown_session(exception=None):
	db_session.remove()


@app.route("/rss")
# /rss?tags=1
# caution! tag number is not continuous
# News = 1, Entertainment = 3, Technology = 4, Video = 5, Finance＝ 6, Animal = 9
# Life = 10, Famous people = 11, Taiwan = 15, Foreign = 16
@nocache
def rss():
	args = request.args
	f = alchemy.return_rss(args)
	# which channel you choose
	# no tags == length of args is 0
	if len(args) == 0:
		channel = "All sources"
	elif args['tags'] == '1':
		channel = "News"
	elif args['tags'] == '3':
		channel = "Entertainment"
	elif args['tags'] == '4':
		channel = "Technology"
	elif args['tags'] == '5':
		channel = "Video"
	elif args['tags'] == '6':
		channel = "Finance"
	elif args['tags'] == '9':
		channel = "Animal"
	elif args['tags'] == '10':
		channel = "Life"
	elif args['tags'] == '11':
		channel = "Famous people"
	elif args['tags'] == '15':
		channel = "Taiwan"
	elif args['tags'] == '16':
		channel = "Foreign"
	else:
		channel = "invalid RSS channel!"
		print channel
		return channel
	print "RSS channel: " + channel

	# RSS channel
	fg = FeedGenerator()
	fg.title('Top ' + str(len(f)) + ' hot feeds in ' + channel)
	fg.author({'name': 'John Chen', 'email': 'john.data_chen@ebc.net.tw'})
	fg.subtitle('For EBC inside only')
	# If not set, lastBuildDate has as value the current date and time.
	fg.lastBuildDate()
	# It’s a number of minutes that indicates how long a channel can be cached before refreshing from the source.
	fg.ttl(ttl=10)
	# choose which channel to return
	# before release, remember modify production site url to http://insight.ebcbuzz.com/rss
	if 'tags' not in args:
		fg.link(href='http://insight.ebcbuzz.com/rss', rel='self')
	else:
		fg.link(href='http://insight.ebcbuzz.com/rss?tags=' + str(args['tags']), rel='self')

	"""
	# start: export RSS feed to debug
	# if this folder doesn't exist
	if not os.path.exists("_RSS_export"):
		os.mkdir("_RSS_export")

	# export to csv, open file
	oldfiles = len([name for name in os.listdir("_RSS_export/") if os.path.isfile(os.path.join("_RSS_export/", name))])
	# print is debug only
	# print "There are " + str(oldfiles) + " old RSS list(s)"
	if oldfiles >= 10:
		import shutil
		# delete folder
		shutil.rmtree("_RSS_export/")
		# re-create folder
		os.mkdir("_RSS_export")
	# print is debug only
	# print "there are over 10 old lists, clear RSS_Export folder"
	feed_list = open("_RSS_export/" + channel + "_" + str(datetime.datetime.now()) + ".csv", mode="w")
	# fix title contains emojo error
	reload(sys)
	sys.setdefaultencoding('utf-8')
	# a loop to export RSS feeds to list
	for counter in range(0, len(f) - 1):
		feed = [str(counter + 1), str(f[counter]['id']), str(f[counter]['title'])]
		feed_list.writelines(",".join(feed).encode("utf-8") + "\n")

	# close csv file
	feed_list.close()
	# end
	"""

	# a loop to input RSS feeds
	for counter in range(0, len(f)):
		# start: how to return values
		if f[counter]['source'] == 'Ptt' and f[counter]['thumbnail'] == "":
			img_src = "http://insight.ebcbuzz.com/static/assets/pics/ptt.png"
		elif f[counter]['source'] != 'Ptt' and f[counter]['thumbnail'] == "":
			img_src = "http://insight.ebcbuzz.com/static/assets/pics/pic_none.png"
		else:
			img_src = f[counter]['thumbnail']

		if f[counter]['likeCount'] >= 0:
			likeCount = str(f[counter]['likeCount'])
		else:
			likeCount = "--"

		if f[counter]['shareCount'] >= 0:
			shareCount = str(f[counter]['shareCount'])
		else:
			shareCount = "--"

		if f[counter]['commentCount'] >= 0:
			commentCount = str(f[counter]['commentCount'])
		else:
			commentCount = "--"

		if f[counter]['dislikeCount'] >= 0:
			dislikeCount = str(f[counter]['dislikeCount'])
		else:
			dislikeCount = "--"

		if f[counter]['viewCount'] >= 0:
			viewCount = str(f[counter]['viewCount'])
		else:
			viewCount = "--"
		# end

		# input feed data
		fe = fg.add_item()
		fe.guid(str(f[counter]['link']))
		fe.description(
				# thumbnail
				"<img src = \"" + img_src + "\" height=\"200px\"><br>" + \
				# Post ID is debug only, should not display in content
				# "<b>" + u"Post ID: " + "</b>" + str(f[counter]['id']) + " <br>" + \
				# RSS Channel
				"<b>" + u"Channel: " + "</b>" + channel + " " + "<br>" + \
				# Source to Author
				"<b>" + u"來源: " + "</b>" + f[counter]['source'] + "<b>" + u" / 看板: " + "</b>" + f[counter]['board'] + \
				"<b>" + u" / 作者: " + "</b>" + f[counter]['author'] + " " + "<br>" + \
				# Indicators
				"<b>" + u"Likes: " + "</b>" + likeCount + "<b>" + u" / Shares: " + "</b>" + shareCount + \
				"<b>" + u" / Comments: " + "</b>" + commentCount + "<b>" + u" / Dislikes: " + \
				"</b>" + dislikeCount + "<b>" + u" / Views: " + "</b>" + viewCount + " " + "<br>"
		)
		fe.link(href=f[counter]['link'], rel='alternate')
		fe.title(f[counter]['title'])

		# create datetime object in Taiwan timezone
		# 10/28 temp fix issue 165, last_modified should be publish time after no null
		utc = pytz.utc
		if f[counter]['last_modified'] == None:
			# for debug use
			# print f[counter]['id']
			create_time = datetime.datetime.utcfromtimestamp(f[counter]['timestamp']).replace(tzinfo=utc)
		else:
			create_time = f[counter]['last_modified'].replace(tzinfo=utc)
		fe.pubdate(create_time)
	# output RSS XML to string
	rssfeed = fg.rss_str(pretty=True, encoding="unicode")
	return rssfeed


@app.route("/news_rss")
# /news_rss?tag=earthquake
@nocache
def news_rss():
	# get current file path
	# print os.getcwd()
	# get parameters in config file
	config_parser = SafeConfigParser()
	if not os.path.isfile("../Jarvis_alpha/config.txt"):
		print "jarvis_alpha/config.txt is missing..."
		return "jarvis_alpha/config.txt is missing..."

	config_parser.read('../Jarvis_alpha/config.txt')
	jarvis_path = config_parser.get('FOLDER_PATH', 'ROOT_PATH')
	rss_path = config_parser.get('FOLDER_PATH', 'RSS_PATH')
	insight_pic_path = config_parser.get('FOLDER_PATH', 'INSIGHT_PIC_PATH')
	targets_with_img = config_parser.get('TARGET_TYPE', 'TARGETS_WITH_IMG').split(", ")
	targets_online = config_parser.get('PM_VERIFIED_PASS', 'TARGETS_ONLINE').split(", ")

	# get args.tag
	target = request.args['tag']
	if target not in targets_online:
		print "invalid target: " + target
		return "invalid target: " + target

	# detect which folder
	if os.getcwd() == "/home/charlie/public_html/production/insight_api":
		insight_news_rss_url = config_parser.get('RSS', 'INSIGHT_PRO_URL')
	else:
		insight_news_rss_url = config_parser.get('RSS', 'INSIGHT_TEST_URL')

	# rss start
	rss = etree.Element("rss", version="2.0")
	# channel start
	channel = etree.SubElement(rss, "channel")
	ch_title = etree.SubElement(channel, "title")

	link = etree.SubElement(channel, "link")
	link.text = etree.CDATA("")

	language = etree.SubElement(channel, "language")
	language.text = "zh-tw"

	copyright = etree.SubElement(channel, "copyright")
	copyright.text = etree.CDATA(u"東森電視")

	webMaster = etree.SubElement(channel, "webMaster")
	webMaster.text = "contact@ebc.net.tw"

	ttl = etree.SubElement(channel, "ttl")
	ttl.text = "60"

	pubDate = etree.SubElement(channel, "pubDate")
	# file check, if not, return error message
	if not os.path.isfile(jarvis_path + rss_path + target + "/last_publish_time.txt"):
		print jarvis_path + rss_path + target + "/last_publish_time.txt is missing..."
		return jarvis_path + rss_path + target + "/last_publish_time.txt is missing..."
	with open(jarvis_path + rss_path + target + "/last_publish_time.txt", "r") as data:
		last_publish_time = data.read()
	pubDate.text = last_publish_time

	# item start
	item = etree.SubElement(channel, "item")

	item_title = etree.SubElement(item, "title")
	# file check, if not, return error message
	if not os.path.isfile(jarvis_path + rss_path + target + "/last_title.txt"):
		print jarvis_path + rss_path + target + "/last_title.txt is missing..."
		return jarvis_path + rss_path + target + "/last_title.txt is missing..."
	with open(jarvis_path + rss_path + target + "/last_title.txt", "r") as data:
		last_title = data.read().decode('utf8')
	item_title.text = etree.CDATA(last_title)

	link = etree.SubElement(item, "link")
	link.text = etree.CDATA("")

	guid = etree.SubElement(item, "guid", isPermaLink="false")
	guid.text = target + "_" + pubDate.text

	pubDate = etree.SubElement(item, "pubDate")
	pubDate.text = last_publish_time

	cover_image = etree.SubElement(item, "cover_image")
	cover_image.text = ""

	description = etree.SubElement(item, "description")

	summary = etree.SubElement(item, "summary")
	# file check, if not, return error message
	if not os.path.isfile(jarvis_path + rss_path + target + "/last_text.txt"):
		print jarvis_path + rss_path + target + "/last_text.txt is missing..."
		return jarvis_path + rss_path + target + "/last_text.txt is missing..."
	with open(jarvis_path + rss_path + target + "/last_text.txt", "r") as data:
		last_text = data.read().decode('utf8')
	summary.text = etree.CDATA(last_text)

	author = etree.SubElement(item, "author")
	author.text = etree.CDATA(u"東森記者 - 賈維斯")

	# load configs based target
	# targets without info img
	if target == "earthquake":
		ch_title.text = etree.CDATA(u"EBC 地震最快報！")

		earthquake_logo = config_parser.get('RSS', 'EARTHQUAKE_LOGO')
		cover_image.text = etree.CDATA(earthquake_logo)
		# file check, if not, return error message
		if not os.path.isfile(jarvis_path + rss_path + target + "/img_url.txt"):
			print target + "/img_url.txt is missing..."
			description.text = etree.CDATA(last_text)
		else:
			with open(jarvis_path + rss_path + target + "/img_url.txt", "r") as data:
				img_url = data.read()
				html = last_text + "<img src = \"" + img_url + "\" height=\"480px\">"
				description.text = etree.CDATA(html)

	if target in targets_with_img:
		if target == "gas_price":
			ch_title.text = etree.CDATA(u"EBC 油價快報！")

		elif target == "gas_predict":
			ch_title.text = etree.CDATA(u"EBC 油價預先報！")
			description.text = etree.CDATA(last_text)

		elif target == "tw_stock":
			ch_title.text = etree.CDATA(u"EBC 台股收盤！")
			description.text = etree.CDATA(last_text)

		# info img check, if not, return error message
		if not os.path.isfile(insight_pic_path + target + "/last_" + target + ".jpg"):
			print insight_pic_path + target + "/last_" + target + ".jpg" + " is missing..."
			cover_image.text = etree.CDATA("last_" + target + ".jpg" + " is missing...")
		else:
			random_int = random.sample(range(100000), 1)
			cover_image.text = etree.CDATA(insight_news_rss_url + target + "/last_" + target + ".jpg" + "?" + str(random_int[0]))
		description.text = etree.CDATA(last_text)

	return etree.tostring(rss, encoding="utf-8", xml_declaration=True, pretty_print=True)


@app.route("/adjust_rank", methods=['GET', 'POST'])
@nocache
def adjust_rank():
	board_id = request.values["board_id"]
	action = request.values["action"]
	# args = request.args
	result = alchemy.update_rank_by_id(board_id, action)
	if result == 'success':
		f = {'result': 'success'}
	else:
		f = {'result': 'fail'}
	return generate_json(f)


if __name__ == "__main__":
	app.run(host='0.0.0.0', port=config.SERVER_PORT, threaded=True, debug=True)
# , ssl_context=context)
