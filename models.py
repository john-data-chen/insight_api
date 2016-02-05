# -*- coding: utf-8 -*-
# import db
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer, Float, TIMESTAMP
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import DateTime
# from sqlalchemy import ForeignKey                                                 
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.engine import reflection                                          
from sqlalchemy.orm import scoped_session
import time
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from instance import config
from sqlalchemy.pool import NullPool
from pprint import pprint as pp
import datetime
from sqlalchemy.orm import mapper
from database import db_session
import requests
from facepy import GraphAPI
import json
import urllib2

db = SQLAlchemy()

Base = declarative_base()


class Tags(Base):
	__tablename__ = 'tags'
	query = db_session.query_property()
	id = Column(Integer, primary_key=True, nullable=True, autoincrement=True)
	title = Column(String(80, collation='utf8_unicode_ci'), unique=True)
	enable = Column(Integer, nullable=True, default=1)
	create_date = Column(DateTime, nullable=True, default=datetime.datetime.utcnow)


class Board_Tags(Base):
	__tablename__ = 'table_tags'
	query = db_session.query_property()
	id = Column(Integer, primary_key=True, nullable=True, autoincrement=True)
	board_id = Column(String(80, collation='utf8_unicode_ci'), nullable=False, index=True)
	tag_id = Column(Integer, nullable=False, index=True)


class Boards(Base):
	# this is another table
	__tablename__ = 'boards'
	__table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8',
	                  'mysql_collate': 'utf8_general_ci'}
	query = db_session.query_property()
	# this primary key is the foreign key in post.source
	id = Column(Integer, primary_key=True, nullable=True, autoincrement=True)
	source = Column(String(80, collation='utf8_unicode_ci'))
	board = Column(String(150, collation='utf8_unicode_ci'))
	board_id = Column(String(150, collation='utf8_unicode_ci'))
	link = Column(String(180, collation='utf8_unicode_ci'), unique=True,
	              index=True)
	fansCount = Column(Integer, nullable=True, default=0)
	enable = Column(Integer, default=1)
	rank = Column(Integer, default=0)
	last_check_time = Column(TIMESTAMP, nullable=True)


class Stats(Base):
	__tablename__ = 'stats'
	__table_args__ = (Index('my_index', "link", mysql_using='hash'), {'mysql_engine': 'InnoDB',
	                                                                  'mysql_charset': 'utf8',
	                                                                  'mysql_collate': 'utf8_general_ci'},
	                  )
	id = Column(Integer, primary_key=True, nullable=True, autoincrement=True)
	timestamp = Column(Integer)
	likeCount = Column(Integer, nullable=True, default=0)
	dislikeCount = Column(Integer, nullable=True, default=0)
	shareCount = Column(Integer, nullable=True, default=0)
	commentCount = Column(Integer, nullable=True, default=0)
	viewCount = Column(Integer, nullable=True, default=0)
	fansCount = Column(Integer, nullable=True, default=0)
	rank = Column(Float, nullable=True, default=0)
	link = Column(String(180, collation='utf8_unicode_ci'), nullable=False, index=True)
	board_id = Column(String(150, collation='utf8_unicode_ci'))


class User(db.Model):
	__tablename__ = 'user'

	query = db_session.query_property()

	id = db.Column(db.Integer, primary_key=True, nullable=True, autoincrement=True)
	username = db.Column(db.String(100))
	password = db.Column(db.String(100))
	email = db.Column(db.String(100))
	admin = db.Column(db.Integer, nullable=False, default=0)
	activated = db.Column(db.Integer, nullable=False, default=0)
	reload_sw = db.Column(db.Boolean, nullable=False, default=True)
	fa_mode = db.Column(db.Boolean, nullable=False, default=True)
	name_sha = db.Column(db.String(100, collation='ascii_bin'), nullable=True, default=null)

	def __init__(self, username=None, password=None, email=None, name_sha=None):
		self.username = username
		self.password = password
		self.email = email
		self.name_sha = name_sha

	def __repr__(self):
		return '<User %r>' % self.username

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return unicode(self.id)


