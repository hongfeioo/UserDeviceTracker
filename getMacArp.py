#!/usr/bin/python
# Filename ncm.py
from collections import defaultdict
import telnetlib
import os,sys,commands,multiprocessing
import smtplib  
import time
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText  
from email.mime.image import MIMEImage  

import sys
if not "/root/labroom" in sys.path:
    sys.path.append("/root/labroom")
import messageMode

#-------config------------------
allarpmacfilebakpath = '/root/gitHub/udt/macarpbak/'     
allarpmacbakpath = '/root/gitHub/udt/macarp/'     
devicefile = '/root/gitHub/udt/getMacArp.ini'            #Attention use full path 
allmacfile = '/root/gitHub/udt/allmac.txt'
allarpfile = '/root/gitHub/udt/allarp.txt'
allarpmacfile = '/root/gitHub/udt/allarpmac.html'
pythonlog =  '/root/mylog.txt'

sleep_time = 2                   #control the mutiprocess speed
linecount = 0
MAX_creatfile_process = 1         #mutiprocessing
usr = 'username'                     #switch username
pwd = 'password'                #switch password
pwd2 = ''                   #
receiver = 'yihf@liepin.com'

#---init paramater------
device_idct = defaultdict(lambda:defaultdict(dict))
L3arp_idct = defaultdict(lambda:defaultdict(dict))
L2mac_idct = defaultdict(lambda:defaultdict(dict))
begintime =  time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
#-------read file into idct-----------
file = open(devicefile)
for line in file.readlines():
    if (line.split()[0].find('#') >= 0)|(len(line) < 7)|(len(line.split())!=5): #jump the comments,jump short than 1.1.1.1
        #os.system("echo "+begintime+" getmacarp.py find line error  ! >> "+pythonlog)  # log to mylog.txt 
        continue
    else:
        device_idct[linecount]['ip'] = line.split()[0]
        device_idct[linecount]['type']= line.split()[1]  
        device_idct[linecount]['name']= line.split()[2]
        device_idct[linecount]['flag'] = line.split()[3]    #default flag is 3,this is a L3dev
        device_idct[linecount]['uplinkport'] = line.split()[4]    #default flag is 3,this is a L3dev
        linecount += 1    #line counter
file.close()
#print "linecount:",linecount

#sys.exit()


#--function cisco-nxos--
def cisco_nxos(ip,usr,pwd,_allmacfile,_allarpfile,_flag,_upport):
    '''get cisco nxos switch arp,mac
    '''
    #print ip[7:]
    #time.sleep(int(ip[7:]))
    successful_flag = 'ok'

    #---telnet,username,password------
    try:
        tn = telnetlib.Telnet(ip,23,5)
    except Exception,e:
        return "ip:"+ip+'-'+str(e)
    #---try to login------------
    try:
        login_keyword = tn.read_until("login: ",3)
    except Exception,e:
        return "ip:"+ip+'-'+str(e)
    if str(login_keyword).find('login') == -1:
        return "ip:"+ip+'-'+'not find the login keyword,you can try to change the login type!'

    tn.write(usr+"\n")
    tn.read_until("Password: ",3)
    tn.write(pwd+"\n")
    #------judge logined in ------
    try:
        logined_keyword = tn.read_until("#",3)
    except Exception,e:
        return "ip:"+ip+'-'+str(e)
    if str(logined_keyword).find('#') == -1:
        return "ip:"+ip+'-'+'not find the Enable  keyword,please check the user  password!'


    #print '1.begin to get mac\n'
    message = ''
    tn.write('sh mac address-table ' + '\n')
    while 1:
        message = tn.expect(['--More--'],3)
        new_batchline =  message[2]
        new_batchline_count = new_batchline.count('\n')               #count the line num. of this batch
        for index in range(0,new_batchline_count):
            if (new_batchline.split('\n')[index].count('.') >= 2)&(len(new_batchline.split('\n')[index].split()) == 8):  
                #filter no use information by count the num of dot,everyline must can be splited to 4 part
                try:
                    every_line_mac = ''
                    every_line_mac = 'Mgmt:' +ip +'\t'+ new_batchline.split('\n')[index].split()[2] + '\t' \
                                                  + new_batchline.split('\n')[index].split()[3] + '\t' \
                                                  + new_batchline.split('\n')[index].split()[1] + '\t' \
                                                  + new_batchline.split('\n')[index].split()[7] 
                    if (new_batchline.split('\n')[index].split()[2].count('.') == 2)&(new_batchline.split('\n')[index].split()[7] != _upport):
                        every_line_mac = every_line_mac.replace('(','')
                        every_line_mac = every_line_mac.replace(')','')
                        every_line_mac = every_line_mac + '\tGW:' +_flag
                        os.system('echo  '+every_line_mac+'  >> '+ _allmacfile)   # do not split() every line,or will error
                except Exception,e:
                    return str(e)
        tn.write(" ")
        #print "---> press enter "
        if (message[2].find('--More--') == -1):
            break

    print '1:'+ip+' '+'mac info get ready!'
    if (_flag.find('-') == -1):
        return successful_flag
       

    #print '2:begin to get arp !'
    message = ''
    tn.write('show ip arp' + '\n')
    while 1:
        message = tn.expect(['--More--'],3)
        new_batchline =  message[2]
        new_batchline_count = new_batchline.count('\n')               #count the line num. of this batch
        for index in range(0,new_batchline_count):
            if (new_batchline.split('\n')[index].count('.') >= 5)&(len(new_batchline.split('\n')[index].split()) == 4):  
                #filter no use information by count the num of dot,everyline must can be splited to 4 part
                every_line_arp = ''
                every_line_arp = 'Mgmt:' +ip +'\t'+ new_batchline.split('\n')[index].split()[2] + '\t' \
                                                  + new_batchline.split('\n')[index].split()[0] + '\t' \
                                                  + new_batchline.split('\n')[index].split()[3] 
                os.system('echo  '+every_line_arp+'  >> '+ _allarpfile)   # do not split() every line,or will error
                #print every_line_arp

        tn.write(" ")
        #print "---> press enter "
        press_flag = 1
        if (message[2].find('--More--') == -1):
            tn.write("exit\n")
            tn.close
            #print "5:No more info so  logout!"
            break
    print '2:'+ip+' '+'arp info get ready!'
    return successful_flag



