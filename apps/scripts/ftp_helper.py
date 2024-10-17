from ftplib import FTP
import requests
from requests_toolbelt.adapters import host_header_ssl
from requests.auth import HTTPBasicAuth
import socket
import socks
import re
import urllib.parse
import os

#需要使用代理来连接ftp
PROXY_HOST = ""
PROXY_PORT = 123
PROXY_USER = ""
PROXY_PSW = ""

FTP_HOST = ""
FTP_PORT = 21
FTP_USER = ""
FTP_PSW = ""

#下面2个测试用的不需要
#test_FILE_TO_UPLOAD = "/root/test.sh"
#test_TARGET_PATH = "/package/autoupload/testsucc.txt"

#下载
PKG_DOWNLAOD_URL = "http://192.168.1.218/"
DOWANLOAD_FOLDER = "./apps/package"

#上传
UPLOAD_PATH = "/package/autoupload/"
#该函数是全流程，保留用来查看学习
def upload_file_to_ftp_old_no_use(file_name, target_name):
    print("开始上传文件到 FTP 服务器...")
    file_path = "./apps/package/" + file_name
    target_path = "/package/autoupload/" + target_name
    try:
         # 使用 SOCKS 代理连接 FTP
        socks.set_default_proxy(socks.HTTP, PROXY_HOST, PROXY_PORT, True, PROXY_USER, PROXY_PSW)
        socket.socket = socks.socksocket

        # 创建 FTP 客户端
        ftp = FTP()

        # 连接到 FTP 服务器
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PSW)

        with open(file_path, "rb") as f:
            ftp.storbinary(f"STOR {target_path}", f)
        print("文件上传成功")
    except Exception as e:
        print(f"发生错误: {e}")

    # 关闭 FTP 连接
    finally:
        try:
            ftp.quit()
        except:
            pass
    
def create_package_name(file_name):
    #是国内还是海外
    head = ""
    #是否开启GM
    gm = ""
    #是否有sdk
    sdk = ""
    server = ""
    print(file_name)
    if "国内":
        head = "Y"
    else:
        head = ""
    if "GM":
        gm = "gm_"
    if "sdk":
        sdk = "sdk_"
    if "gray":
        server = "gray_"
    else:
        server = ""
    version = extract_numbers(file_name)
    name = f"{head}{gm}{sdk}{server}{version}.apk"
    print(name)
    return name
    
def extract_numbers(file_name):
    # 匹配两个连字符之间的数字
    match = re.search(r'-(\d+)-', file_name)
    if match:
        number = match.group(1)
        return number
    else:
        return '0000'
    

#获取资源版本号，但是好像比较复杂先不管
def get_res_version():
    print("start")
    #海外分支安卓打包
    url = "http://192.168.1.218:8080/job/%E6%B5%B7%E5%A4%96%E5%88%86%E6%94%AF%E5%AE%89%E5%8D%93%E6%89%93%E5%8C%85/21/console"
    #灰度分支安卓打包
    #url = "http://192.168.1.218:8080/job/%E9%9B%B7%E9%9C%86%E7%81%B0%E5%BA%A6%E5%88%86%E6%94%AF%E5%AE%89%E5%8D%93%E6%89%93%E5%8C%85/262/console"
    #灰度分支安卓热更
    #url = "http://192.168.1.218:8080/job/%E9%9B%B7%E9%9C%86%E7%81%B0%E5%BA%A6%E5%88%86%E6%94%AF%E5%AE%89%E5%8D%93%E7%83%AD%E6%9B%B4/89/console"
    USERNAME = ''
    PASSWORD = ''
    try:
        response = requests.get(f"{url}", auth=HTTPBasicAuth(USERNAME, PASSWORD))
        response.raise_for_status()  # 检查请求是否成功
        html_content = response.text
        pattern = r'打包后新资源版本号：:(\d+)'
        match = re.search(pattern, html_content)
        namelist_str = match.group()
        print(namelist_str)
        version_num = namelist_str.split(":")[1]
        print(version_num)
    except requests.exceptions.HTTPError as err:
        return print({"error": str(err)})
    except Exception as ex:
        return print({"error": str(ex)})

