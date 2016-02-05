#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from flask import Flask, url_for, render_template, request, session, redirect, abort, Response, make_response
from flask import jsonify
import json
from flask.ext.cors import CORS
from nocache import nocache
from flask import request
import settings 
from database import *


alchemy = sqlalchemy_()

app = Flask(__name__)
cors = CORS(app)

@app.route("/")
def index():
    return render_template('index.html')
"""
@app.route("/mock")
def mock():
    return render_template('mock.html')



from flask import Response
@app.route("/posts")
@nocache
def posts():
    args = request.args
    print ">>>>>>>>>>>> ", args
    #.get('user')
   
    with open('sample.json') as data_file:    
        data = json.load(data_file)


    f = {'result': alchemy.query(args)}   
    result = json.dumps(f, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=True, separators=None, encoding="utf-8", default=None, sort_keys=False)
    
    # 
    #return Response(result, mimetype='application/json')
    # 
    resp = make_response(result)
    else:
        resp.mimetype = 'text/plain'
    return resp

"""

from flask import Response
@app.route("/boards")
@nocache
def query_distinct_board():
    args = request.args

    f = {'result': alchemy.query_distinct_board(args)}   
    result = json.dumps(f, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=True, separators=None, encoding="utf-8", default=None, sort_keys=False)

    """
    return Response(result, mimetype='application/json')
    """
    resp = make_response(result)
    if request.headers.get('Accept', '').find('application/json') > -1:
        resp.mimetype = 'application/json'
    else:
        resp.mimetype = 'text/plain'
    return resp


from flask import Response
@app.route("/posts_test")
@nocache
def posts_test():
    args = request.args
    print ">>>>>>>>>>>> ", args
    #.get('user')
   
    with open('sample.json') as data_file:    
        data = json.load(data_file)


    f = {'result': alchemy.query_test(args)}   
    result = json.dumps(f, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=True, separators=None, encoding="utf-8", default=None, sort_keys=False)
    
    """
    return Response(result, mimetype='application/json')
    """
    resp = make_response(result)
    if request.headers.get('Accept', '').find('application/json') > -1:
        resp.mimetype = 'application/json'
    else:
        resp.mimetype = 'text/plain'
    return resp


@app.route("/posts_sql")
def posts_sql():
    """
    return flask.jsonify(**f), 201
    return jsonify(**f)
    id=1, email="preiva@gmail.com")
    import sql
    qryresult = sql.query_posts()
    return jsonify(json_list=[i.serialize for i in qryresult.all()])
    """
    pass




@app.route("/center/<name>/")
def center(name):
    if os.path.isfile('./kml/area_center/result-%s.json' % name):
        buf = open('./kml/area_center/result-%s.json' % name).read()
        return Response(buf, mimetype='application/json')
    return '', 404

@app.route("/area/<name>/<ratio>/")
def area(name, ratio):
    if not os.path.isfile('./kml/area_center/result-%s.json' % name):
        return '', 404
    if not os.path.isfile('./kml/kml_%s/%s.kml' % (ratio, name)):
        return '', 404

    buf = open('./kml/kml_%s/%s.kml' % (ratio, name)).read()
    return buf.replace('330030ff', '55ffffff')

if __name__ == "__main__":
    app.secret_key = 'zooz'
    app.debug = True
    app.run(host='0.0.0.0', port=settings.SERVER_PORT, threaded=True)

