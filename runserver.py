#coding=utf-8
import sys

from apps import app

if __name__ == '__main__':
    HOST = '0.0.0.0'
    PORT = 8888
    app.run(HOST, PORT, debug = True, use_reloader = True)
    print("--------------------server start---------------------------")