#--function cisco-4500-sw--

def cisco_4500_sw(ip,usr,pwd,_allmacfile,_allarpfile,_flag,_upport):
    '''get cisco 4500 switch arp(= ciscosw,ciscorouter),mac
    '''
    message_list = ''
    message = ''
    successful_flag = 'ok'

    #---telnet,username,password------
    try:
        tn = telnetlib.Telnet(ip,23,5)
    except Exception,e:
        return "ip:"+ip+'-'+str(e)

    #---try to login----------
    try:
        login_keyword = tn.read_until("Username: ",3)
    except Exception,e:
        return "ip:"+ip+'-'+str(e)
    if str(login_keyword).find('Username:') == -1:
        return "ip:"+ip+'-'+'not find the login keyword,you can try to change the login type!'

    tn.write(usr+"\n")
    tn.read_until("Password: ",3)
    tn.write(pwd+"\n")


    #------judge logined in ------
    try:
        logined_keyword = tn.read_until("#",3)
    except Exception,e:
        return "ip:"+ip+'-'+str(e)
    if str(logined_keyword).find('#') == -1:
        return "ip:"+ip+'-'+'not find the Enable  keyword,please check the user  password!'

    tn.write('sh mac address-table ' + '\n')
    press_flag = 0 
    #---find the end of configuration and exit----
    while 1:
        message = tn.expect(['--More--'],3)
        if press_flag != 0:
            #print 'find . -->',new_batchline.find('.')
            new_batchline =  message[2][27:]
            #print new_batchline
        if press_flag == 0:
            new_batchline =  message[2]

        new_batchline_count = new_batchline.count('\n')               #count the line num. of this batch
        for index in range(0,new_batchline_count):
            if (new_batchline.split('\n')[index].count('.') >= 2)&(len(new_batchline.split('\n')[index].split()) == 5):  
                #filter no use information by count the num of dot,everyline must can be splited to 4 part
                every_line_mac = ''
                every_line_mac = 'Mgmt:' +ip +'\t'+ new_batchline.split('\n')[index].split()[1] + '\t' \
                                                  + new_batchline.split('\n')[index].split()[2] + '\t' \
                                                  + new_batchline.split('\n')[index].split()[0] + '\t' \
                                                  + new_batchline.split('\n')[index].split()[4] 
                
                if(new_batchline.split('\n')[index].split()[4] != _upport):
                    every_line_mac = every_line_mac + '\tGW:' +_flag
                    os.system('echo  '+every_line_mac+'  >> '+ _allmacfile)   # do not split() every line,or will error

        tn.write(" ")
        #print "---> press enter "
        press_flag = 1
        if (message[2].find('--More--') == -1):
            #print "5:No more info so  logout!"
            break
    print '1:'+ip+' '+'mac info get ready!'

    if (_flag.find('-') == -1):
        return successful_flag


    message = ''
    press_flag = 0 
    tn.write('show ip arp' + '\n')
    #print '2:show ip arp  !'
    #---find the end of configuration and exit----
    while 1:
        message = tn.expect(['--More--'],3)
        message_list += str(message[2])
        tn.write(" ")
        if (str(message[2]).find('--More--') == -1):
            tn.write("exit\n")
            tn.close
            #print "3:No more info so  logout!"
            break

    #print '-----\n',message_list,'-------\n'
    arp_all_count =  message_list.count('\n')
    #print 'arp all count:',ip,'--',arp_all_count         #can make mac Num. warning,include 'Incomplete '
    for index in range(0,arp_all_count):
        if (message_list.split('\n')[index].count('.') >= 5)&(len(message_list.split('\n')[index].split()) == 6):  
            #filter no use information by count the num of dot,everyline must can be splited to 6 parts
            every_line_ip_arp = ''
            every_line_ip_arp =  'Mgmt:'+ip+'\t'+message_list.split('\n')[index].split()[3]+'\t' \
                                  +message_list.split('\n')[index].split()[1]+'\t' \
                                  +message_list.split('\n')[index].split()[5] 
            os.system('echo  '+every_line_ip_arp+'  >> '+ _allarpfile)
    print '2:'+ip+' '+'arp info get ready!'
    return successful_flag


