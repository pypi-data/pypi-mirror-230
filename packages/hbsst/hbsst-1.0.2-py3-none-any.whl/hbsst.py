import sys
import os
import json
import time

SCRIPT_VERSION="1.0.2"

class main:
    def __init__(self, config=None, url=None):
        self.config = config
        self.url = url
        print("""
heStudio 百度搜索提交助手

作者：醉、倾城
博客：https://www.hestudio.net

(C)Copyright heStudio 2021-2023
        """)
        print("验证版本...")
        get_version = os.popen(str("curl https://raw.githubusercontent.com/hestudio-community/hbsst/master/version.json"))
        new_ver = json.load(get_version)
        if not new_ver["version"] == SCRIPT_VERSION:
            if SCRIPT_VERSION in new_ver["support"]:
                print("你所使用的版本为旧版本，请及时更新，避免影响你的业务。")
                print("更新内容：",new_ver["info"])
                print("更新代码： “pip install hbsst”\n")
                time.sleep(5)
            else:
                print("你所使用的版本过于老旧，请更新。")
                print("更新内容：",new_ver["info"])
                print("更新代码： “pip install hbsst”")
                sys.exit()

    def submit(self):
        print("正在读取预设方案...")
        if not self.config:
            print("请传入预设方案！")
            sys.exit()
        print("正在读取url...")
        if not self.url:
            print("请传入需要提交的url！")
            sys.exit()
        if not os.path.exists(str("hbsst_config.json")):
            print("未找到配置文件！")
            sys.exit()
        config_db = json.load(open(str("hbsst_config.json")))
        if not config_db[self.config]:
            print("未找到预设方案！")
            sys.exit()
        print("正在保存url...")
        urls = open("urls.txt", mode = 'w')
        time.sleep(1)
        urls.write(self.url)
        time.sleep(2)
        urls.close()
        time.sleep(1)
        print("正在推送...")
        curl_return = os.popen(str("curl -H 'Content-Type:text/plain' --data-binary @urls.txt "+repr(config_db[self.config])))
        curl_return_read = curl_return.read()
        time.sleep(2)
        print("正在接收返回结果...\n")
        curl_return_json = open("hbsst_return.json", mode = 'w')
        time.sleep(1)
        curl_return_json.write(str(curl_return_read))
        time.sleep(2)
        curl_return_json.close()
        time.sleep(1)
        curl_return_data = json.load(open("hbsst_return.json"))
        if "success" in curl_return_data:
            print("成功推送的url条数：", curl_return_data["success"])
        if "remain" in curl_return_data:
            print("当天剩余的可推送url条数：", curl_return_data["remain"])
        if "not_same_site" in curl_return_data:
            print("由于不是本站url而未处理的url列表：", "\n")
            for not_same in curl_return_data["not_same_site"]:
                print("- ", not_same)
        if "not_valid" in curl_return_data:
            print("不合法的url列表：", "\n")
            for not_valid in curl_return_data["not_valid"]:
                print("- ", not_valid)
        if "error" in curl_return_data:
            print("错误码：", curl_return_data["error"])
        if "message" in curl_return_data:
            print("错误描述：", curl_return_data["message"])

def submit(config=None, url=None):
    submit_data = main(config, url)
    submit_data.submit()

if __name__ == "__main__":
    main()
    print("请通过函数调用！")
