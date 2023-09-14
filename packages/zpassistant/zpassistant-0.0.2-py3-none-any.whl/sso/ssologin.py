import base64
import datetime
import os
import requests
from selenium import webdriver
import time
import http.cookiejar
import urllib.parse

class SsoLoginUtil:
    def __init__(self,sso_url = None):
        self.browser_type_map = {
            "chrome": self.init_chrome,
            "edge": self.init_edge,
            "firefox": self.init_firefox,
            "safari": self.init_safari,
        }
        self.installed_browser = None
        self.work_folder = ".zpsso"
        # 读取环境变量 ZPSSO_FOLDER_NAME
        self.url =os.getenv("ZPSSO_URL",sso_url)

    def ssologinByBrowser(self,url, checkFunction):
        session = requests.Session() 
        # 创建LWPCookieJar对象
        cookie_jar = http.cookiejar.LWPCookieJar(filename=self.get_or_create_work_dir() + '/cookies.txt')
        # 校验是否超时
        if cookie_jar.filename is not None and os.path.exists(cookie_jar.filename):
            cookie_jar.load()
            if not self.check_cookie_jar_expire(cookie_jar):
                # 遍历cookie,延期一天
                for cookie in cookie_jar:
                    cookie.expires = (datetime.datetime.now() + datetime.timedelta(days=1)).timestamp()
                session.cookies = cookie_jar
                return session
            else:
                print("cookie 过期,重新登录")
                cookie_jar.clear()

        # 创建一个浏览器实例，这里使用Chrome浏览器作为示例
        print("正在打开浏览器,请进行单点登录操作,请耐心等待...")
        browser = self.get_installed_browser()
        # 打开一个网页
        browser.get(f"{self.url}?service={url}")
        # 等待用户进行操作，例如登录或浏览网页
        while True:
            time.sleep(1)
            print("等待用户登录...")
            if checkFunction(browser):
                break

        # 获取浏览器中的cookie
        browser_cookies = browser.get_cookies()

        # 将浏览器中的cookie添加到cookie_jar中
        expiration_time = datetime.datetime.now() + datetime.timedelta(days=1)
        for cookie in browser_cookies:
            cookie_dict = {
                "version": 0,
                "name": cookie['name'],
                "value": cookie['value'],
                "port": None,
                "port_specified": False,
                "domain": cookie['domain'],
                "domain_specified": True,
                "domain_initial_dot": False,
                "path": cookie['path'],
                "path_specified": True,
                "secure": False,
                "expires": expiration_time.timestamp() if "expires" not in cookie else cookie['expires'],
                "discard": False,
                "comment": None,
                "comment_url": None,
                "rfc2109": False,
                "rest": {'HttpOnly': None}
            }
            cookie_jar.set_cookie(http.cookiejar.Cookie(**cookie_dict))

        # 保存cookie_jar到指定文件
        cookie_jar.save()

        # 关闭浏览器
        browser.quit()
        session.cookies = cookie_jar
        return session

    def get_or_create_work_dir(self):
        user_home = os.path.expanduser("~")
        folder_name = self.work_folder
        config_path = os.path.join(user_home, folder_name)
        if not os.path.exists(config_path):
            os.makedirs(config_path)
            print(f"文件夹 '{folder_name}' 已创建在用户主目录下。")
        return os.path.abspath(config_path)


    def is_cookie_expired(self,cookie):
        current_time = datetime.datetime.now()
        return cookie.expires is not None and cookie.expires < current_time.timestamp()


    def check_cookie_jar_expire(self,cookie_jar):
        for cookie in cookie_jar:
            if self.is_cookie_expired(cookie):
                return True
        return False

    def ssoLoginByUserNamePassword(self,url, userName, password):
        # 密码去除前后空格,base64加密
        password = password.strip()
        password = base64.b64encode(str(password).encode("utf-8")).decode()
        # urlEncode
        password = urllib.parse.quote(password)
        portal_address = urllib.parse.quote(url)
        headers = {
            'Referer': self.url
        }
        session = requests.Session()
        session.cookies = http.cookiejar.LWPCookieJar(filename=self.get_or_create_work_dir() + '/cookies.txt')
        __data = f"path={portal_address}&username={userName}&password={password}&hideDing=true&loginthrid=&ct="
        response = session.post(self.url, data=__data, headers=headers, allow_redirects=True)
        if response.status_code == 200:
            response = session.get(response.url, allow_redirects=True)
            if response.status_code == 200:
                apolloCasUrl = urllib.parse.unquote(response.url)
                redirectUrl = apolloCasUrl.split("redirectUrl=")[1]
                response = session.get(redirectUrl)
                if response.status_code == 200:
                    session.cookies.save(ignore_discard=True, ignore_expires=True)
                    return session
        raise Exception("登录失败" + response.text)


    def is_chrome_installed(self):
        if self.get_installed_browser() is not None:
            return True
        return False


    def init_chrome(self):
        # 尝试检测Chrome浏览器
        try:
            from selenium.webdriver.chrome.service import Service as ChromeService
            return webdriver.Chrome(service=ChromeService())
        except Exception as e:
            pass


    def init_edge(self):
        # 尝试检测Edge浏览器
        try:
            from selenium.webdriver.edge.service import Service as EdgeService
            return webdriver.Edge(service=EdgeService())
        except Exception as e:
            pass


    def init_firefox(self):
        # 尝试检测Firefox浏览器
        try:
            from selenium.webdriver.firefox.service import Service as FirefoxService
            return webdriver.Firefox(service=FirefoxService())
        except Exception as e:
            pass


    def init_safari(self):
        # 尝试检测Safari浏览器 (需要Safari驱动程序)
        try:
            from selenium.webdriver.safari.service import Service as SafariService
            return webdriver.Safari(service=SafariService())
        except Exception as e:
            pass


    def get_installed_browser(self):
        if self.installed_browser is not None:
            return self.installed_browser
        # 读取浏览器类型

        typePath = os.path.abspath(self.get_or_create_work_dir() + "/browser")
        if os.path.exists(typePath):
            with open(typePath, 'r', encoding="utf-8") as f:
                typePath = f.read()
        if typePath:
            type = typePath.strip()
            if type in self.browser_type_map:
                return self.browser_type_map[type]()
        for browser_type in self.browser_type_map:
            self.installed_browser = self.browser_type_map[browser_type]()
            if self.installed_browser is not None:
                with open(typePath, 'w', encoding="utf-8") as f:
                    f.write(browser_type)
                return self.installed_browser
        return self.installed_browser