#--function cisco-router---
def ciscorouter(ip,usr,pwd,_allmacfile,_allarpfile,_flag,_upport):
    '''get cisco router arp(= ciscosw),mac
    '''
    message_list = ''
    message = ''
    successful_flag = 'ok'

    #---telnet,username,password------
    try:
        tn = telnetlib.Telnet(ip,23,5)
    except Exception,e:
        return "ip:"+ip+'-'+str(e)

    #---try to login----------
    try:
        login_keyword = tn.read_until("Username: ",3)
    except Exception,e:
        return "ip:"+ip+'-'+str(e)
    if str(login_keyword).find('Username:') == -1:
        return "ip:"+ip+'-'+'not find the login keyword,you can try to change the login type!'

    tn.write(usr+"\n")
    tn.read_until("Password: ",3)
    tn.write(pwd+"\n")


    #------judge logined in ------
    try:
        logined_keyword = tn.read_until("#",3)
    except Exception,e:
        return "ip:"+ip+'-'+str(e)
    if str(logined_keyword).find('#') == -1:
        return "ip:"+ip+'-'+'not find the Enable  keyword,please check the user  password!'

    tn.write('sh mac-address-table' + '\n')
    press_flag = 0 
    #---find the end of configuration and exit----
    while 1:
        message = tn.expect(['--More--'],3)
        if press_flag != 0:
            new_batchline =  message[2][27:]
        if press_flag == 0:
            new_batchline =  message[2]

        new_batchline_count = new_batchline.count('\n')               #count the line num. of this batch
        for index in range(0,new_batchline_count):
            if (new_batchline.split('\n')[index].count('.') >= 2)&(len(new_batchline.split('\n')[index].split()) == 4):    
                #filter no use information by count the num of dot,every line must can be split to 4 parts
                every_line_mac = ''
                every_line_mac = 'Mgmt:' +ip +'\t'+ new_batchline.split('\n')[index].split()[0] + '\t' \
                                                  + new_batchline.split('\n')[index].split()[1] + '\t' \
                                                  + new_batchline.split('\n')[index].split()[2] + '\t' \
                                                  + new_batchline.split('\n')[index].split()[3] 
                if(new_batchline.split('\n')[index].split()[3] != _upport):
                    every_line_mac = every_line_mac + '\tGW:' +_flag
                    os.system('echo  '+every_line_mac+'  >> '+ _allmacfile)   # do not split() every line,or will error

        tn.write(" ")
        #print "---> press enter "
        press_flag = 1
        if (message[2].find('--More--') == -1):
            break
    print '1:'+ip+' '+'mac info get ready!'

    if (_flag.find('-') == -1):
        return successful_flag
     

    message = ''
    tn.write('show ip arp' + '\n')
    #print '2:show ip arp  !'
    #---find the end of configuration and exit----
    while 1:
        message = tn.expect(['--More--'],3)
        message_list += str(message[2])
        tn.write(" ")
        if (str(message[2]).find('--More--') == -1):
            tn.write("exit\n")
            tn.close
            #print "5:No more info so  logout!"
            break

    #print '-----\n',message_list,'-------\n'
    arp_all_count =  message_list.count('\n')
    #print 'arp all count:',ip,'--',arp_all_count                     #c315an make mac Num. warning,include 'Incomplete '
    for index in range(0,arp_all_count):
        if (message_list.split('\n')[index].count('.') >= 5)&(len(message_list.split('\n')[index].split()) == 6):  
            #filter no use information by count the num of dot,everyline must can be splited to 6 parts
            every_line_ip_arp = ''
            every_line_ip_arp =  'Mgmt:'+ip+'\t'+message_list.split('\n')[index].split()[3]+'\t' \
                                  +message_list.split('\n')[index].split()[1]+'\t' \
                                  +message_list.split('\n')[index].split()[5] 
            os.system('echo  '+every_line_ip_arp+'  >> '+ _allarpfile)
    print '2:'+ip+' '+'arp info get ready!'
    return successful_flag
    
