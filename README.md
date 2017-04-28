# UserDeviceTracker
快速定位一个IP或MAC在你的网络中的位置.


## 介绍
1. 本程序会采集cisco,huawei,h3c交换机上的arp表和mac地址表，经过后台的匹配生成: ip->mac->interface 三元素的对应关系， 这对于查找服务器所在的交换机端口非常有帮助
2. 随着虚拟化技术的发展，本程序对于定位虚拟机所在的物理机也有帮助。


## 工作流程
程序会通过模拟登陆的方式获取网络设备的arp表和MAC表,取到的ARP信息记录在allarp.txt 中，MAC信息记录在allmac.txt 中, 然后会在ARP文件中逐一取出条目，并针对这个ip的mac 在mac地址库中进行查，把结果显示成html文件，循环往复。


## 配置文件的格式
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

## 备注
1.  推荐只采集核心交换和接入层设备，汇聚层设备不要放，因为太多的trunk口没什么用.
2.  macarpbak目录为自动生成，程序会在生成allarpmac.html 之后向本文件夹中拷贝一份留作备用，以方便以后查找,需要注意的是磁盘空间。
3.  macarp目录为自动生成， 存放allmac 和allarp的备份数据
4.  没有三层信息的设备在allarpmac.html中是找不到的。(下文已得到改善)
5.  配置文件中的ip顺序是有讲究的，核心交换，汇聚交换，接入层交换, 这样的排列可以让生成的结果更易读。


### arp信息格式(allarp.txt)
```bash
Mgmt:10.64.0.16 fcfb.fb9e.1041 10.64.3.75 Vlan2   // Mgmt:设备ip  mac  ip  vlan(未用到)
```


### MAC信息格式 (allmac.txt)
```
Mgmt:10.64.0.16 58bf.ea74.72b0 DYNAMIC 1 Gi1/0/15 GW:-    // Mgmt:设备ip  mac  dynamic  vlan   interface  Gateway(现在统一为-， 以后可以开发成其他含义的字段)
```


### arp+mac组合成HTML展示(allarpmac.html)
你需要有一个web的展示环境，例如apache nginx 就可以看到内容.


## 总结
allarpmac.html 是对采集的数据进行了简单的展示(IP -> MAC -> SwitchPort)，很丑但凑活能用. 在展现方面在下边还有两个小项目的优化，分别以不同的方式展示了采集回来的数据。
 
1.  php+python  (IP -> MAC -> SwitchPort)
2.  golang      (SwirthPort -> MAC -> IP)


## TODO
1.  模拟登陆的方式获取arp和mac信息,会在翻页处造成少量信息丢失，本项目的第二个版本会采用go重构所有代码，snmp获取信息.
2.  2017年3月, 本程序已经完成的go语言的重构，采集信息的方式由模拟登陆变成了snmp,存储方式也由文本变成了ETCD，并对外提供RESTful接口，后期可能公布源码。



* * *

# 1-UDT简易UI(选用)
为了让采集得到的数据更加直观的展示，index.php 和 udt.py  两个文件为UDT提供了一个简易的UI， 可以在网页中搜索ip或者mac _( 一位网络工程师已逐渐走向全栈，请不要阻拦)_


## 截图
<img src="udt.png" alt="udt" >



```
解释：
 ARP:703d.15e3.6dd7 ip:10.10.100.20 L3dev:10.10.88.1</p>                 //这其实是一条arp信息，L3dev指这条arp信息所在的设备
 L2dev:10.10.88.1 type:Dynamic vlan:100 interface:Bridge.Aggregation19</p>   //红色的mac地址，出现在10.10.88.1这台设备上，接口是一个及联口。
 L2dev:10.10.82.3 type:Learned vlan:100 interface:GigabitEthernet1/0/41</p>   //还出现在了10.10.82.3这个接入层交换机上，这是一个真实的物理接口。

从以上信息可以解读到，10.10.100.20(703d.15e3.6dd7)  这个设备连接在 10.10.82.3这台接入层交换机的G1/0/41口，vlan 100 。

```



## 按钮的作用
1. search   对最近的一次采集结果进行搜索
2. history  在所有的备份文件中搜索（当你想知道某个ip是否被占用也可以用这个功能）
3. update   触发一次后台的getMacArp操作，获取最新的arp和mac信息。





## 注意
1. history按钮会对macarpbak中的“所有”备份文件进行搜索，为了避免展示内容过长可以定期清理这些备份文件, 当显示超过500条目时，页面会有提示。
2. 面页中 “红色”部分其实就是arp信息，L3dev指的是这条arp信息所在的设备,  L2dev 表示红色mac地址所在的设备. 
3. 要让index.php 跑起来你需要一个web环境，例如apache ,此处不多讲。



