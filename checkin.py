# encoding=utf8
import io
import sys
import json
import platform
import subprocess

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait

# 获得浏览器的版本号
def get_driver_version():
    system = platform.system()

    if system == "Darwin":
        cmd = r'''/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version'''
    elif system == "Windows":
        cmd = r'''powershell -command "&{(Get-Item 'C:\Program Files\Google\Chrome\Application\chrome.exe').VersionInfo.ProductVersion}"'''

    try:
        out, err = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    except IndexError as e:
        print('Check chrome version failed:{}'.format(e))
        return 0

    if system == "Darwin":
        out = out.decode("utf-8").split(" ")[2].split(".")[0]
    elif system == "Windows":
        out = out.decode("utf-8").split(".")[0]

    return out

# 签到程序，发送签到请求
def glados_checkin(driver):
    checkin_url = "https://glados.rocks/api/user/checkin"
    checkin_query = """
            (function (){
            var request = new XMLHttpRequest();
            request.open("POST","%s",false);
            request.setRequestHeader('content-type', 'application/json;charset=UTF-8');
            request.setRequestHeader('origin', 'https://glados.rocks');
            request.setRequestHeader('authority', 'glados.rocks');
            request.setRequestHeader('authorization', '69794648422198146854520851128606-1080-1920');
            request.setRequestHeader('sec-ch-ua', '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"');
            request.setRequestHeader('user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36');
            request.send('{"token": "glados.one"}');
            return request;
            })();
            """ % (checkin_url)
    checkin_query = checkin_query.replace("\n", "")
    resp = driver.execute_script("return " + checkin_query)
    resp = json.loads(resp["response"])
    return resp["code"], resp["message"]


def glados_status(driver):
    status_url = "https://glados.rocks/api/user/status"
    status_query = """
        (function (){
        var request = new XMLHttpRequest();
        request.open("GET","%s",false);
        request.send(null);
        return request;
        })();
        """ % (status_url)
    status_query = status_query.replace("\n", "")
    resp = driver.execute_script("return " + status_query)
    resp = json.loads(resp["response"])
    return resp["code"], resp["data"]


def glados(cookie_string):
    options = uc.ChromeOptions()
    options.add_argument("--disable-popup-blocking")

    version = get_driver_version()
    # 20230809报错，提示HttpError，将下面改为空参就可以了
    # driver = uc.Chrome(version_main=version, options=options)
    driver = uc.Chrome()
    print(uc.find_chrome_executable())
    # Load cookie
    driver.get("https://glados.rocks")

    if cookie_string.startswith("cookie:"):
        cookie_string = cookie_string[len("cookie:"):]
    cookie_dict = [
        {"name": x[:x.find('=')].strip(), "value": x[x.find('=') + 1:].strip()}
        for x in cookie_string.split(';')
    ]

    driver.delete_all_cookies()
    for cookie in cookie_dict:
        if cookie["name"] in ["koa:sess", "koa:sess.sig"]:
            driver.add_cookie({
                "domain": "glados.rocks",
                "name": cookie["name"],
                "value": cookie["value"],
                "path": "/",
            })

    driver.get("https://glados.rocks")
    WebDriverWait(driver, 240).until(
        lambda x: x.title != "Just a moment..."
    )

    message = str()
    # 执行签到程序
    checkin_code, checkin_message = glados_checkin(driver)
    # checkin_code如果为0代表签到成功，如果为1代表签到失败（可能是已签到，checkin_message一般是：oops,token error），2或其他代表登陆错误；
    if checkin_code == -2:
        checkin_message = "Login fails, please check your cookie."

    message = f"{message}【Checkin】{checkin_message}\n"
    print(f"【Checkin】{checkin_message}")

    if checkin_code != -2:
        status_code, status_data = glados_status(driver)
        left_days = int(float(status_data["leftDays"]))
        print(f"【Status】Left days:{left_days}")
        message = f"{message}【Status】Left days:{left_days}\n"

    driver.close()
    driver.quit()

    return checkin_code, message