import json 
import os
import time
import requests
from tqdm import tqdm
import configparser

import base64

# 将 PUBLIC_PREFIX 转换为 base64 编码
PUBLIC_PREFIX = "https://disk.sophgo.vip"
def fix_url(url):
    prefix = url.split('/')[2]
    return PUBLIC_PREFIX+url.split(prefix)[1]

def judge(url):
    return url.split("/")[3] == "sharing"

def _get_file_name(url):
    if judge(url):
        id = url.split('/')[4]
        file_name_url = PUBLIC_PREFIX+"/sharing/webapi/entry.cgi?api=SYNO.Core.Sharing.Session&version=1&method=get&sharing_id=%22{}%22".format(id)
        file_name = requests.get(file_name_url).text.split('filename" : "')[1].split('"')[0]
    else:
        file_name = url.split("/")[-1]
    return file_name

def get_id(url):
    return url.split("/")[4]

def _get_sharing_id(url):
    res = requests.get(url)
    sharing_id = res.headers['Set-Cookie'].split('=')[1].split(';')[0]
    return sharing_id

def get_sharing_id(url):
    file_name = _get_file_name(url)
    if judge(url):
        sharing_id = _get_sharing_id(url)
    else:
        converted_url = url_convert(url)
        sharing_id = _get_sharing_id(converted_url)
    return sharing_id

def judge_if_need_process(url):
    if judge(url):
        file_name = _get_file_name(url)
        if len(file_name.split(".")) == 1:
            return "dir_o"
        else :
            return "single"
    else:
        return "dir"

def url_convert(url):
    if judge(url):
        ulist = url.split("/")
        converted_url = PUBLIC_PREFIX + "/fsdownload/" + get_id(url) + "/" + _get_file_name(url)
        return converted_url
    else:
        ulist = url.split("/")
        converted_url = PUBLIC_PREFIX + "/sharing/" + get_id(url)
        return converted_url

def get_file_name(url):
    return _get_file_name(url)+".zip" if judge_if_need_process(url) != "single" else _get_file_name(url)

def get_curl_cmd(url):
    fixed_url = fix_url(url)
    sharing_id = get_sharing_id(fixed_url)
    file_name = get_file_name(fixed_url)
    id = get_id(fixed_url)
    if judge_if_need_process(fixed_url) == "single":
        curl_cmd = 'curl -o ' + file_name + ' -b "sharing_sid=' + sharing_id \
            + '" "' + url_convert(fixed_url) + '"'
    else:
        post_data = "api=SYNO.FolderSharing.Download&method=download&version=2&mode=download&stdhtml=false&dlname=%22" \
            + file_name + "%22&path=%5B%22%2F" + file_name.split(".")[0] + "%22%5D&_sharing_id=%22" + id + "%22&codepage=chs"
        curl_cmd = 'curl -o ' + file_name + ' -H "Content-Type: application/x-www-form-urlencoded" -b "sharing_sid=' + sharing_id \
            + '" -X POST -d "' + post_data + '" "' + PUBLIC_PREFIX + '/fsdownload/webapi/file_download.cgi/' + file_name + '"'
    return curl_cmd

def download_from_nas(url):
    def download(resp, url):
        total = int(resp.headers.get('content-length', 0))
        fname = get_file_name(url)
        with open(fname, 'wb') as file, tqdm(
                desc=fname,
                total=total,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
        ) as bar:
            for data in resp.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)
    fixed_url = fix_url(url)
    sharing_id = get_sharing_id(fixed_url)
    file_name = get_file_name(fixed_url)
    id = get_id(fixed_url)
    cookie = {
        "sharing_sid":sharing_id
    }
    if judge_if_need_process(url) == "single":
        resp = requests.get( url = url_convert(fixed_url),cookies = cookie, stream=True)
        download(resp, fixed_url)
    else:
        url = PUBLIC_PREFIX + '/fsdownload/webapi/file_download.cgi/' + file_name
        post_data = "api=SYNO.FolderSharing.Download&method=download&version=2&mode=download&stdhtml=false&dlname=%22" \
                + file_name + "%22&path=%5B%22%2F" + file_name.split(".")[0] + "%22%5D&_sharing_id=%22" + id + "%22&codepage=chs"
        resp = requests.post( url = url,cookies = cookie, data = post_data, stream=True)
        download(resp, fixed_url)

def get_sid(username, password):
    ret = requests.get(f'{PUBLIC_PREFIX}/webapi/auth.cgi?api=SYNO.API.Auth&version=3&method=login&account={username}&passwd={password}&session=FileStation&format=sid')
    ret = json.loads(ret.content)
    if not ret['success']:
        ValueError("Login Failed! Please check your username and password!")
    _sid =ret['data']['sid']
    return _sid