class User_Fa(db.Model):
	__tablename__ = 'user_fa'

	query = db_session.query_property()

	id = db.Column(db.Integer, primary_key=True, nullable=True, autoincrement=True)
	username = db.Column(db.String(100))
	fa_name = db.Column(db.String(100, collation='utf8_unicode_ci'), default=null)
	fa_order = db.Column(db.Integer, nullable=True, default=null)
	sel_time = db.Column(db.Integer, nullable=True, default=24)
	sel_source = db.Column(db.String(100, collation='utf8_unicode_ci'), nullable=True, default=null)
	sel_tags = db.Column(db.String(100, collation='utf8_unicode_ci'), nullable=True, default=null)
	sel_boards = db.Column(db.String(100, collation='utf8_unicode_ci'), nullable=True, default=null)
	sel_word = db.Column(db.String(100, collation='utf8_unicode_ci'), nullable=True, default=null)
	sel_orderby = db.Column(db.String(100, collation='utf8_unicode_ci'), nullable=True, default=null)


class Posts(Base):
	# create a table named posts
	__tablename__ = 'posts'
	query = db_session.query_property()
	# define Columns in the new table
	id = Column(Integer, primary_key=True, nullable=True, autoincrement=True)
	# remove Foreign Key at first
	# source = Column(Integer, ForeignKey('post_link.id'), nullable=False)
	author = Column(String(150, collation='utf8_unicode_ci'))
	board_id = Column(String(150, collation='utf8_unicode_ci'))
	source = Column(String(50, collation='utf8_unicode_ci'))
	board = Column(String(150, collation='utf8_unicode_ci'))
	title = Column(String(150, collation='utf8_unicode_ci'))
	link = Column(String(180, collation='utf8_unicode_ci'), unique=True)
	description = Column(String(1500, collation='utf8_unicode_ci'))
	thumbnail = Column(String(150, collation='utf8_unicode_ci'))
	content = Column(Text(collation='utf8_unicode_ci'))
	create_time = Column(DateTime)
	timestamp = Column(Integer)
	likeCount = Column(Integer)
	shareCount = Column(Integer)
	commentCount = Column(Integer)
	dislikeCount = Column(Integer)
	viewCount = Column(Integer)
	rank = Column(Float, nullable=True, default=0)
	location = Column(String(50, collation='utf8_unicode_ci'))
	post_type = Column(String(20, collation='utf8_unicode_ci'))
	last_modified = Column(TIMESTAMP, nullable=True)


