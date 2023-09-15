import argparse as arg
import os
import configparser
from .util import download_from_nas, list_file, upload, init, uploadshare, share

def bmcompiler_parser():
    parser = arg.ArgumentParser(description     = "handle nas with command line",
                                formatter_class = arg.ArgumentDefaultsHelpFormatter,
                                prog            = "python -m dtools")
    
    parser.add_argument("method", choices=["download", "upload", "list", "init", "share", "upshare"], help="download or upload, you can do init first to avoid enter username and passwd  everytime")
    
    # upload file argments : name, password, local_dir, nas_dir
    parser.add_argument("--name", type=str,help="username")
    parser.add_argument("--password", type=str,help="password")
    parser.add_argument("--local_dir", type=str,help="local dir")
    parser.add_argument("--nas_dir", type=str,help="nas dir. Attention : \n \
        1. if the nas_dir is not exist, it will be created automatically. \n \
        2. And usually you should set nas_dir as /home/xxxx. \n \
        3. upload mode and target name is not support now. ")
    parser.add_argument('--verbose', type=bool, default=False, help='verbose')
    parser.add_argument("--sharetime", type=int, default=30, help="the share link available time : \n \
                        1. if the sharetime is not set, the default time is 30 days. \n \
                        2. the sharetime will be 1000 days if you set -1.")
    return parser

def check_user_info(parser):
    if parser.password and parser.name:
        pw = parser.password
        un = parser.name
    elif os.path.exists(os.path.expanduser("~/.nasops.ini")):
        cfg = configparser.ConfigParser()
        cfg.read(os.path.expanduser("~/.nasops.ini"))
        un = cfg.get("SophonNas", "username")
        pw = cfg.get("SophonNas", "password")
    else:
        assert("no username,password given or no config file found, please enter username and password or do init first")
    return un, pw

def main():
    parser = bmcompiler_parser()
    a = parser.parse_args()

    if a.method == 'download':
        download_from_nas(a.url)
    
    if a.method == 'upload':
        un, pw = check_user_info(a)
        upload(un, pw, a.local_dir, a.nas_dir)

    if a.method == 'upshare':
        un, pw = check_user_info(a)
        uploadshare(un, pw, a.local_dir, a.nas_dir, a.sharetime)

    if a.method == 'share':
        un, pw = check_user_info(a)
        share(un, pw, a.nas_dir, a.sharetime)

    if a.method == 'list':
        un, pw = check_user_info(a)
        list_file(un, pw, a.nas_dir)
    
    if a.method == 'init': 
        if os.name == "posix":
            if a.name and a.password:
                init(a.name, a.password)
            else:
                assert("please set your username and password when init")
        else:
            assert("not supported")

if __name__ == "__main__":
    main()