def upload_file(sid, filename, nas_dir):
    # check filename is exist 
    if not os.path.exists(filename):
        ValueError(f'{filename} is not exist')
    
    # if nas_dir is not exist, will automatically create it 
    
    local_dir = os.path.dirname(filename)
    local_file_name = os.path.basename(filename)
    # print(f'uploading {filename} to {nas_dir} .... ')
    try:
        with open(os.path.join(local_dir,local_file_name), 'rb') as payload:
            args = {
                'path': nas_dir,
                'create_parents': 'true',
                'overwrite': 'true'
            } 
            files = {'file': (local_file_name, payload, 'application/octet-stream')}      
            uri=PUBLIC_PREFIX + r'/webapi/entry.cgi?api=SYNO.FileStation.Upload&version=2&method=upload&_sid=' + sid
            req=requests.post(uri, data=args, files=files, verify=True)
            # print("Success: \t",req.json())
    except Exception as e:
        print('upload %s error:%s' % (local_file_name,e))

def generate_data_expired(timelong=3600*24*30):
    current_time = int(time.time())
    end_time = current_time + timelong
     # return "YYYY-MM-DD"
    format_time = time.strftime("%Y-%m-%d", time.localtime(end_time))
    return format_time

def share(username=None, password=None, nas_dir=None, sharetime=30,sid=None):
    if not sid:
        assert username and password
        sid = get_sid(username, password)
    else:
        pass
    sharetime = 1000 if sharetime == -1 else sharetime
    timelong  = 3600*24*sharetime
    try:
        payload={
            "api":"SYNO.FileStation.Sharing",
            "version":3,
            "method":"create",
            "path": nas_dir,
            "date_expired": generate_data_expired(timelong),
        }
        url=PUBLIC_PREFIX + r'/webapi/entry.cgi'
        # 构造cookies
        cookies = {
            "id":sid
        }
        req=requests.get(url, params=payload, verify=True, cookies=cookies)
        req = req.json()
        print(req['data']['links'][0]['url'])
    except Exception as e:
        print(e)

def uploadshare(username, password, local_dir, nas_dir):
    # upload local_dir to nas_dir
    sid = get_sid(username, password)
    upload_dir(sid, local_dir, nas_dir)
    share(sid, nas_dir)
    print("upload success")

def upload_dir(sid, local_dir, nas_dir):
    # local_dir is file path, use upload_file to upload it
    # local_dir is dir path, use upload_dir to upload it
    if os.path.isfile(local_dir):
        upload_file(sid, local_dir, nas_dir)
    else:
        for each_file in tqdm(os.listdir(local_dir), leave=False):
            if os.path.isdir(os.path.join(local_dir,each_file)):
                upload_dir(sid, os.path.join(local_dir,each_file), nas_dir+"/"+each_file)
            else:
                upload_file(sid, os.path.join(local_dir,each_file), nas_dir)
    
def list_nas_files(sid, nas_dir="home"):
    # list all files in nas_dir
    uri=PUBLIC_PREFIX + r'/webapi/entry.cgi?api=SYNO.FileStation.List&version=2&method=list&_sid=' + sid
    args = {
        'folder_path': nas_dir,
        'additional': 'real_path,owner,time,perm,real_path',
        'limit': 1000,
        'offset': 0
    }
    try:
        req=requests.get(uri, params=args, verify=True)
        req = req.json()
        for each_file in req['data']['files']:
            print(each_file['name'])
    except Exception as e:
        ValueError(f'list {nas_dir} error: {e}')
    


def upload(username, password, local_dir, nas_dir):
    # upload local_dir to nas_dir
    sid = get_sid(username, password)
    upload_dir(sid, local_dir, nas_dir)
    print("upload success")

def uploadshare(username, password, local_dir, nas_dir, sharetime):
    # upload local_dir to nas_dir
    sid = get_sid(username, password)
    upload_dir(sid, local_dir, nas_dir)
    print("upload success! start to share")
    share(sid=sid, nas_dir=nas_dir, sharetime=sharetime)

def list_file(username, password, nas_dir="/home"):
    # list all files in nas_dir
    sid = get_sid(username, password)
    list_nas_files(sid, nas_dir)

def init(un, pw):
    config = configparser.ConfigParser()
    config["SophonNas"] = {
        "username" : un,
        "password" : pw
    }
    # with open(os.path.expanduser("~/.nasops.ini"), 'wb+') as cfg:
    with open(os.path.expanduser("~/.nasops.ini"), 'w') as cfg:
        config.write(cfg)
    print("init successfully")
