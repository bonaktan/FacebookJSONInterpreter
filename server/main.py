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

from bottle import Bottle, static_file, abort, request
from bottle_websocket import GeventWebSocketServer, websocket

app = Bottle()

@app.route('/')
def home():
    return static_file('index.html', root='./build/')

@app.get('/websocket', apply=[websocket])
def WebsocketInterface(ws):
    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        print('405')
        abort(405, "Don't access /websocket using a browser, it's a WebSocket")
    while True:
        try:
            message = wsock.receive()
            if message == None: continue
            print(message)
            wsock.send("Your message was: %r" % message)
        except WebSocketError:
            break

@app.route('/static/<filename:path>')
def statics(filename): return static_file(filename, root='./build/static')

if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    from geventwebsocket import WebSocketError
    from geventwebsocket.handler import WebSocketHandler
    server = WSGIServer(('127.0.0.1', 42069), app,
                    handler_class=WebSocketHandler)
    print("Access at http://%s:%s/websocket.html" % ('127.0.0.1', 42069))
    server.serve_forever()