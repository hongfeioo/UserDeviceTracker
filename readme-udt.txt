# UDT简易UI
index.php 和 udt.py  两个文件为UDT提供了一个简易的UI， 可以在网页中搜索ip或者mac。


<img src="udt.png" alt="udt" width="200" height="100">


## 按钮的作用
1. search   对最近的一次采集结果进行搜索
2. history  在所有的备份文件中搜索（当你想知道某个ip是否被占用也可以用这个功能）
3. update   触发一次后台的getMacArp操作，获取最新的arp和mac信息。





## 注意
1. history按钮会对macarpbak中的“所有”备份文件进行搜索，为了避免展示内容过长可以定期清理这些备份文件, 当显示超过500条目时，页面会有提示。
2. 面页中 “红色”部分其实就是arp信息，L3dev指的是这条arp信息所在的设备,  L2dev 表示红色mac地址所在的设备. 
3. 要让index.php 跑起来你需要一个web环境，例如apache ,此处不多讲。



## 排错
---------
1.  网页的按钮update不起作用，可能是文件或者目录权限导致。
2.  通过这种方式可以直接测试程序是否有问题。排除php的干扰。
```
example:
python udt.py 192.168.102.134 history  在所有arpmac库中搜索
python udt.py 192.168.102.134 search   在今天的arpmac库中搜索
python udt.py 00ef.ccrg.a3ff history
python udt.py 00ef.ccrg.a3ff search 
```