def ciscosw(ip,usr,pwd,_allmacfile,_allarpfile,_flag,_upport):
    '''get cisco switch arp(=cisco router),mac
    '''
    message_list = ''
    message = ''
    successful_flag = 'ok'

    #---telnet,username,password------
    try:
        tn = telnetlib.Telnet(ip,23,5)
    except Exception,e:
        return "ip:"+ip+'-'+str(e)

    #---try to login----------
    try:
        login_keyword = tn.read_until("Username: ",3)
    except Exception,e:
        return "ip:"+ip+'-'+str(e)
    if str(login_keyword).find('Username:') == -1:
        return "ip:"+ip+'-'+'not find the login keyword,you can try to change the login type!'

    tn.write(usr+"\n")
    tn.read_until("Password: ",3)
    tn.write(pwd+"\n")


    #------judge logined in ------
    try:
        logined_keyword = tn.read_until("#",3)
    except Exception,e:
        return "ip:"+ip+'-'+str(e)
    if str(logined_keyword).find('#') == -1:
        return "ip:"+ip+'-'+'not find the Enable  keyword,please check the user  password!'

    tn.write('sh mac address-table ' + '\n')
    press_flag = 0 
    #---find the end of configuration and exit----
    while 1:
        message = tn.expect(['--More--'],3)
        if press_flag != 0:
            new_batchline =  message[2][27:]
        if press_flag == 0:
            new_batchline =  message[2]

        new_batchline_count = new_batchline.count('\n')               #count the line num. of this batch
        for index in range(0,new_batchline_count):
            if (new_batchline.split('\n')[index].count('.') >= 2)&(len(new_batchline.split('\n')[index].split()) == 4):  
                #filter no use information by count the num of dot,everyline must can be splited to 4 part
                every_line_mac = ''
                every_line_mac = 'Mgmt:' +ip +'\t'+ new_batchline.split('\n')[index].split()[1] + '\t' \
                                                  + new_batchline.split('\n')[index].split()[2] + '\t' \
                                                  + new_batchline.split('\n')[index].split()[0] + '\t' \
                                                  + new_batchline.split('\n')[index].split()[3] 
                if(new_batchline.split('\n')[index].split()[3] != _upport):
                    every_line_mac = every_line_mac + '\tGW:' +_flag
                    os.system('echo  '+every_line_mac+'  >> '+ _allmacfile)   # do not split() every line,or will error

        tn.write(" ")
        #print "---> press enter "
        press_flag = 1
        if (message[2].find('--More--') == -1):
            break
    print '1:'+ip+' '+'mac info get ready!'

    if (_flag.find('-') == -1):
        return successful_flag
       


    message = ''
    tn.write('show ip arp' + '\n')
    #print '2:show ip arp  !'
    #---find the end of configuration and exit----
    while 1:
        message = tn.expect(['--More--'],3)
        message_list += str(message[2])
        tn.write(" ")
        if (str(message[2]).find('--More--') == -1):
            tn.write("exit\n")
            tn.close
            #print "3:No more info so  logout!"
            break

    #print '-----\n',message_list,'-------\n'
    arp_all_count =  message_list.count('\n')
    #print 'arp all count:',ip,'--',arp_all_count         #can make mac Num. warning,include 'Incomplete '
    for index in range(0,arp_all_count):
        if (message_list.split('\n')[index].count('.') >= 5)&(len(message_list.split('\n')[index].split()) == 6):  
            #filter no use information by count the num of dot,everyline must can be splited to 6 parts
            every_line_ip_arp = ''
            every_line_ip_arp =  'Mgmt:'+ip+'\t'+message_list.split('\n')[index].split()[3]+'\t' \
                                  +message_list.split('\n')[index].split()[1]+'\t' \
                                  +message_list.split('\n')[index].split()[5] 
            os.system('echo  '+every_line_ip_arp+'  >> '+ _allarpfile)
    print '2:'+ip+' '+'arp info get ready!'
    return successful_flag



