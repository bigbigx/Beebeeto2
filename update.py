#!/usr/bin/env python
#coding=utf-8
import urllib
import urllib2
import os
import sys
import socket
from util.BeautifulSoup import BeautifulSoup
import re
import time
import platform


g_cookie = 'csrftoken=jLySq58kvH7DW23sxIUwkVPpsOMStUdX; sessionid=8g49ri43mn8fgmic41gd1nt9x1ati6v1; CNZZDATA1253290531=1433061732-1414286034-%7C1414824533'
g_readme_head = ''' <html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<style type="text/css">
<!--
body {  FONT-FAMILY: verdana;  font-size: 10pt; color: #000000} 
-->
</style>
<title>POC LIST</title>
</head>
<body bgcolor="#FFFFFF">     
'''

def isWindow():
    return "Window" in platform.platform()


def format_dos(info):
    if not isWindow():
        return info

    try:
        return str(info).decode("utf8").encode("gbk")
    except:
        return info


def strip_tags(html):
    html = html.replace('&nbsp;', ' ')  
    html = html.replace('&gt;', '>')  
    html = html.replace('&lt;', '<') 
    html = html.replace('&quot;', '"') 
    html = html.replace('&#39;', "'") 
    html = html.replace('&amp;', "&") 
    html = ''.join(html)
    html = html[html.find('#!/'):]

    return format_dos(html)


def getHtml(url):
    info= ''
    for i in range(3):
        try:
            req = urllib2.Request(url)
            req.add_header('Cookie', g_cookie) 
            info = urllib2.urlopen(req).read()
            break
        except Exception,e:
            time.sleep(i+1)
            continue

    return info


def getPoc(poc):
    info = getHtml("http://beebeeto.com/pdb/" + poc + "/")
    if '' == info:
        return ''
    if '<img src="/static/img/test.jpg"' in info:
        return ''
    if "立即查看" in info:
        return ''

    try:
        bt = BeautifulSoup(info)
        ret = bt.find('pre', {'class' : "brush: python;"})
        ret = ret.renderContents()
        if ret: 
            return strip_tags(ret)
        else:
            return ''
    except:
        return ''

def makeReadme(name, info):
    ret = re.findall("'name'.*", info)
    if ret == '':
        print info,name
        return
    if len(ret) == 0:
        print info,name
        return

    info = ret[0].replace("'name'", "")
    info = info.replace(":", "")
    info = info.replace("'", "")
    info = info.replace(",", "")
    info = info.strip()
    
    if not os.path.exists("./poc/readme.html"):
        with open("./poc/readme.html", 'w') as fp: 
            fp.write(g_readme_head)          

    info = "[<a href=%s>%s<a>]%s\r\n<br>" % ("http://beebeeto.com/pdb/"+name, name, info)
    with open("./poc/readme.html", 'a') as fp: fp.write(info)


def savePoc(name, info):
    if '' == info:
        return

    name = name.replace("-", "_")
    sname = "./poc/" + name + ".py"
    if os.path.exists(sname):
        return

    with open(sname, "wb") as fp:
        fp.write(str(info))

    makeReadme(name, info)


def get_onepage_poclist(page):
    info = getHtml("http://beebeeto.com/pdb" + '/?page=' + str(page))
    if '' == info:
        return ''

    bt = BeautifulSoup(info)
    end = bt.find('a', {'style' : "font-size: 20px;font-weight: bold; border-bottom: 3px solid #777777;"})
    if '1' == end.renderContents() and page != 1:
        return ''

    ret = bt.find('div', {'class' : 'mainlist'})
    ret = ret.renderContents()
    if ret == "":
        return ""

    retlist = []
    rets = re.findall('<a href=.*?>', ret)
    for one in rets:
        if "poc-" in one:
            one = one.replace('<a href="', "")
            one = one.replace('">', "")
            one = one.strip()
            retlist.append(one)
      
    return retlist


def main():
    sum = 0
    socket.setdefaulttimeout(10)
    info = getHtml("http://beebeeto.com/")
    if "注册" in info and "登录" in info:
        print "[ERR] The cookie is error!"
        return

    readme = ""
    if os.path.exists("./poc/readme.html"):
        with open("./poc/readme.html", 'r') as fp: readme = fp.read()

    for i in range(1,1000):
        pocs = get_onepage_poclist(i)
        if "" == pocs:
            break

        for t in pocs:
            name = t.replace("-", "_")
            if name in readme:
                #print "[*] Get Poc -> %s " % t
                continue

            info = getPoc(t)
            if info == "": 
                 print "[*] Get Poc -> %s failed" % t
                 continue

            print "[+] Get Poc -> %s " % t
            savePoc(t, info)
            sum = sum + 1
            #return

    print "[+] The total number of POC is %d " % sum


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "usage: update.py cookie"
        sys.exit()
    else:
        g_cookie = sys.argv[1]

    main()
    #info = getPoc("poc-2014-0115")
    #savePoc('poc-2014-0115', info)
    #open('txt.html', 'w').write(str(info))
