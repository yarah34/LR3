import http.cookies
import math
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import psycopg2
from jinja2 import Environment, FileSystemLoader

client = psycopg2.connect(
    dbname='db_name1',
    user='postgres',
    password='P@ssw0rd',
    host='localhost',
    port=5432
)

pugjs = Environment(
    loader=FileSystemLoader('.'),
    extensions=['pypugjs.ext.jinja.PyPugJSExtension']
)

# Слушатель http запросов
class HTTPHandler(BaseHTTPRequestHandler):

    def redirect(self, location, cookies=None):
        self.send_response(301)
        self.send_header("Location", location)
        if cookies is not None:
            self.send_header('Set-Cookie', cookies.output(header="", sep=""))
        self.end_headers()

    def send(self, status_code, content=None, content_type="text/html;charset=UTF-8", cookies=None):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        if cookies is not None:
            self.send_header('Set-Cookie', cookies.output(header="", sep=""))
        self.end_headers()
        if content is not None:
            self.wfile.write(content.encode("UTF-8"))

    def get_cookies(self) -> http.cookies.SimpleCookie:
        cookies_string = self.headers.get('Cookie')
        cookies = http.cookies.SimpleCookie()
        if cookies_string:
            cookies.load(cookies_string)
        return cookies

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        url = urlparse(self.path)
        params = parse_qs(self.rfile.read(content_length).decode('UTF-8'))

        if url.path == "/signin":
            login = params.get('name').pop()
            password = params.get('pass').pop()

            cursor = client.cursor()

            try:
                cursor.execute(
                    "SELECT name as result FROM users WHERE name = %s AND pass = md5(%s)",
                    (login, password)
                )
                data: tuple = cursor.fetchone()
                cursor.close()

                user_id: str = data[0]
                if len(data) > 0 and user_id:
                    one_day_to_seconds = 24 * 60 * 60
                    cookies = http.cookies.SimpleCookie()
                    cookies['userId'] = user_id
                    cookies['userId']['max-age'] = one_day_to_seconds
                    cookies['userId']['HttpOnly'] = True
                    self.redirect("/books", cookies=cookies)
            except Exception as e:
                self.send(403, "Username or password incorrect!")
                print(f"Error {e}.")
            finally:
                cursor.close()
        elif url.path == "/addbook":
            print("adding new book")
            aid = params.get('author').pop()
            bname = params.get('bookname').pop()
            bid = math.floor(random.random() * 2000)

            booksql = "insert into book(id, name) values(%s, %s)"
            assignsql = "insert into books_by_authors(id, aid, bid) values (%s, %s, %s)"

            cursor = client.cursor()

            try:
                cursor.execute(
                    booksql,
                    (bid, bname)
                )
                cursor.execute(
                    assignsql,
                    (math.floor(random.random() * 3000), aid, bid)
                )
            except Exception as e:
                print(f"Error: {e}.")
            finally:
                cursor.close()

            self.redirect('/books')
            print("added new book")
        else:
            self.send(404, f"Page {self.path} not found!")

    def do_GET(self):
        url = urlparse(self.path)
        params = parse_qs(url.query)

        if url.path == "/books":

            user = self.get_cookies().get("userId")
            if not user:
                print("unauthenticated. redirect to login")
                self.redirect('/')
                return
            print('Cookies:', self.get_cookies())

            bookname = params.get("name")

            sql = "select ba.id, a.name as author, b.name as book from books_by_authors ba" \
                  " left join author a on a.id = ba.aid" \
                  " left join book b on b.id = ba.bid "

            if bookname:
                sql += "where b.name like %s"
                bookname = bookname.pop()

            cursor = client.cursor()

            try:
                if bookname:
                    cursor.execute(sql, (bookname, ))
                else:
                    cursor.execute(sql)
                data: list = cursor.fetchall()
                cursor.close()

                res = pugjs.get_template('views/booklist.pug').render(
                    filter=bookname if bookname else "",
                    data=data
                )
                self.send(200, res)
            except Exception as e:
                print(f"Error {e}.")
                self.send(500)
            finally:
                cursor.close()
        elif url.path == "/":
            self.redirect("/login.html")
        else:
            path = "./static" + self.path

            # Fix Path Traversal
            while "../" in path or "//" in path:
                path = path.replace("../", "").replace("//", "/")

            file_name = Path(path).name

            # Extension filter
            if file_name.endswith(".html") or file_name.endswith(".ico"):
                try:
                    with open(path, "r", encoding="UTF-8") as f:
                        answer = f.read()
                        self.send(200, answer)
                except Exception as e:
                    print(e)
                    self.send(404)
            else:
                self.send(403)


def main():
    # Создаём объект http-сервера
    http_server = HTTPServer(("192.168.1.133", 44444), HTTPHandler)
    http_server.serve_forever()


if __name__ == '__main__':
    main()