def huawei(ip,usr,pwd,_allmacfile,_allarpfile,_flag,_upport):
    '''get huawei switch & router  mac,arp
    '''
    successful_flag = 'ok'
    #---telnet,username,password------
    try:
        tn = telnetlib.Telnet(ip,23,5)
    except Exception,e:
        return "ip:"+ip+'-'+str(e)
    #----try to login --------
    try:
        login_keyword = tn.read_until(": ",3)
    except Exception,e:
        return "ip:"+ip+'-'+str(e)
    if str(login_keyword).find(':') == -1:
        return "ip:"+ip+'-'+'not find the login keyword of maohao!'

    tn.write(usr+"\n")
    tn.read_until(": ",3)
    tn.write(pwd+"\n")
    #------judge logined in ------
    try:
        logined_keyword = tn.read_until(">",3)
    except Exception,e:
        return "ip:"+ip+'-'+str(e)
    if str(logined_keyword).find('>') == -1:
        #print "try style-2 usr-pwd2"
        tn.read_until(': ',10)
        tn.write(usr+'\n')
        tn.read_until(': ',3) 
        tn.write(pwd2+'\n')
        if str(tn.read_until(">",3)).find('>') == -1:
            return "ip:"+ip+'-'+'not find the   keyword,try style-2 user-password also not right!'
              
    tn.write('sy\n')
    #-----judge system priority------
    try:
        systemed = tn.read_until("]",3)
    except Exception,e:
        return "ip:"+ip+'-'+str(e)
    if str(systemed).find(']') == -1:
        return "ip:"+ip+'-'+'not find the   keyword, no system priority !'
    #print '1:begin to get arp !'

    message = ''
    press_flag = 0 
    tn.write('dis mac-address' + '\n')
    while 1:
        message = tn.expect(['-- More --'],3)
        if press_flag != 0:
            #print 'find . -->',message[2].find('-')
            new_batchline =  message[2]
        if press_flag == 0:
            new_batchline =  message[2]
        new_batchline_count = new_batchline.count('\n')               #count the line num. of this batch
        #print 'batch line count:',new_batchline_count
        for index in range(0,new_batchline_count):
            r_newbatchline = new_batchline.split('\n')[index]
            #filter no use information by count the num of dot, every line must can split() to 5 field
            if (r_newbatchline.count('-') >= 2)&(len(r_newbatchline.split()) == 4):     #every line must can be splited to 5 parts 
                every_line_mac = ''
                every_line_mac  = 'Mgmt:'+ip +'\t'+ r_newbatchline.split()[0]+'\t'+  \
                                                    r_newbatchline.split()[3]+'\t'+ \
                                                    r_newbatchline.split()[1]+'\t'+ \
                                                    r_newbatchline.split()[2]
                if(r_newbatchline.split()[2] != _upport):
                    every_line_mac = every_line_mac.replace('/-','')
                    every_line_mac = every_line_mac.replace('-','.')
                    every_line_mac = every_line_mac + '\tGW:' +_flag
                    #print every_line_mac
                    os.system('echo  '+every_line_mac+'  >> '+ _allmacfile)   # do not split() every line,or will error
        tn.write(" ")
        #print "---> press enter "
        press_flag = 1
        if (message[2].find('-- More --') == -1):
            break
    print '1:'+ip+' '+'mac info get ready!'

    if (_flag.find('-') == -1):
        return successful_flag
      

    message = ''
    press_flag = 0 
    tn.write('dis arp' + '\n')
    while 1:
        message = tn.expect(['-- More --'],3)
        if press_flag != 0:
            #print 'find . -->',message[2].find('.')
            new_batchline =  message[2]   #[54:]
        if press_flag == 0:
            new_batchline =  message[2]
        new_batchline_count = new_batchline.count('\n')               #count the line num. of this batch
        #print 'batch line count:',new_batchline_count
        for index in range(0,new_batchline_count):
            r_newbatchline = new_batchline.split('\n')[index]
            #filter no use information by count the num of dot, every line must can split() to 5 field
            if (r_newbatchline.count('.') >= 3)&(len(r_newbatchline.split()) == 5):     #every line must can be splited to 5 parts 
                every_line_arp = ''
                every_line_arp  = 'Mgmt:'+ip +'\t'+ r_newbatchline.split()[1]+'\t'+  \
                                                    r_newbatchline.split()[0]+'\t'+ \
                                                    r_newbatchline.split()[4]
                every_line_arp = every_line_arp.replace('-','.')
                #print every_line_arp
                if r_newbatchline.split()[1].find('Incomplete') == -1:         #filter incomplete line
                    os.system('echo  '+every_line_arp+'  >> '+ _allarpfile)   # do not split() every line,or will error
        tn.write(" ")
        #print "---> press enter "
        press_flag = 1
        if (message[2].find('-- More --') == -1):
            tn.write("quit\n")
            tn.write("quit\n")
            tn.close
            break
    print '2:'+ip+' '+'arp info get ready!'
    return successful_flag



