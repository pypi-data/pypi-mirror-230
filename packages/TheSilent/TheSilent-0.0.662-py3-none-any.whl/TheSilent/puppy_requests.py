import http.client
import re
import socket
import ssl
import time
import urllib.parse
from TheSilent.return_user_agent import *

verify = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
verify.check_hostname = False
verify.verify_mode = ssl.CERT_NONE

RED = "\033[1;31m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"

fake_headers = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Encoding":"deflate",
                "Accept-Language":"en-US,en;q=0.5",
                "Referer":"https://www.google.com/",
                "User-Agent":return_user_agent(),
                "UPGRADE-INSECURE-REQUESTS":"1"}

def getheaders(host,method="GET",params={},headers={},timeout=30):
    path = urllib.parse.urlparse(host).scheme + "://" + urllib.parse.urlparse(host).netloc
    path = host.replace(path, "")

    if host.startswith("https://"):
        my_request = http.client.HTTPSConnection(urllib.parse.urlparse(host).netloc,timeout=timeout,context=verify)

    else:
        my_request = http.client.HTTPConnection(urllib.parse.urlparse(host).netloc,timeout=timeout)

    if len(headers) > 0:
        if len(params) > 0:
            my_request.request(method=method,url=path,body=urllib.parse.urlencode(params),headers=headers)
            simple_respone = my_request.getresponse()
            return simple_respone.getheaders()

        else:
            my_request.request(method=method,url=path,headers=headers)
            simple_respone = my_request.getresponse()
            return simple_respone.getheaders()

    else:
        if len(params) > 0:
            my_request.request(method=method,url=path,body=urllib.parse.urlencode(params),headers=fake_headers)
            simple_respone = my_request.getresponse()
            return simple_respone.getheaders()

        else:
            my_request.request(method=method,url=path,headers=fake_headers)
            simple_respone = my_request.getresponse()
            return simple_respone.getheaders()

def history(host,method="GET",params={},headers={},timeout=30):
    path = urllib.parse.urlparse(host).scheme + "://" + urllib.parse.urlparse(host).netloc
    path = host.replace(path, "")

    host_list = [host]
    for _ in range(1000):
        redirect = status_code(host,method,params,headers,timeout)
        if redirect.startswith("30"):
            header = str(getheaders(host,method,params,headers,timeout)).replace("'", "").replace('"', "")
            host = re.findall("location,\s*(\S+)\)", header.lower())[0]
            host_list.append(host)

        if not redirect.startswith("30"):
            break

    return host_list

def status_code(host,method="GET",params={},headers={},timeout=30):
    path = urllib.parse.urlparse(host).scheme + "://" + urllib.parse.urlparse(host).netloc
    path = host.replace(path, "")

    if host.startswith("https://"):
        my_request = http.client.HTTPSConnection(urllib.parse.urlparse(host).netloc,timeout=timeout,context=verify)

    else:
        my_request = http.client.HTTPConnection(urllib.parse.urlparse(host).netloc,timeout=timeout)

    if len(headers) > 0:
        if len(params) > 0:
            my_request.request(method=method,url=path,body=urllib.parse.urlencode(params),headers=headers)
            simple_respone = my_request.getresponse()
            return str(simple_respone.status)

        else:
            my_request.request(method=method,url=path,headers=headers)
            simple_respone = my_request.getresponse()
            return str(simple_respone.status)

    else:
        if len(params) > 0:
            my_request.request(method=method,url=path,body=urllib.parse.urlencode(params),headers=fake_headers)
            simple_respone = my_request.getresponse()
            return str(simple_respone.status)

        else:
            my_request.request(method=method,url=path,headers=fake_headers)
            simple_respone = my_request.getresponse()
            return str(simple_respone.status)

def text(host,method="GET",params={},headers={},timeout=30,raw=False):
    path = urllib.parse.urlparse(host).scheme + "://" + urllib.parse.urlparse(host).netloc
    path = host.replace(path, "")
    
    for _ in range(1000):
        redirect = status_code(host,method,params,headers,timeout)
        if redirect.startswith("30"):
            header = str(getheaders(host,method,params,headers,timeout)).replace("'", "").replace('"', "")
            host = re.findall("location,\s*(\S+)\)", header.lower())[0]

        if not redirect.startswith("30"):
            break

    if host.startswith("https://"):
        my_request = http.client.HTTPSConnection(urllib.parse.urlparse(host).netloc,timeout=timeout,context=verify)

    else:
        my_request = http.client.HTTPConnection(urllib.parse.urlparse(host).netloc,timeout=timeout)

    if len(headers) > 0:
        if len(params) > 0:
            my_request.request(method=method,url=path,body=urllib.parse.urlencode(params),headers=headers)
            simple_respone = my_request.getresponse()
            if not raw:
                return simple_respone.read().decode(errors="ignore").replace("\r","")

            if raw:
                return simple_respone.read()

        else:
            my_request.request(method=method,url=path,headers=headers)
            simple_respone = my_request.getresponse()
            if not raw:
                return simple_respone.read().decode(errors="ignore").replace("\r","")

            if raw:
                return simple_respone.read()

    else:
        if len(params) > 0:
            my_request.request(method=method,url=path,body=urllib.parse.urlencode(params),headers=fake_headers)
            simple_respone = my_request.getresponse()
            if not raw:
                return simple_respone.read().decode(errors="ignore").replace("\r","")

            if raw:
                return simple_respone.read()

        else:
            my_request.request(method=method,url=path,headers=fake_headers)
            simple_respone = my_request.getresponse()
            if not raw:
                return simple_respone.read().decode(errors="ignore").replace("\r","")

            if raw:
                return simple_respone.read()
