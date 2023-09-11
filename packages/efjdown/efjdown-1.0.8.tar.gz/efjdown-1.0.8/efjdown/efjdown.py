import re
import os
import tqdm
import time
import requests
import argparse
import configparser
from pathlib import Path
from loguru import logger

logo = """
███████╗███████╗         ██╗██████╗  ██████╗ ██╗    ██╗███╗   ██╗
██╔════╝██╔════╝         ██║██╔══██╗██╔═══██╗██║    ██║████╗  ██║
█████╗  █████╗█████╗     ██║██║  ██║██║   ██║██║ █╗ ██║██╔██╗ ██║
██╔══╝  ██╔══╝╚════╝██   ██║██║  ██║██║   ██║██║███╗██║██║╚██╗██║
███████╗██║         ╚█████╔╝██████╔╝╚██████╔╝╚███╔███╔╝██║ ╚████║
╚══════╝╚═╝          ╚════╝ ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝
                         - ver: 1.0.7 -                                                                                              
"""


class ArtifactoryStructDownloader(object):
    """
    for download some artifactory url as origin struct  desc it in one word is "SYNC"
    eg:ArtifactoryStructDownloader.download_artifactory_directory(url,save_path)
    """

    def __init__(self):
        self.save_path = None
        self.header = None
        self.download_count = 0

    @staticmethod
    def load_token():
        config = configparser.ConfigParser()
        config.read(os.path.join(str(Path.home()), '.efgdown_config.ini'))
        return config['Token']['token']

    @staticmethod
    def clean_token():
        if os.path.exists(os.path.join(str(Path.home()), '.efgdown_config.ini')):
            os.remove(os.path.join(str(Path.home()), '.efgdown_config.ini'))
            logger.success("clean token success.")
        else:
            logger.warning("can not find token file, please check your token file path.")

    @staticmethod
    def save_token(token):
        config = configparser.ConfigParser()
        config['Token'] = {'token': token}
        with open(os.path.join(str(Path.home()), '.efgdown_config.ini'), 'w') as configfile:
            config.write(configfile)

    @staticmethod
    def find_all_link_by_html(html_content):
        pattern = r'<a\s+href="([^"]+)"'
        matches = re.findall(pattern, html_content)
        if matches:
            pass
        else:
            logger.warning("can not find any link on this site. please review if the link is error.")
        return matches

    def download_file(self, url, save_path):
        response = requests.get(url, headers=self.header, stream=True)
        logger.info(f'Downloading {url}')
        if response.status_code == 200:
            data_len = round(int(response.headers.get('Content-Length', 0))) / 1024 / 1024
            try:
                with open(save_path, "wb") as file:
                    for data_block in tqdm.tqdm(iterable=response.iter_content(1024 * 1024), total=data_len,
                                                desc=f"Downloading {os.path.basename(url)}", unit="MB"):
                        file.write(data_block)
                self.download_count += 1
            except Exception as e:
                logger.error(f"[ERROR] save path access error, {save_path, e}")
                logger.warning(f"[HINT] check your save path {save_path} is valid.")
        else:
            logger.error(f"[ERROR] Failed to download {url, response.status_code}")

    def download_artifactory_directory(self, url, save_path):
        """
        save path will auto create, do not need mkdir first
        """
        if not self.save_path:
            self.save_path = save_path
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        # 如果是超大文件会卡住，因此需要判断下head是不是html，如果不是html 直接跳过
        rep_header = requests.head(url, headers=self.header)
        content_type = rep_header.headers.get('Content-Type', '')
        if 'text/html' not in content_type:
            logger.debug(f"find file {url}, directly download it.")
            self.download_file(url, save_path)
            return


        rsp = requests.get(url, headers=self.header)
        rsp_code = rsp.status_code
        rsp_text = rsp.text
        if rsp_code == 200:
            links = ArtifactoryStructDownloader.find_all_link_by_html(rsp_text)
            
            # 如果link返回空检查其是文件还是网页，如果是文件直接下载，如果是网页就跳过
            if not links:
                if url.endswith('/'):
                    logger.warning(f"[HINT] {url} is a empty folder, skip it.")
                else:
                    logger.debug(f"find file {url}, directly download it.")
                    self.download_file(url, save_path)
            for link in links:
                if link == '../':
                    continue
                item_url = url + "/" + link
                item_path = os.path.join(save_path, link)
                if link.endswith('/'):
                    logger.debug(f"find folder {link},visit it and for again.")
                    self.download_artifactory_directory(
                        item_url, item_path)
                else:
                    logger.debug(f"find file {link}, directly download it.")
                    self.download_file(item_url, item_path)
        else:
            logger.error(f"[ERROR] get {url} error, error code is {rsp_code}")
            logger.warning(f"[HINT] check your url is correct {url} and your token {self.header} is valid.")
            logger.warning(f"[HINT] if target is a file DONT write the filename at save_path.")

    def print_file_tree(self, root=None, prefix=""):
        if root is None:
            root = self.save_path
        if os.path.isdir(root):
            items = os.listdir(root)
            files = [f for f in items if os.path.isfile(os.path.join(root, f))]
            dirs = [d for d in items if os.path.isdir(os.path.join(root, d))]
            for i, item in enumerate(sorted(dirs) + sorted(files)):
                path = os.path.join(root, item)
                if i == len(items) - 1:
                    new_prefix = prefix + "└── "
                    new_prefix_subs = prefix + "    "
                else:
                    new_prefix = prefix + "├── "
                    new_prefix_subs = prefix + "│   "
                if os.path.isdir(path):
                    logger.info(f"{new_prefix}{item}/")
                    self.print_file_tree(path, new_prefix_subs)
                else:
                    size = os.path.getsize(path) / (1024 * 1024)  # 文件大小以MB为
                    logger.info(f"{new_prefix}{item} ({size:.4f} MB)")
        else:
            logger.info(f"File Tree of {root}:")
            logger.info(f"└── {os.path.basename(root)}")