#获取下载页面的包名列表
def get_pkg_name_list():
    #url = ''
    # 发送 GET 请求
    response = requests.get(PKG_DOWNLAOD_URL)
    # 检查请求是否成功
    response.raise_for_status()
    # 获取 HTML 源码
    html_content = response.text
    #print(html_content)
    # 匹配文件名列表
    pattern = r'fileNameList\s*=\s*\[(.*?)\]'
    match = re.search(pattern, html_content)
    namelist_str = match.group()
    #print(namelist_str)
     # 找到'['的位置, +1 是为了跳过'['
    start_index = namelist_str.index('[') + 1
    # 找到']'的位置
    end_index = namelist_str.rindex(']')
    # 提取内容
    file_names_segment = namelist_str[start_index:end_index]  
    # 以逗号分割并去掉引号和多余空格
    file_name_list = [name.strip().strip('"') for name in file_names_segment.split(',')]
    return file_name_list

#下载指定包名的APK文件
def download_pkg_by_name(pkg_name):
    print("------startdownload-------")
    if not check_pkg_already_download(pkg_name):
    #file_url = ''
        file_url = PKG_DOWNLAOD_URL + chinese_to_http(pkg_name)
        print(f"download {pkg_name} from {file_url}")
        response = requests.get(file_url)
        # 检查请求是否成功
        # 如果请求失败，这行会抛出异常
        response.raise_for_status()
        # 目标文件路径
        file_path = os.path.join(DOWANLOAD_FOLDER, pkg_name)  
        # 保存文件到路径
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"{pkg_name} download success!")

def check_pkg_already_download(pkg_name):
    if os.path.exists(DOWANLOAD_FOLDER + "/" + pkg_name):
        print(f"{pkg_name}文件存在")
        return True
    else:
        print(f"{pkg_name}文件不存在")
        return False

# 将中文字符串转换为 HTTP 编码
def chinese_to_http(chinese_str):
    return urllib.parse.quote(chinese_str)

#删除下载的包
def delete_download_file_by_name(filename):
    file_path = os.path.join(DOWANLOAD_FOLDER, filename)
    try:
        # 检查是否为文件并删除
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"已删除文件: {file_path}")
            return True
    except Exception as e:
        print(f"删除文件时发生错误: {e}")
        return False
    return None

def connect_ftp_server():
    try:
        print("开始连接 FTP 服务器...")
        # 使用 SOCKS 代理连接 FTP
        socks.set_default_proxy(socks.HTTP, PROXY_HOST, PROXY_PORT, True, PROXY_USER, PROXY_PSW)
        socket.socket = socks.socksocket

        # 创建 FTP 客户端
        ftp = FTP()

        # 连接到 FTP 服务器
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PSW)
        print("FTP 连接成功.")
        return ftp
    except Exception as e:
        print(f"FTP 连接发生错误: {e}")
        return None

def disconnect_ftp_server(ftp):
    if ftp is not None:
        try:
            ftp.quit()  # 安全断开 FTP 连接
            print("FTP 连接已断开.")
            return True
        except Exception as e:
            print(f"断开 FTP 连接时发生错误: {e}")
            return False
    else:
        print("没有可断开的 FTP 连接.")
        return None

def check_ftp_file_exists(ftp, target_file):
    if ftp is None:
        print("检查ftp文件时没有可用的 FTP 连接.")
        return False
    try:
        # 获取当前目录下的文件列表 ftp.nlst() 如果不传则是根目录
        files = ftp.nlst(UPLOAD_PATH)
        print(f"当前ftp目录下的文件列表: {files}")
        # 检查目标文件是否在文件列表中
        if target_file in files:
            print(f"文件 '{target_file}' 存在于 FTP 服务器上.")
            return True
        else:
            print(f"文件 '{target_file}' 不存在于 FTP 服务器上.")
            return False
    except Exception as e:
        print(f"检查ftp文件发生错误: {e}")
        return False

def upload_file_to_ftp(file_name, target_name):
    #file_path = "./apps/package/" + file_name
    file_path = DOWANLOAD_FOLDER + file_name
    #target_path = "/package/autoupload/" + target_name
    target_path = UPLOAD_PATH + target_name
    ftp = connect_ftp_server()
    if ftp is None or ftp == False:
        msg = "连接 FTP 服务器失败，上传失败."
        print(msg)
        return False, msg
    # 检查文件是否已经存在于 FTP 服务器上
    if check_ftp_file_exists(ftp, target_name):
        msg = f"{target_name} 已经存在于 FTP 服务器上，上传失败."
        print(msg)
        return False, msg
    try:
        print("开始上传文件到 FTP 服务器...")
        # 上传文件
        with open(file_path, "rb") as f:
            ftp.storbinary(f"STOR {target_path}", f)
        msg=f"{target_path}上传成功"
        return True, msg
    except Exception as e:
        msg = f"发生错误: {e}"
        return False, msg
    finally:
        disconnect_ftp_server(ftp)