def h3csw(ip,usr,pwd,_allmacfile,_allarpfile,_flag,_upport):
    '''get h3c switch & router  mac,arp
    '''
    successful_flag = 'ok'
    #---telnet,username,password------
    try:
        tn = telnetlib.Telnet(ip,23,5)
    except Exception,e:
        return "ip:"+ip+'-'+str(e)
    #----try to login -------why-
    try:
        login_keyword = tn.read_until(": ",5)
    except Exception,e:
        return "ip:"+ip+'-'+str(e)
    if str(login_keyword).find(':') == -1:
        return "ip:"+ip+'-'+'not find the login keyword maohao'

    tn.write(usr+"\n")
    tn.read_until(": ",3)
    tn.write(pwd+"\n")
    #tn.write("\n")
    #------judge logined in ------
    try:
        logined_keyword = tn.read_until(">",3)
    except Exception,e:
        return "ip:"+ip+'-'+str(e)
    if str(logined_keyword).find('>') == -1:
        #print "try style-2 usr-pwd2"
        tn.read_until(': ',10)
        tn.write(usr+'\n')
        tn.read_until(': ',3) 
        tn.write(pwd2+'\n')
        if str(tn.read_until(">",3)).find('>') == -1:
            return "ip:"+ip+'-'+'not find the   keyword,try style-2 user-password also not right!'
              
    #tn.write('sy\n')
    #-----judge system priority------
    #try:
    #    systemed = tn.read_until("]",3)
    #except Exception,e:
    #    return "ip:"+ip+'-'+str(e)
    #if str(systemed).find(']') == -1:
    #    return "ip:"+ip+'-'+'not find the   keyword, no system priority !'


    #print '1:begin to get mac !'
    message = ''
    press_flag = 0 
    tn.write('dis mac-address' + '\n')
    while 1:
        message = tn.expect(['---- More ----'],6)
        if press_flag != 0:
            #print 'find . -->',message[2].find('-')
            new_batchline =  message[2]
            #print new_batchline
        if press_flag == 0:
            new_batchline =  message[2]
            #print new_batchline
        new_batchline_count = new_batchline.count('\n')               #count the line num. of this batch
        #print 'batch line count:',new_batchline_count
        for index in range(0,new_batchline_count):
            r_newbatchline = new_batchline.split('\n')[index]
            #filter no use information by count the num of dot, every line must can split() to 5 field
            if (r_newbatchline.count('-') >= 2)&(len(r_newbatchline.split()) == 5):     #every line must can be splited to 5 parts 
                every_line_mac = ''
                every_line_mac  = 'Mgmt:'+ip +'\t'+ r_newbatchline.split()[0]+'\t'+  \
                                                    r_newbatchline.split()[2]+'\t'+ \
                                                    r_newbatchline.split()[1]+'\t'+ \
                                                    r_newbatchline.split()[3]
                if(r_newbatchline.split()[3] != _upport):
                    every_line_mac = every_line_mac.replace('-','.')
                    every_line_mac = every_line_mac + '\tGW:' +_flag
                    #print every_line_mac
                    os.system('echo  '+every_line_mac+'  >> '+ _allmacfile)   # do not split() every line,or will error
        tn.write(" ")
        #print "---> press enter "
        press_flag = 1
        if (message[2].find('-- More --') == -1):
            break
    print '1:'+ip+' '+'mac info get ready!'

    if (_flag.find('-') == -1):
        return successful_flag
       

    message = ''
    press_flag = 0 
    tn.write('dis arp' + '\n')
    while 1:
        message = tn.expect(['-- More --'],3)
        if press_flag != 0:
            #print 'find . -->',message[2].find('.')
            new_batchline =  message[2][54:]
            #print new_batchline
        if press_flag == 0:
            new_batchline =  message[2]
            #print new_batchline
        new_batchline_count = new_batchline.count('\n')               #count the line num. of this batch
        #print 'batch line count:',new_batchline_count
        for index in range(0,new_batchline_count):
            r_newbatchline = new_batchline.split('\n')[index]
            #filter no use information by count the num of dot, every line must can split() to 5 field
            if (r_newbatchline.count('.') >= 3)&(len(r_newbatchline.split()) >= 5):     #every line must can be splited to 5 parts 
                every_line_arp = ''
                every_line_arp  = 'Mgmt:'+ip +'\t'+ r_newbatchline.split()[1]+'\t'+  \
                                                    r_newbatchline.split()[0]+'\t'+ \
                                                    r_newbatchline.split()[2]
                every_line_arp = every_line_arp.replace('-','.')
                #print every_line_arp
                if r_newbatchline.split()[1].find('Incomplete') == -1:         #filter incomplete line
                    os.system('echo  '+every_line_arp+'  >> '+ _allarpfile)   # do not split() every line,or will error
        tn.write(" ")
        #print "---> press enter "
        press_flag = 1
        if (message[2].find('-- More --') == -1):
            tn.write("quit\n")
            #tn.write("quit\n")
            tn.close
            break
    print '2:'+ip+' '+'arp info get ready!'
    return successful_flag



