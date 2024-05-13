#             buddha please make this work
#                        _oo0oo_
#                       o8888888o
#                       88" . "88
#                       (| -_- |)
#                       0\  =  /0
#                     ___/`---'\___
#                   .' \\|     |// '.
#                  / \\|||  :  |||// \
#                 / _||||| -:- |||||- \
#                |   | \\\  -  /// |   |
#                | \_|  ''\---/''  |_/ |
#                \  .-\__  '-'  ___/-. /
#              ___'. .'  /--.--\  `. .'___
#           ."" '<  `.___\_<|>_/___.' >' "".
#          | | :  `- \`.;`\ _ /`;.`/ - ` : | |
#          \  \ `_.   \_ __\ /__ _/   .-` /  /
#      =====`-.____`.___ \_____/___.-`___.-'=====
#                        `=---='

from bottle import route, run, static_file, get, abort
from bottle_websocket import GeventWebSocketServer, websocket


@route('/')
def home():
    return static_file('index.html', root='./build/')

@get('/websocket', apply=[websocket])
def WebsocketProtocol(ws):
    while True:
        msg = ws
        try:
            msg = ws.receive()
            if msg is not None:
                ws.send(msg)
            else: break
        except: abort(405, "Don't access /websocket using a browser, it's a Websocket")

@route('/static/<filename:path>')
def statics(filename): return static_file(filename, root='./build/static')

if __name__ == '__main__':
    run(host='127.0.0.1', port=8080, server=GeventWebSocketServer)