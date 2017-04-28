#!/usr/bin/python
# Filename udt.py
from collections import defaultdict
import telnetlib
import os,sys,commands,multiprocessing
import smtplib  
import time
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText  
from email.mime.image import MIMEImage  
#-------config------------------
allarpmacfile = '/root/gitHub/udt/allarpmac.html'
pythonlog =  '/root/mylog.txt'
history_path =  '/root/gitHub/udt/macarpbak/'
getMacArp_py_path = '/root/gitHub/udt/getMacArp.py'

if(len(sys.argv) != 3):
    print "please input ip or mac !</p>"
    print "MAC example: 90b1.1c94.c1fb</p>"
    print "IP example: 10.10.8.30</p>"
    sys.exit()

ipormac = sys.argv[1]
s_or_his = sys.argv[2]

if (ipormac.count('.') <= 1)|(ipormac.count('*') > 0)|(ipormac.count('.') >= 4):
    print "content not ip or mac "
    sys.exit()

def main(_ipormac,_allarpmacfile):
    logtime =  time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    arpsearch_cmd = "grep 'ARP.*."+_ipormac+" ' "+ _allarpmacfile
    os.system("echo "+ logtime +" UDT be using now  ! cmd:"+arpsearch_cmd+" >> "+pythonlog)  # log to mylog.txt
    #print arpsearch_cmd
    tagidstr =  os.popen(arpsearch_cmd,'r').read()
    #print tagidstr
    tagidcount =  tagidstr.count('\n')
    if (tagidcount == 0):
        print "No result!"+"</p>"

    for tagidindex in xrange(tagidcount):
        tagid =  tagidstr.split('\n')[tagidindex].split()[0]
        macsearch_cmd = "awk  -vbb="+tagid+" '{if ($1==bb){print $2,$3,$4,$5,$6}}' "+_allarpmacfile
        #print macsearch_cmd
        allresult =  os.popen(macsearch_cmd,'r').read()
        allresult_count =  allresult.count('\n')
        for resultindex in xrange(allresult_count):
            #print resultindex 
            if (resultindex == 0):    #the first line is arp info
                print '<font color="red">'+allresult.split('\n')[resultindex]+'</font>'+'</p>'
            else:                     #other line is mac-address info
                print allresult.split('\n')[resultindex]+'</p>'
        if (allresult_count == 1):
            print "no mac-address infomation!"+'</p>'

if __name__ == "__main__":
    if (s_or_his == 'search'):
        main(ipormac,allarpmacfile)
        sys.exit()
    if (s_or_his == 'history'):
        #print history_path
        listdirstr =  os.listdir(history_path)
        listdirstr = sorted(listdirstr,reverse=True)
        #print listdirstr
        #print len(listdirstr)
        if (len(listdirstr)>500):
            print '<font color="green">'+">>>>>>>>>Warning: history list > 500, please rm some XXX.arpmacbak <<<<<<<<"+'</font>'
        for arpmacbak_line in listdirstr:
            print '</p><b>['+'history file: '+arpmacbak_line+']</b></p>'
            main(ipormac,history_path+arpmacbak_line)
        sys.exit()
    if (s_or_his == 'update'):
         os.system('python '+ getMacArp_py_path )  
         print '<font color="green">'+"GetAllArpMac  successful ! "+'</font>'