def mainscan(_ip,_infotype,_infoname,_infoflag,_uplinkport,_nowscancount,_linecount):

    print '--------',_infoname,'|',_infotype,'|',_ip,'------'+str(_nowscancount)+'/'+str(_linecount)+'---------'
    if _infotype.find('cisco-router') >= 0:
        cisco_router_ret = ciscorouter(_ip,usr,pwd,allmacfile,allarpfile,_infoflag,_uplinkport)
        if (cisco_router_ret != 'ok'):
            os.system("echo "+begintime+' '+_ip+':'+"  cisco-router get mac or arp  fail ! Code:"+cisco_router_ret+" >> "+pythonlog)  # log to mylog.txt 
            print _infoname+' '+_ip+'  get mac or arp  fail...'
        return _ip+' cisco-router '+'function successful'
    if _infotype.find('cisco-sw') >= 0:
        cisco_sw_ret =  ciscosw(_ip,usr,pwd,allmacfile,allarpfile,_infoflag,_uplinkport)
        if (cisco_sw_ret != 'ok'):
            os.system("echo "+begintime+' '+_ip+':'+"  cisco-sw get mac or arp  fail ! Code:"+cisco_sw_ret+" >> "+pythonlog)  # log to mylog.txt 
            print _infoname+' '+_ip+'  get mac or arp  fail...'
        return _ip+' cisco-sw '+'function successful'
    if _infotype.find('cisco-nxos') >= 0:
        cisco_nxos_ret =  cisco_nxos(_ip,usr,pwd,allmacfile,allarpfile,_infoflag,_uplinkport)
        if (cisco_nxos_ret != 'ok'):
            os.system("echo "+begintime+' '+_ip+':'+"  cisco-nxos get mac or arp  fail ! Code:"+cisco_nxos_ret+" >> "+pythonlog)  # log to mylog.txt 
            print _infoname+' '+_ip+'  get mac or arp  fail...'
        return _ip+' cisco-nxos '+'function successful'
    if _infotype.find('cisco-4500') >= 0:
        cisco_4500_ret =  cisco_4500_sw(_ip,usr,pwd,allmacfile,allarpfile,_infoflag,_uplinkport)
        if (cisco_4500_ret != 'ok'):
            os.system("echo "+begintime+' '+_ip+':'+"  cisco-4500 get mac or arp  fail ! Code:"+cisco_4500_ret+" >> "+pythonlog)  # log to mylog.txt 
            print _infoname+' '+_ip+'  get mac or arp  fail...'
        return _ip+' cisco-4500 '+'function successful'
    if _infotype.find('huawei') >= 0:
        huawei_ret =   huawei(_ip,usr,pwd,allmacfile,allarpfile,_infoflag,_uplinkport)
        if (huawei_ret != 'ok'):
            os.system("echo "+begintime+' '+_ip+':'+"  huawei get mac or arp  fail ! Code:"+huawei_ret+" >> "+pythonlog)  # log to mylog.txt 
            print _infoname+' '+_ip+'  get mac or arp  fail...'
        return _ip+' huawei '+'function successful'
    if _infotype.find('h3c-sw') >= 0:
        h3c_sw_ret =  h3csw(_ip,usr,pwd,allmacfile,allarpfile,_infoflag,_uplinkport)
        if (h3c_sw_ret != 'ok'):
            os.system("echo "+begintime+' '+_ip+':'+"  h3c-sw  get mac or arp  fail ! Code:"+h3c_sw_ret+" >> "+pythonlog)  # log to mylog.txt 
            print _infoname+' '+_ip+'  get mac or arp  fail...'
        return _ip+' h3csw '+'function successful'
    return _ip+': unknow type'





def main(_linecount):
    #--run multiprocess to create allmacfile,allarpfile-----
    result=[]
    pool = multiprocessing.Pool(processes=MAX_creatfile_process)   #max processes 
    for line_ in range(0,linecount):
        print "get arp&mac creat multiprocess thread:",line_
        c_ip = device_idct[line_]['ip']
        c_type = device_idct[line_]['type']
        c_name = device_idct[line_]['name']
        c_flag = device_idct[line_]['flag']
        c_upport = device_idct[line_]['uplinkport']
        result.append(pool.apply_async(mainscan,(c_ip,c_type,c_name,c_flag,c_upport,line_,linecount,)))
        time.sleep(sleep_time)
    pool.close()
    pool.join()


    for index_result in range(0,len(result)):
        if result[index_result].successful() != True:
            os.system("echo "+ begintime +" mutiprocess thread error ! ip:"+device_idct[index_result]['ip']+" >> "+pythonlog)  # log to mylog.txt 
        #else:
        #    print 'Mutiprocess thread all successful'
        
    #----read arpfile + macfile -> MAC-ip----



