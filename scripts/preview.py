# 本地预览：模拟 Cloudflare Pages 的 clean URL（/a/b -> /a/b.html，/a/ -> /a/index.html）
# 用法：python scripts/preview.py [端口，默认 8765]
import http.server
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def send_head(self):
        path = self.path.split('?', 1)[0].split('#', 1)[0]
        local = os.path.join(ROOT, path.lstrip('/').replace('/', os.sep))
        if not path.endswith('/') and not os.path.exists(local) and os.path.isfile(local + '.html'):
            self.path = path + '.html'
        return super().send_head()


if __name__ == '__main__':
    print(f'Preview: http://localhost:{PORT}/zh/models/')
    http.server.ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
