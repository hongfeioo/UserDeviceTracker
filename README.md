# UserDeviceTracker
快速定位一个IP或MAC在你的网络中的位置.



介绍
--------
1. 本程序会采集cisco,huawei,h3c交换机上的arp表和mac地址表，经过后台的匹配生成: ip->mac->interface 三元素的对应关系， 这对于查找服务器所在的交换机端口非常有帮助
2. 随着虚拟化技术的发展，本程序对于定位虚拟机所在的物理机也有很大帮助。
3. 本程序已经完成的go语言的重构，采集信息的方式也由现在的模拟登陆变成了snmp,存储方式也由现在的文本变成了ETCD，并对外提供RESTful接口，后期可能公布源码。


工作流程
-----------
程序会通过模拟登陆的方式获取网络设备的arp表和MAC表,取到的ARP信息记录在allarp.txt 中，MAC信息记录在allmac.txt 中, 然后会在ARP文件中逐一取出条目，并针对这个ip的mac 在mac地址库中进行查，把结果显示成html文件，循环往复。


配置文件的格式
-------------
```

#idc1
10.10.8.1       h3c-sw          slp_CoreSW      -       -
10.10.8.11      h3c-sw          server_acc_150  -       Bridge-Aggregation2
10.10.8.12      h3c-sw          server_acc_151  -       Bridge-Aggregation2
#idc2
10.55.0.1       cisco-nxos      core1.idc5      -       -
10.55.1.1       cisco-nxos      n5k1.idc5       -       Po51
10.55.1.2       cisco-nxos      n5k2.idc5       -       Po51

1.  第1个字段设备ip，
2.  第2个字段设备类型（不同的设备类型对应不同的模拟登陆方式和arp／mac获取方式），
3.  第3个字段为备注（可描述设备名字,随意书写），
4.  第4个字段如果是-则取双表，如果不是-则只取mac地址表（目前都设置-，以后可以开发成更有用的字段）。
5.  第5个字段.   mac地址表入库的时候，会排除这些接口。 如果是核心交换则用- ，如果是接入层交换机则写上这个交换机的上联口。 

```

备注
-----------
1.  只放网关设备和接入层设备，汇聚层设备不要放，因为太多的trunk口没什么用.
2.  本目录下的macarpbak文件夹是自动生成的，程序会在生成allarpmac.html 之后向本文件夹中拷贝一份留作备用，以方便以后查找,需要注意的是磁盘空间。
3.  macarp 目录存放allmac 和allarp的备份数据
4.  如果有些设备没有ip，那么在allarpmac.html中是找不到的。
5.  配置文件中的ip顺序是有讲究的，核心交换，汇聚交换，接入层交换, 这样的排列可以让生成的结果更易读。


arp信息格式(allarp.txt)
------------------
```bash
Mgmt:10.64.0.16 fcfb.fb9e.1041 10.64.3.75 Vlan2   // Mgmt:设备ip  mac  ip  vlan(未用到)
```


MAC信息格式 (allmac.txt)
-------------
```
Mgmt:10.64.0.16 58bf.ea74.72b0 DYNAMIC 1 Gi1/0/15 GW:-    // Mgmt:设备ip  mac  dynamic  vlan   interface  Gateway(现在统一为-， 以后可以开发成其他含义的字段)
```


arp+mac组合成HTML展示(allarpmac.html)
--------------------------
```
例如：
11311 ARP:f8bc.1278.ba1e ip:192.168.8.142 L3dev:10.64.0.250</p>               /这其实是一条arp信息，L3dev指这条arp信息所在的设备(即allarp表中的MGMT)
11311 L2dev:10.64.0.250 type:Dynamic vlan:2 interface:FastEthernet0/0/0</p>   // 这些都是dis mac信息， 这里有三条说明这个mac出现在三个物理设备上
11311 L2dev:192.168.8.253 type:Learned vlan:1 interface:Ethernet1/0/23</p>
11311 L2dev:192.168.8.250 type:Learned vlan:1 interface:Ethernet1/0/4</p>

这些html代码生成的页面效果我就不展示了，虽然很丑凑活能用,美观的事儿得找UI搞定。

```

TODO
-------
1.  模拟登陆的方式获取arp和mac信息,会在翻页处造成信息丢失，本项目的第二个版本会采用go重构所有代码，snmp获取信息，并且所有信息放入ETCD存储。


作者介绍
----------
yihongfei  QQ:413999317   MAIL:yihf@liepin.com

CCIE 38649


寄语
------
为网络自动化运维尽绵薄之力