if __name__ == "__main__":
    os.system("echo "+ begintime +" getMacArp begin ! >> "+pythonlog)  # log to mylog.txt 
    os.system("rm -f "+allmacfile)
    os.system("rm -f "+allarpfile)
    os.system("rm -f "+allarpmacfile)
    os.system("echo "+ begintime +" delete allarpmacfile,allmacfile,allarpfile ok ! >> "+pythonlog)  # log to mylog.txt 

    main(linecount)

    #--read arpfile into L3 dict--
    b_allarpfile =  str(os.path.exists(allarpfile)).find('False')
    b_allmacfile =  str(os.path.exists(allmacfile)).find('False')
    if((b_allarpfile == 0)|(b_allmacfile == 0)):
        os.system("echo "+ begintime +" not find arpfile or mac file ! >> "+pythonlog)  # log to mylog.txt 
        print 'not find arpfile or mac file !!'
        sys.exit()

    #--read allarpfile----
    arpid = 0
    arpfile = open(allarpfile)
    for line in arpfile.readlines():
            L3arp_idct[arpid]['L3mac'] = line.split()[1]
            L3arp_idct[arpid]['L3dev'] = line.split()[0][5:]
            L3arp_idct[arpid]['ip']= line.split()[2]  
            arpid += 1    #line counter
    arpfile.close()
    print 'read allarp file to L3 idct,allarp_count:',arpid


    #--read allmacfile
    mac_count = 0
    mac_count_cmd = "grep -c $ "+allmacfile
    mac_count =  os.popen(mac_count_cmd,'r').read()
    mac_count =  mac_count.replace('\n','')
    print 'read allmac_count:',mac_count


    #--function print L3->L2 result--
    midtime =  time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    print 'begin to match mac(ip) to device-interface........'
    ifcount = 0
    noifcount = 0
    for arpline in range(0,arpid):
        arpline_mac = L3arp_idct[arpline]['L3mac']
        arpline_ip = L3arp_idct[arpline]['ip']
        arpline_L3dev = L3arp_idct[arpline]['L3dev']
        title =  str(arpline)+' ARP:'+ arpline_mac+' ip:'+ arpline_ip+' L3dev:'+arpline_L3dev
        #print title
        os.system("echo \'"+ title +"</p>\' >> "+allarpmacfile)   
        #print-mac-interface-detail
        search_command = 'grep  \''+arpline_mac+'\' '+allmacfile+'|awk \'{print $1" "$3" "$4" "$5}\''
        #print search_command
        macs_line_os  = os.popen(search_command,'r').read()
        #print macs_line_os
        macs_line_count =  macs_line_os.count('\n')
        for detail_line in range(0,macs_line_count):
            macline_dev = macs_line_os.split('\n')[detail_line].split(' ')[0]
            macline_type =  macs_line_os.split('\n')[detail_line].split(' ')[1]
            macline_vlan =  macs_line_os.split('\n')[detail_line].split(' ')[2]
            macline_if =  macs_line_os.split('\n')[detail_line].split(' ')[3]
            #macline_gw = macs_line_os.split('\n')[detail_line].split(' ')[4]
            #macline_gw = macline_gw.replace('-',macline_dev[5:])
            #ifdetail = str(arpline)+ " L2dev:%s type:%s vlan:%s interface:%s %s"%(macline_dev[5:],macline_type,macline_vlan,macline_if,macline_gw)
            ifdetail = str(arpline)+ " L2dev:%s type:%s vlan:%s interface:%s"%(macline_dev[5:],macline_type,macline_vlan,macline_if)
            #print ifdetail
            os.system("echo \'"+ ifdetail +"</p>\' >> "+allarpmacfile)   
            ifcount += 1
        if(macs_line_count == 0):
            noifcount +=1
    
    print 'match over! check allarpmac.html,then begin to backup this file'
    if os.path.exists(allarpmacfilebakpath) == False:
        os.makedirs(allarpmacfilebakpath)
    if os.path.exists(allarpmacbakpath) == False:
        os.makedirs(allarpmacbakpath)
    filenametime =  time.strftime('%Y%m%d%H%M%S.arpmacbak',time.localtime(time.time()))
    filenametimearp =  time.strftime('%Y%m%d%H%M%S.arpbak',time.localtime(time.time()))
    filenametimemac =  time.strftime('%Y%m%d%H%M%S.macbak',time.localtime(time.time()))
    os.system("cp "+allarpmacfile+" "+allarpmacfilebakpath+'/'+filenametime)
    os.system("cp "+allarpfile+" "+allarpmacbakpath+'/'+filenametimearp)
    os.system("cp "+allmacfile+" "+allarpmacbakpath+'/'+filenametimemac)
    os.system("echo "+ midtime +" creat new allarpmacfile,allarp,allmac ok and backup ready ! >> "+pythonlog)  # log to mylog.txt 


    endtime =  time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    print 'begintime:',begintime
    print 'endtime:',endtime
    os.system("echo "+ endtime +" getMacArp successful check allarpmac.html ! >> "+pythonlog)  # log to mylog.txt 
    sendtxt = 'arp_count:'+str(arpid)+'</p>'  + 'mac_count:'+mac_count+'</p>' + 'arp->if success:'+str(ifcount)+'</p>'  + 'know arp,but no interface:'+str(noifcount)+'</p>'     
    messageMode.sendtxtmail('getMacArp ready!',0,sendtxt,receiver,endtime)