def main():
    try:
        start_time = time.time()
        # 根据路径递归遍历，生成文件树形结构图
        parser = argparse.ArgumentParser(description='Enflame Artifactory Struct Downloader')
        parser.add_argument('-u', '--url', type=str, required=False, help='artifactory url')
        parser.add_argument('-p', '--save_path', type=str, required=False, help='save path')
        parser.add_argument('-t', '--token', type=str, required=False, help='public account token')
        parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0.0')
        parser.add_argument('-c', '--clean', action='store_true', help='clean token')
        parser.add_argument('-l', '--list', action='store_true', help='list file tree')
        args = parser.parse_args()
        if args.clean and not (args.url or args.save_path or args.token):
            # 处理清理token的情况
            ArtifactoryStructDownloader.clean_token()
            pass
        elif args.url and args.save_path:
            _url = args.url
            _save_path = args.save_path
            _token = args.token

            efjdown = ArtifactoryStructDownloader()
            # if the token is set by args, use it, else use the token in config.ini
            if _token:
                if 'Bearer' not in _token:
                    _token = f"Bearer {_token}"
                else:
                    _token = _token
                efjdown.header = {'Authorization': f'Bearer {_token}'}
            else:
                if not os.path.exists(os.path.join(str(Path.home()), '.efgdown_config.ini')):
                    logger.info(
                        "Welcome to Enflame Artifactory Struct Downloader, Detect that you have not set the token yet. ")
                    token = input("Please enter your public account token:")
                    ArtifactoryStructDownloader.save_token(token)
                    try:
                        efjdown.header = {'Authorization': f'Bearer {efjdown.load_token()}'}
                    except Exception as e:
                        logger.error(f"Maybe save config or read config is fail, please check error:{e}")
                else:
                    token = ArtifactoryStructDownloader.load_token()
                    efjdown.header = {'Authorization': f'Bearer {token}'}
            efjdown.download_artifactory_directory(_url, _save_path)
            if args.list:
                efjdown.print_file_tree()
            logger.success(f"{efjdown.download_count} file total, download cost "
                           f"{time.strftime('%Hhours %Mmin %Ssec', time.gmtime(time.time() - start_time))},"
                           " have a nice day!")
        else:
            logger.info(logo)
            parser.print_help()
    except KeyboardInterrupt:
        logger.success("Bye~ see you next time.")


if __name__ == "__main__":
    main()