## 排错
1.  网页的按钮update不起作用，可能是文件或者目录权限导致。
2.  通过这种方式可以直接测试程序是否有问题。排除php的干扰。
```
example:
python udt.py 192.168.102.134 search   在最近的arpmac库中搜索ip
python udt.py 192.168.102.134 history  在所有arpmac库中搜索ip
python udt.py 00ef.ccrg.a3ff search    在最近的arpmac库中搜索mac
python udt.py 00ef.ccrg.a3ff history   在所有arpmac库中搜索mac
```

* * *

# 2-UDT的简易UI(选用)

## 介绍
1.  可以看作是UDT的go版的简易UI
2.  和php版本的UI相比，这个版本展示的信息更全，显示的更加形象。
3.  引入了mac地址翻译功能，可以看出网卡的厂家



## 特性介绍
1. 以arp库文件和mac库文件作为源，分析出Interface -> mac -> IP 的对应关系， 这个和allarpmac.html 的生成过程刚好相反，好处在于没有IP信息的mac也会被展示出来。
2. 一个mac地址对应多个IP的情况被很好的展现。
3. MAC地址解析成厂家的依据是这个文件：ieee_mac.txt ，可去官方网站更新




## 启动方法
```
go build  VserverMap.go
./VserverMap

注意：golang的安装方法此处不做介绍
```

## 使用方法
```
1. http://localhost:8080/mac   Interface ->mac->Ip    
2. http://localhost:8080/      Interface -> IP

备注：go的强大之处可见一斑，分分钟就能搭建一个网页展示
```



## 截图
<img src="vm.png" alt="vservermap" >



##  举例子
```

Mgmt:192.168.24.71-GigabitEthernet2/0/10
-+1866.daf8.5844(Dell Inc.)
--+192.168.30.170
解读：这种情况最为普遍，交换机192.168.24.71的2/0/10口下有一个mac地址1866.daf8.5844，并且可以被成功是被为dell厂商，对应的ip为192.168.30.170


Mgmt:10.2.1.15-GigabitEthernet1/0/19
-+5ab0.461d.f641
--+10.10.10.12
-+c81f.66c2.c2d3(Dell Inc.)
--+10.10.10.11
-+d2d2.0eb8.2d49
--+10.10.10.13
解读： 这种情况可能是c81f.66c2.c2d3（10.10.10.11）物理机上启动了两个虚拟机分别是5ab0.461d.f641（10.10.10.12）和d2d2.0eb8.2d49（10.10.10.13）


Mgmt:172.16.4.3-GigabitEthernet2/0/15
-+b82a.72dc.3dcb
--+21.15.118.66
--+21.15.118.60
--+21.15.118.6
解读： 交换机172.16.4.3的2/0/15口下有一个mac地址b82a.72dc.3dcb，这个mac对应了三个IP，说明可能有虚IP的情况。




Mgmt:192.168.254.6-GigabitEthernet2/0/19
-+c81f.66fa.d90f(Dell Inc.)
--+no ip find
解读： 这种情况很可能是这个服务器没有位置IP，所以只获取了二层信息，没有三层信息。

```


## 数据结构设计
```
1. 用map的key存放信息有天然去重的功效,并且可以检索，这个是数组无法比拟的（至少现在数组没有去重的函数）
2. 一个接口下会有多个mac，并且mac可能重复: 这种情况， 外层key存放Interface，内层key存放mac很合理。
3. 一个mac地址会对应多个IP地址,   这种情况，外层key存放mac ，内层key存放Ip很合理。
4. 内层的map只用到了key没有用到value，以后可以开发使用。

type MapMap struct {
        mapp map[string]map[string]int  
}

5.  外层键值为string，内容为map； 
6.  内层键值为string，内容为0
7.  FillMacInterface  外层键值Interface  内层键值mac  内容为空, 满足一个接口下多个mac（自动去重），并存入多个不同端口
8.  FillMacIp         外层键值Mac        内层键值Ip   内容为空，满足一个mac对应多个ip（自动去重），并存入多个不同mac
9.  FillIeeeMac       外层键值Mac前缀    内层键值厂家名字  内容为空，  其实这里没有去重的必要，但是用key检索value还是比较快的。
```

## 函数介绍
1.  FillMacInterface从allmac.txt中过滤出端口和mac的对应关系,存入双重的map关系,记录了  Interface -> mac  的一对多关系
2.  FillMacIp从allarp.txt 中过滤出mac和ip的对应关系, 存入双重的map结构. 记录了mac -> IP  的一对多关系。
3.  FillIeeeMac，从ieeemac.txt数据库中，过滤出mac地址前缀和厂家的关系存入双map结构，记录了 mac前缀 ->  厂家的关系。



### IEEE 指定的MAC地址规范下载
https://regauth.standards.ieee.org/standards-ra-web/pub/view.html#registries


### 缺陷
如果物理服务器有两块网卡，宿主走一个网卡，虚拟机走另外一个网卡，这种情况用本程序就无法找到虚拟机所在的宿主了。



------



## 作者介绍
yihongfei  QQ:413999317   MAIL:yihf@liepin.com

CCIE 38649


## 寄语
为网络自动化运维尽绵薄之力