class sqlalchemy_(object):
	def __init__(self):
		db_drive = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (config.DB_ID, \
		                                                            config.DB_PW, config.DB_HOST, config.DB_PORT,
		                                                            config.DB_DATABASE)
		self.engine = create_engine(db_drive, encoding='utf-8', echo=False, poolclass=NullPool,
		                            isolation_level="READ UNCOMMITTED")

		# create new table if it doesn't exist
		Base.metadata.create_all(self.engine)
		Session = scoped_session(sessionmaker(bind=self.engine))
		# , autoflush=True, \))
		self.session = Session()

	def query_tags(self, args):
		Session = scoped_session(sessionmaker(bind=self.engine))
		session = Session()
		tags = session.query(Tags).filter(Tags.enable==1).all()
		response = []
		for _tag in tags:
			_tmp = {}
			_tmp["title"] = _tag.title
			_tmp["id"] = _tag.id
			# _tmp["create_date"] = _tag.create_date
			response.append(_tmp)
		session.close()
		return response


	def get_boards_statistics(self, args):
		Session = scoped_session(sessionmaker(bind=self.engine))
		# , autoflush=True, \))
		session = Session()

		and_filter_arg = []
		or_filter_arg = []
		#join_str = ".join(Boards, and_(Posts.board_id == Boards.board_id, Boards.enable == 1))"


		#if 'tags' in args:
		if 'tags' in args:
			tags = args['tags']
			for tag in tags.split(","):
				or_filter_arg.append(u"Board_Tags.tag_id =='" + tag + "'")
			join_str += ".join(Board_Tags, Posts.board_id == Board_Tags.board_id)"
		# .filter(Board_Tags.tag_id=='1')"
		#if 'tags' in args:
		#filter_str += join_str
		boards = session.query(Boards).filter(Boards.enable==1)#.join(Board_Tags).\
                                                               #filter(Boards.board_id == Board_Tags.board_id)
		#print query_str.encode("utf-8")
		#boards = eval(query_str)

		response = []
		import datetime
		for _board in boards:
			_tmp = {}
			_tmp['source'] = _board.source
			_tmp['board'] = _board.board
			_tmp['board_id'] = _board.board_id
			_tmp['board_crawler_last_check_time'] = unicode(_board.last_check_time)
			_tmp['link'] = _board.link
			_tmp['fansCount'] = _board.fansCount
			_tmp['rank'] = 0
			_tmp['error_count'] = 0
			_posts = session.query(Posts.create_time, Posts.timestamp, Posts.link).filter(Posts.board_id == _board.board_id).order_by(desc(Posts.timestamp)).first()
			if _posts == None:
			    _tmp['article_crawler_last_check_time'] = "N/A"
			    _tmp['last_article_time'] ="N/A"
			else:
			    _link = _posts.link
			    _tmp['last_article_time'] = unicode(_posts.create_time)
			    _timestamp = session.query(Stats).filter(Stats.link == _link).order_by(desc(Stats.timestamp)).first()
			    if _timestamp != None:
			        _tmp['article_crawler_last_check_time'] = datetime.datetime.fromtimestamp(_timestamp.timestamp).strftime('%Y-%m-%d %H:%M:%S')
			    else:
			        _tmp['article_crawler_last_check_time'] = "No data"
			_tmp['categories'] = []
			_tags = session.query(Tags).join(Board_Tags, Tags.id == Board_Tags.tag_id).filter(Board_Tags.board_id == _board.board_id)
			#pp(_board.__dict__)
			for tag in _tags:
			    _tmp['categories'].append(tag.title)
			response.append(_tmp)
		session.close()
		return response

	def query_distinct_board(self, args):
		Session = scoped_session(sessionmaker(bind=self.engine))
		# , autoflush=True, \))
		session = Session()
		timestamp = int(time.time() - 3600 * 72)

		and_filter_arg = []
		or_filter_arg = []
		join_str = ".join(Boards, and_(Posts.board_id == Boards.board_id, Boards.enable == 1))"

		if 'source' in args:
			source = args['source']
			and_filter_arg.append(u"Posts.source=='" + source + "'")
		and_filter_arg.append(u"Posts.timestamp >= timestamp")

		if 'tags' in args:
			tags = args['tags']
			for tag in tags.split(","):
				or_filter_arg.append(u"Board_Tags.tag_id =='" + tag + "'")
			join_str += ".join(Board_Tags, Posts.board_id == Board_Tags.board_id)"
		# .filter(Board_Tags.tag_id=='1')"

		filter_str = ""
		if len(and_filter_arg) > 0:
			arg_str = u",".join(and_filter_arg)
			filter_str = u".filter(and_(" + arg_str + "))"

		if len(or_filter_arg) > 0:
			arg_str = u",".join(or_filter_arg)
			filter_str += u".filter(or_(" + arg_str + "))"

		filter_str += join_str
		query_str = u"session.query(Posts.source, Posts.board, Posts.board_id, Boards.rank)" + filter_str + ".distinct()"
		print query_str.encode("utf-8")
		try:
			boards = eval(query_str)
		except Exception as e:
			print "eval query got an exception: " + str(e)

		response = []
		for _board in boards:
			_tmp = {}
			_tmp['source'] = _board.source
			_tmp['board'] = _board.board
			_tmp['board_id'] = _board.board_id
			_tmp['rank'] = _board.rank
			response.append(_tmp)

		session.close()
		return response

	def return_rss(self, args):
		Session = scoped_session(sessionmaker(bind=self.engine))
		# , autoflush=True, \))
		session = Session()
		# hot feeds in 6 hours
		timestamp = int(time.time() - 3600 * 6)

		and_filter_arg = []
		or_filter_arg = []
		join_str = ".join(Boards, and_(Posts.board_id == Boards.board_id, Boards.enable == 1))"

		and_filter_arg.append(u"Posts.timestamp >= timestamp")

		# /rss?tags=1
		# caution! tag number is not continuous
		# News = 1, Entertainment = 3, Technology = 4, Video = 5, Finance＝ 6, Animal = 9
		# Life = 10, Famous people = 11, Taiwan = 15, Foreign = 16
		if 'tags' in args:
			tags = args['tags']
			for tag in tags.split(","):
				or_filter_arg.append(u"Board_Tags.tag_id =='" + tag + "'")
			join_str += ".join(Board_Tags, Posts.board_id == Board_Tags.board_id)"
		# .filter(Board_Tags.tag_id=='1')"

		filter_str = ""
		if len(and_filter_arg) > 0:
			arg_str = u",".join(and_filter_arg)
			filter_str = u".filter(and_(" + arg_str + "))"

		if len(or_filter_arg) > 0:
			arg_str = u",".join(or_filter_arg)
			filter_str += u".filter(or_(" + arg_str + "))"

		filter_str += join_str
		# after last_modified value null issue is fixed, should change to 30
		query_str = u"session.query(Posts.id, Posts.author, Posts.source, Posts.board, Posts.title, Posts.link, " + \
		u" Posts.thumbnail, Posts.timestamp, Posts.last_modified, Posts.likeCount, Posts.shareCount, Posts.commentCount, " + \
		u"Posts.dislikeCount, Posts.viewCount)" + filter_str + ".distinct().order_by(desc(Posts.rank)).limit(30)"
		try:
			feeds = eval(query_str)
		except Exception as e:
			print "eval query got an exception: " + str(e)

		response = []
		for _feed in feeds:
			_tmp = {}
			_tmp['id'] = _feed.id
			_tmp['author'] = _feed.author
			_tmp['source'] = _feed.source
			_tmp['board'] = _feed.board
			_tmp['title'] = _feed.title
			_tmp['link'] = _feed.link
			_tmp['thumbnail'] = _feed.thumbnail
			_tmp['timestamp'] = _feed.timestamp
			_tmp['last_modified'] = _feed.last_modified
			_tmp['likeCount'] = _feed.likeCount
			_tmp['shareCount'] = _feed.shareCount
			_tmp['commentCount'] = _feed.commentCount
			_tmp['dislikeCount'] = _feed.dislikeCount
			_tmp['viewCount'] = _feed.viewCount
			response.append(_tmp)

		session.close()
		return response

	def query_test(self, args):
		Session = scoped_session(sessionmaker(bind=self.engine))
		# , autoflush=True, \))
		session = Session()
		# order_by(desc(table1.mycol))
		order_by = ""
		if 'order_by' in args:
			order_by_column = args['order_by']
		else:
			order_by_column = 'shareCount'
		order_by = u".order_by(desc(Posts." + order_by_column + "))"

		and_filter_arg = []
		or_filter_arg = []
		join_str = ".join(Boards, and_(Posts.board_id == Boards.board_id, Boards.enable == 1))"

		if 'st' in args:
			st = args['st']
			and_filter_arg.append(u"Posts.timestamp > " + st)

		if 'et' in args:
			et = args['et']
			and_filter_arg.append(u"Posts.timestamp<" + et)

		if 'source' in args:
			source = args['source']
			and_filter_arg.append(u"Posts.source=='" + source + "'")

		if 'tags' in args:
			tags = args['tags']
			for tag in tags.split(","):
				or_filter_arg.append(u"Board_Tags.tag_id =='" + tag + "'")
			join_str += ".join(Board_Tags, Posts.board_id == Board_Tags.board_id)"

		if 'board_id' in args:
			boards = args['board_id'].split(",")
			# for board in boards:
			and_filter_arg.append(u"Posts.board_id.in_(boards)")

		if 'q' in args:
			qs = args['q'].split(u',')
			for q in qs:
				and_filter_arg.append(u"Posts.content.like('%" + q + "%')")

		filter_str = ""
		if len(and_filter_arg) > 0:
			arg_str = u",".join(and_filter_arg)
			filter_str = u".filter(and_(" + arg_str + "))"

		if len(or_filter_arg) > 0:
			arg_str = u",".join(or_filter_arg)
			filter_str += u".filter(or_(" + arg_str + "))"

		limit_size = 30
		offset = "0"
		if 'page' in args:
			page = args['page']
			if int(page) <= 0:
				page = "1"
		else:
			page = "1"
		offset = str(limit_size * (int(page) - 1))

		paging_str = u".offset(%s).limit(%s)" % (offset, limit_size)
		# http://stackoverflow.com/questions/18468887/flask-sqlalchemy-pagination-error
		query_str = u"session.query(Posts)" + filter_str + join_str + order_by + paging_str
		print query_str.encode("utf-8")
		try:
			posts = eval(query_str)
		except Exception as e:
			print "eval query got an exception: " + str(e)

		# posts = self.session.query(Posts).order_by(desc(Posts.eval(order_by_column))).all()[:70]
		response = []
		for post in posts:
			_tmp = post.__dict__
			try:
				_tmp.pop('_sa_instance_state', None)
				_tmp['create_time'] = _tmp['create_time'].strftime('%Y-%m-%d %H:%M:%S')
				stats = session.query(Stats).filter(Stats.link == _tmp['link']).order_by(desc(Stats.timestamp)).limit(
					10)
				_tmp['histogram'] = {'value': []}
				_tmp['histogram']['type'] = "'%s'" % order_by_column

				for stat in stats:
					_ = stat.__dict__
					_tmp['histogram']['value'].append({'timestamp': _['timestamp'], 'value': float(_['rank'])})

				"""
                _tmp['stats'] = {
                    'likeCount': _tmp['likeCount'],
                    'shareCount': _tmp['shareCount'],
                    'commentCount': _tmp['commentCount'],
                    'dislikeCount': _tmp['dislikeCount'],
                    'viewCount': _tmp['viewCount']
                }
                """
			except:
				continue
			response.append(_tmp)
		session.close()
		return response

	def add_user(self, user_form):
		Session = scoped_session(sessionmaker(bind=self.engine))
		session = Session()
		print "this is user_form:"
		pp(user_form)
		try:
			user = session.query(User).filter(User.username == user_form['username']).first()
			print "query user from db:"
			pp(user)
			if user is None:
				session.add(User(**user_form))
				session.commit()
			else:
				print "user existed"
				return "used"

		except Exception as e:
			print "add user fail: " + str(e)
			return "fail"

		session.close()
		print "add user: success"
		return "success"

	def activate_user(self, name_sha):
		Session = scoped_session(sessionmaker(bind=self.engine))
		session = Session()
		try:
			# reference: https://stackoverflow.com/questions/21803278/sqlalchemy-update-not-working-with-sqlite
			session.query(User).filter(User.name_sha == name_sha).update({"activated": 1})
			session.commit()
			session.close()
			print "user account is activated"
		except Exception as e:
			print "modify activated to True fail: " + str(e)

	def return_user_fa(self, username):
		Session = scoped_session(sessionmaker(bind=self.engine))
		session = Session()
		# check user favorite(s)
		query_str = u"session.query(User_Fa.id, User_Fa.username, User_Fa.fa_order, User_Fa.fa_name, User_Fa.sel_time, \
					User_Fa.sel_source, User_Fa.sel_tags, User_Fa.sel_boards, User_Fa.sel_word, User_Fa.sel_orderby). \
				filter_by(username=username).distinct().order_by(asc(User_Fa.fa_order)).all()"
		try:
			favs = eval(query_str)
		except Exception as e:
			print "eval query got an exception: " + str(e)

		response = []
		for _fav in favs:
			_tmp = {}
			_tmp['id'] = _fav.id
			_tmp['username'] = _fav.username
			_tmp['fa_order'] = _fav.fa_order
			_tmp['fa_name'] = _fav.fa_name
			_tmp['sel_time'] = _fav.sel_time
			_tmp['sel_source'] = _fav.sel_source
			_tmp['sel_tags'] = _fav.sel_tags
			_tmp['sel_boards'] = _fav.sel_boards
			_tmp['sel_word'] = _fav.sel_word
			_tmp['sel_orderby'] = _fav.sel_orderby
			response.append(_tmp)

		session.close()
		return response

	def return_user_info(self, username):
		Session = scoped_session(sessionmaker(bind=self.engine))
		session = Session()
		# check admin / reload_switch / fa_mode
		query_str = u"session.query(User.username, User.admin, User.reload_sw, User.fa_mode). \
				filter_by(username=username).distinct().all()"
		try:
			user_info = eval(query_str)
		except Exception as e:
			print "eval query got an exception: " + str(e)

		response = []
		for _col in user_info:
			_tmp = {}
			_tmp['username'] = _col.username
			_tmp['is_admin'] = _col.admin
			_tmp['reload_sw'] = _col.reload_sw
			_tmp['fa_mode'] = _col.fa_mode
			response.append(_tmp)

		session.close()
		return response

	def add_user_favorite(self, fa_form):
		Session = scoped_session(sessionmaker(bind=self.engine))
		session = Session()
		try:
			session.add(User_Fa(**fa_form))
			session.commit()
			print "add a new user favorite: success"
			return "success"
		except Exception as e:
			print "add user favorite filters fail: " + str(e)
			return "fail"

	def update_user_favorite(self, fa_id, fa_order, fa_name, sel_time, sel_source, sel_tags, sel_boards, sel_word, \
	sel_orderby):
		Session = scoped_session(sessionmaker(bind=self.engine))
		session = Session()
		try:
			session.query(User_Fa).filter(User_Fa.id == fa_id).\
			update({"fa_order": fa_order, "fa_name": fa_name, "sel_time": sel_time, "sel_source": sel_source,
			"sel_tags": sel_tags, "sel_boards": sel_boards, "sel_word": sel_word, "sel_orderby": sel_orderby})
			session.commit()
			session.close()
			print "update a user favorite: success"
			return "success"
		except Exception as e:
			print "update user favorite filters fail: " + str(e)
			return "fail"

	def del_user_favorite(self, fa_id):
		Session = scoped_session(sessionmaker(bind=self.engine))
		session = Session()
		try:
			session.query(User_Fa).filter(User_Fa.id == fa_id).delete(synchronize_session=False)
			session.commit()
			print "delete a new user favorite: success"
			return "success"
		except Exception as e:
			print "delete user favorite filter fail: " + str(e)
			return "fail"

	def reload_switch(self, username, reload_sw):
		Session = scoped_session(sessionmaker(bind=self.engine))
		session = Session()
		# print is debug use
		print "username: " + username
		print "reload_sw: " + reload_sw
		try:
			# request send a string, so need to transform type of value
			if reload_sw == "true" or reload_sw == "false":
				if reload_sw == "true":
					reload_sw = True
				else:
					reload_sw = False
				# reference: https://stackoverflow.com/questions/21803278/sqlalchemy-update-not-working-with-sqlite
				session.query(User).filter(User.username == username).update({"reload_sw": reload_sw})
				session.commit()
				session.close()
				print "success! reload_switch is changed!"
				return "success"
			else:
				print "invalid reload_switch value: " + reload_sw
				return "fail"
		except Exception as e:
			print "modify reload_switch fail: " + str(e)
			return "fail"

	def fa_mode_switch(self, username, fa_mode):
		Session = scoped_session(sessionmaker(bind=self.engine))
		session = Session()
		# print is debug use
		print "username: " + username
		print "fa_mode: " + fa_mode
		try:
			# request send a string, so need to transform type of value
			if fa_mode == "true" or fa_mode == "false":
				if fa_mode == "true":
					fa_mode = True
				else:
					fa_mode = False
				# reference: https://stackoverflow.com/questions/21803278/sqlalchemy-update-not-working-with-sqlite
				session.query(User).filter(User.username == username).update({"fa_mode": fa_mode})
				session.commit()
				session.close()
				print "success! fa_mode is changed!"
				return "success"
			else:
				print "invalid fa_mode value: " + fa_mode
				return "fail"
		except Exception as e:
			print "modify fa_mode fail: " + str(e)
			return "fail"

	def return_user_fa(self, username):
		Session = scoped_session(sessionmaker(bind=self.engine))
		session = Session()
		# check admin and reload_switch
		query_str = u"session.query(User_Fa.id, User_Fa.username, User_Fa.fa_order, User_Fa.fa_name, User_Fa.sel_time, \
					User_Fa.sel_source, User_Fa.sel_tags, User_Fa.sel_boards, User_Fa.sel_word, User_Fa.sel_orderby). \
				filter_by(username=username).distinct().order_by(asc(User_Fa.fa_order)).all()"
		favs = eval(query_str)
		response = []
		for _fav in favs:
			_tmp = {}
			_tmp['id'] = _fav.id
			_tmp['username'] = _fav.username
			_tmp['fa_order'] = _fav.fa_order
			_tmp['fa_name'] = _fav.fa_name
			_tmp['sel_time'] = _fav.sel_time
			_tmp['sel_source'] = _fav.sel_source
			_tmp['sel_tags'] = _fav.sel_tags
			_tmp['sel_boards'] = _fav.sel_boards
			_tmp['sel_word'] = _fav.sel_word
			_tmp['sel_orderby'] = _fav.sel_orderby
			response.append(_tmp)

		session.close()
		return response

	def reload_switch(self, username, reload_sw):
		Session = scoped_session(sessionmaker(bind=self.engine))
		session = Session()
		# print is debug use
		print "username: " + username
		print "reload_sw: " + reload_sw
		try:
			# request send a string, so need to transform type of value
			if reload_sw == "true" or reload_sw == "false":
				if reload_sw == "true":
					reload_sw = True
				else:
					reload_sw = False
				# reference: https://stackoverflow.com/questions/21803278/sqlalchemy-update-not-working-with-sqlite
				session.query(User).filter(User.username == username).update({"reload_sw": reload_sw})
				session.commit()
				session.close()
				print "success! reload_switch is changed!"
				return "success"
			else:
				print "invalid reload_switch value: " + reload_sw
				return "fail"
		except Exception as e:
			print "modify reload_switch fail: " + str(e)
			return "fail"

	def add_board(self, board_info, tags):
		Session = scoped_session(sessionmaker(bind=self.engine))
		session = Session()
		try:
			board = session.query(Boards).filter(Boards.board_id == board_info['board_id']).first()
			if board is None:
				session.merge(Boards(**board_info))
				session.commit()
			else:
				session.query(Boards).filter(Boards.board_id == board_info['board_id']).update(board_info)
				session.commit()
		except Exception as e:
			print str(e)
			return "fail"

		try:
			board = session.query(Boards).filter(Boards.board_id == board_info['board_id']).first()
			# pp(board.board_id)
			# Board_Tags.query.filter(Board_Tags.board_id == board_info['board_id']).delete()
			session.query(Board_Tags).filter(Board_Tags.board_id == board_info['board_id']).delete(
				synchronize_session=False)
			for tag in tags:
				tmp = {'board_id': board.board_id, 'tag_id': int(tag)}
				pp(tmp)
				session.merge(Board_Tags(**tmp))

			session.commit()
		except Exception as e:
			print str(e)
			return "fail"
		session.close()
		return "success"

	def get_board_source_by_link(self, link):
		if "www.ptt.cc" in link:
			return "Ptt"

		if "www.facebook.com" in link:
			return "Facebook"

		if "youtube.com" in link:
			return "Youtube"

		else:
			print "Not-supported"
			return "Not-supported"

	def get_board_id_by_link(self, link):
		if "www.ptt.cc" in link:
			return self.get_ptt_board_id(link)
		if "www.facebook.com" in link:
			fb_id = self.get_facebook_board_id(link)
			access_token = self._get_access_token()
			graph = GraphAPI(access_token)
			board = graph.get(fb_id)
			return board["id"]

		if "youtube.com" in link:
			channel_id = self.get_youtube_board_id(link)
			return channel_id

	def get_ptt_board_id(self, url):
		"""
        https://www.ptt.cc/bbs/Baseball/index.html                               
        https://www.ptt.cc/bbs/Baseball/index1231.html                           
        """
		return url.split("/")[-2]

	def get_facebook_board_id(self, url):
         if 'timeline' in url:
            return url.split('-')[-1].split('/')[0]
         elif '-' in url:
            # https://www.facebook.com/Viral-Thread-363765800431935
            import re
            return re.sub("[^0-9]", "", url.split('-')[-1])
         else:
            return url.split("/")[-1].split("?")[0]

	def get_youtube_board_id(self, url):
		link = url.replace("/videos/", "")
		link = url.replace("/videos", "")
		if "channel" in url:
			return link.replace("https://www.youtube.com/channel/", "")
		elif "user" in url:
			username = link.replace("https://www.youtube.com/user/", "")
			api_key = config.YT_API_KEY
			pp(username)
			api_link = "https://www.googleapis.com/youtube/v3/channels?key=%s&forUsername=%s&part=id" % (
				api_key, username)
			# pp(api_link)
			result = json.load(urllib2.urlopen(api_link))
			# pp(result)
			return result['items'][0]['id']
		else:
			return ""

	def _get_access_token(self):
		app_id = config.FB_APP_ID
		app_secret = config.FB_APP_SECRET
		# https://github.com/jgorset/facepy
		# http://stackoverflow.com/questions/3058723/programmatically-getting- \
		#  an-access-token-for-using-the-facebook-graph-api
		payload = {'grant_type': 'client_credentials', 'client_id': app_id, 'client_secret': app_secret}
		file = requests.post('https://graph.facebook.com/oauth/access_token?', params=payload)
		# print file.text #to test what the FB api responded with
		result = file.text.split("=")[1]
		# print file.text #to test the TOKEN
		return result

	def get_board_by_link(self, link):

		if "www.ptt.cc" in link:
			return self.get_ptt_board_id(link)

		if "www.facebook.com" in link:
			fb_id = self.get_facebook_board_id(link)
			"""
            170901143077174                                                         
            """
			access_token = self._get_access_token()
			graph = GraphAPI(access_token)
			print ">>", fb_id
			board = graph.get(fb_id)
			return board["name"]

		if "youtube.com" in link:
			channel_id = self.get_youtube_board_id(link)
			api_key = config.YT_API_KEY
			api_link = "https://www.googleapis.com/youtube/v3/channels?key=%s&id=%s&part=snippet" % (
				api_key, channel_id)
			pp(api_link)
			result = json.load(urllib2.urlopen(api_link))
			pp(result)
			board_title = result['items'][0]['snippet']['title']
			return board_title

		return ""


	def update_rank_by_id(self, board_id, action):
		try:
		    Session = scoped_session(sessionmaker(bind=self.engine))
		    session = Session()
		    rank_weight = {3:2, 2:1.5, 1:1.2 , 0:1, -1:0.8, -2:0.25, -3: 0.1}

		    _board = session.query(Boards).filter(Boards.board_id == board_id).first()
		    rank = _board.rank
		    if action == "up":
			    rank += 1
		    elif action == "down":
			    rank-=1
		    else :
			    return "fails"

		    if rank > 3 or rank <-3: 
			    return "fails"

		    _posts = session.query(Posts).filter(Posts.board_id == board_id).order_by(desc(Posts.timestamp)).limit(100)
		    _stats = session.query(Stats).filter(Stats.board_id == board_id).order_by(desc(Stats.timestamp)).first()
		    fansCount = _stats.fansCount 
		    print "fansCount", fansCount
		    for post in _posts:
			    numerator = post.likeCount + post.dislikeCount +  \
			    post.commentCount + post.viewCount +  \
			    8*post.shareCount
			    _rank = round(numerator / float(fansCount), 5) * rank_weight[rank]
			    session.query(Posts).filter(Posts.id == post.id).update({"rank": _rank})
			    session.query(Boards).filter(Boards.board_id == board_id).update({"rank": rank})
		    session.commit()
		except Exception as e:
		    print str(e)
		    return "fails"
		session.close()
		return "success"
