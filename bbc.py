#!/usr/bin/env python2
#encoding=utf-8

import requests
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
import subprocess
import random
import time


def hangshu(wenjian):
    n=0
    with open(wenjian) as f:
        for i in f:
            n+=1
    f.close()
    return n


def dinhang(n,wenjian):
    q=1
    res=''
    with open(wenjian) as f:
        for i in f:
            if q==n:
                res=i.replace('\r\n','').replace('\n','')
            q+=1
    return res

def gettoutiao(zhuye):
    while True:
        try:
            html = requests.get(zhuye,verify=False,timeout=10)
            break
        except:
            continue
    html.encoding='utf-8'
    bs1 = html.text.encode('utf')
 
    start=0
    for i in bs1.split('\n'):
        if re.search('id="page-title"',i):
            start=1
        if start==1 and re.search('href',i):
            shouye=re.findall('href="(.+)"',i)[0]
            break

    shouyewangzhi=zhuye+shouye

    return(shouyewangzhi)
    

def getcontent(wangzhi):
    while True:
        try:
            html = requests.get(wangzhi,verify=False,timeout=10)
            break
        except:
            continue
    html.encoding='utf-8'
    bs1 = html.text.encode('utf')
    
    f=open('./neirong.tmp','wb')
    dayin=0
    for i in bs1.split('\n'):
        if re.search('class="story-body"',i):
            dayin=1
        if dayin==1:
            f.write(i)
            f.write('\n')
    f.close()

    f2=open('./youjian.tmp','wb')
    f2.write('<html>')
    f2.write('\n')
    f2.write('<body>')
    f2.write('\n')

    biaoti=''
    dayin2=0
    with open('./neirong.tmp','rb') as f3:
        for i in f3:
            if re.search(r'<h1 class="story-body__h1">(.*)</h1>',i):
                biaoti=re.findall(r'<h1 class="story-body__h1">(.*)</h1>',i)[0]
            if re.search('class="story-body__introduction"',i):
                f2.write(i.replace('</figure>',''))
                f2.write('\n')
                dayin2=1
                continue
            if dayin2==1 and not re.search('Related Topics|Share this story',i):
                f2.write(i)
                f2.write('\n')
                continue
            if dayin2==1 and re.search('Related Topics|Share this story',i):
                dayin2=0
                break

    f3.close()

    f2.write('</body>')
    f2.write('\n')
    f2.write('</html>')
    f2.write('\n')
    f2.close()

    return(biaoti)

def zhengxing(wenjian):
    ok=[]
    reg=r'src="(.*?\.jpg|.*?\.png)'
    imgre=re.compile(reg)

    with open(wenjian,'rb') as f:
        for i in f:
            if re.search(imgre,i):
                ok=ok+re.findall(imgre,i)
    f.close()

    for i in ok:
        jpgfile="./pic/"+i.split('/')[-1]
        num=6
        while num>0:
            try:
                res=requests.get(i,verify=False,timeout=6)
                break
            except:
                num-=1
                
        with open(jpgfile,'wb') as f:
            f.write(res.content)
        f.close()

    fn=open('%s.tmp'%wenjian,'wb')
    with open(wenjian,'rb') as fo:
        for i in fo:
            for j in ok:
                if re.search(j,i):
                    t1=j.split('/')[:-1]
                    t2='/'.join(t1)+'/'
                    fn.write(re.sub(t2,'cid:',i)) 
                else:
                    fn.write(i)
    fo.close()
    fn.close()
    subprocess.call('cp %s.tmp %s'%(wenjian,wenjian),shell=True)
            

def fayoujian(wenjian,biaoti):
    msg = MIMEMultipart()
    msg['Subject'] = biaoti
    msg['From'] = "my_news@m1.sg"
    msg['To'] = "zou.jun@zte.com.cn,zouj2003@qq.com"

    text = open(wenjian,'rb')
    msg.attach(MIMEText(text.read(),'html','GBK'))
    text.close()

    tolist = ["zou.jun@zte.com.cn","zouj2003@qq.com"]
    s = smtplib.SMTP('127.0.0.1')
    s.sendmail("my_news@m1.sg",tolist,msg.as_string())
    s.quit()

def fayoujian_ql(wenjian,biaoti):
    msg = MIMEMultipart()
    msg['Subject'] = biaoti
    msg['From'] = "my_news@m1.sg"
    msg['To'] = "zou.jun@zte.com.cn,zouj2003@qq.com,zouql2000@qq.com"

    text = open(wenjian,'rb')
    msg.attach(MIMEText(text.read(),'html','GBK'))
    text.close()

    tolist = ["zou.jun@zte.com.cn","zouj2003@qq.com","zouql2000@qq.com"]
    s = smtplib.SMTP('127.0.0.1')
    s.sendmail("my_news@m1.sg",tolist,msg.as_string())
    s.quit()

if __name__=="__main__":
    os.chdir('/root/py/bbcnews')
    toutiao=gettoutiao('https://www.bbc.com')
    title=getcontent(toutiao)
    lastwangye=dinhang(1,'./lastrec')
    lastbiaoti=dinhang(2,'./lastrec')
    lasthangshu=dinhang(3,'./lastrec')
#    zhengxing('./youjian.tmp')
    newhangshu=str(hangshu('./youjian.tmp'))

    bishijian=time.strftime("%H%M", time.localtime())

#    if hangshu('./youjian.tmp')>5 and (lastwangye!=toutiao or lastbiaoti!=title or (lastwangye==toutiao and int(newhangshu)-int(lasthangshu)>50 and int(lasthangshu)<=100)):
    if hangshu('./youjian.tmp')>5 and (lastwangye!=toutiao or (lastwangye==toutiao and int(newhangshu)-int(lasthangshu)>50 and int(lasthangshu)<=100)):
        if bishijian>'1600':
            fayoujian_ql('./youjian.tmp',title)
        else:
            fayoujian('./youjian.tmp',title)
        fn=open('./lastrec','wb')
        fn.write(toutiao)
        fn.write('\n')
        fn.write(title)
        fn.write('\n')
        fn.write(newhangshu)
        fn.close()
        
#    subprocess.call('rm ./pic/*',shell=True)
