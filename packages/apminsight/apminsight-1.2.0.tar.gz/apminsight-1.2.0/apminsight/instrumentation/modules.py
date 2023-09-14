from apminsight.instrumentation.packages import django
from apminsight.instrumentation.packages import sqlite
from apminsight.instrumentation.packages import mysql
from apminsight.instrumentation.packages import flask
from apminsight.instrumentation.packages import redis
from apminsight.instrumentation.packages import jinja2
from apminsight.instrumentation.packages import pymemcache
from apminsight.instrumentation.packages import psycopg2
from apminsight.instrumentation.packages import cassandra
from apminsight.instrumentation.packages import memcache
from apminsight.instrumentation.packages import bottle
from apminsight.instrumentation.packages import cherrypy
from apminsight.instrumentation.packages import pyramid
from apminsight.instrumentation.packages import mako
from apminsight.instrumentation.packages import genshi
from apminsight.instrumentation.packages import http
from apminsight.instrumentation.packages import httpx
from apminsight.instrumentation.packages import httplib2
from apminsight.instrumentation.packages import urllib
from apminsight.instrumentation.packages import urllib3

modules_info = {}
modules_info.update(django.module_info)
modules_info.update(sqlite.module_info)
modules_info.update(mysql.module_info)
modules_info.update(flask.module_info)
modules_info.update(redis.module_info)
modules_info.update(jinja2.module_info)
modules_info.update(pymemcache.module_info)
modules_info.update(psycopg2.module_info)
modules_info.update(cassandra.module_info)
modules_info.update(memcache.module_info)
modules_info.update(bottle.module_info)
modules_info.update(cherrypy.module_info)
modules_info.update(pyramid.module_info)
modules_info.update(mako.module_info)
modules_info.update(genshi.module_info)
modules_info.update(http.module_info)
modules_info.update(httpx.module_info)
modules_info.update(httplib2.module_info)
modules_info.update(urllib.module_info)
modules_info.update(urllib3.module_info)
