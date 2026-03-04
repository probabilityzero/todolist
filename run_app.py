from threading import Thread
import webview
import socket

from app import app


def find_free_port():
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def run_flask(port):
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)


if __name__ == '__main__':
    port = find_free_port()
    t = Thread(target=run_flask, args=(port,), daemon=True)
    t.start()
    webview.create_window('Todo List', f'http://127.0.0.1:{port}/')
    webview.start()
