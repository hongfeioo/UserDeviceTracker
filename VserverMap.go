package main

import (
	"bufio"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
)

var fillIeeeMac MapMap      //put mac->factoryInfo
var fillInterfaceMac MapMap //put Interface->mac
var fillMacIp MapMap        //put Mac->Ip
var showMac bool

//------------------
const (
	FILE_ALLMAC  = "./allmac.txt"
	//FILE_ALLMAC2 = "./allmac_input.txt"
	FILE_ALLARP  = "./allarp.txt"
	//FILE_ALLARP2 = "./allarp_input.txt"
	FILE_IEEEMAC = "./ieee_mac.txt"
)

//------------------
type MapMap struct {
	//a map of interface to mac,map["interface"]{"mac1":0;"mac2":0}  ; map["mac"]{"ip1":0,"ip2":0}
	mapp map[string]map[string]int
}

func main() {

	//---------http-----------------------------
	fmt.Println("Listening:8080")
	http.HandleFunc("/", handler)
	err1 := http.ListenAndServe(":8080", nil)
	if err1 != nil {
		log.Fatal("listenandserver err:", err1.Error())
	}
}

func handler(w http.ResponseWriter, r *http.Request) {
	log.Println("requestRUL", r.RequestURI)
	showMac := r.RequestURI[1:]
	log.Println("show mac or not", showMac)
	log.Println("host", r.Host)

	//---------load mac factory info------------
	ff4, err := FillIeeeMac(FILE_IEEEMAC)
	if err != nil {
		fmt.Println("FillIeeeMac error")
	}
	fillIeeeMac = ff4
	//ff4.ListMap()

	//---------load Interface mac info-----------
	//MacBooks := []string{FILE_ALLMAC, FILE_ALLMAC2}
	MacBooks := []string{FILE_ALLMAC}
	fillAllInterfaceMac, err := FillInterfaceMac(MacBooks)
	if err != nil {
		fmt.Println("FillInterfaceMac error")
	}
	fillInterfaceMac = fillAllInterfaceMac

	//---------load Mac Ip info-----------
	//ArpBooks := []string{FILE_ALLARP, FILE_ALLARP2}
	ArpBooks := []string{FILE_ALLARP}
	fillAllMacIp, err := FillMacIp(ArpBooks)
	if err != nil {
		fmt.Println("FillMacIp error")
	}
	fillMacIp = fillAllMacIp

	//-------creat html page ---------------------------------------------
	fmt.Fprintf(w, "<html><head><title>VserverMap</title></head><body><table  style=\"color:black;font-size:10px\" align=\"center\" border=\"2\"  cellpadding=\"10\"  cellspacing=\"2\">") //<< to html
	for i, ii := range fillInterfaceMac.mapp {                                                                                                                                                            //show all interface - mac
		fmt.Fprintf(w, "<tr><td>")
		fmt.Fprintf(w, i+"</br>")
		for mac, _ := range ii { //search ip in everyone mac
			if showMac == "mac" {
				var IeeeMacInfo string
				for i, _ := range fillIeeeMac.mapp[mac[:7]] { //get ieeemacinfo
					IeeeMacInfo = "(" + i + ")"
				}
				fmt.Fprintf(w, "-+"+mac+"<font color=\"red\">"+IeeeMacInfo+"</font><br>") //show mac & ieeemacinfo

				if len(fillMacIp.mapp[mac]) == 0 { //not find ip in two mac book
					fmt.Fprintf(w, "--+no ip find<br>")
				}
				IeeeMacInfo = ""

			}
			for i, _ := range fillMacIp.mapp[mac] { //all ip in first mac book
				fmt.Fprintf(w, "--+"+i+"</br>")
			}
		}

		fmt.Fprintf(w, "</td></tr>") //<< to html
	}
	fmt.Fprintf(w, "</table></body></html>") //<< to html
	//-----------html end---------------------------

}

func (m *MapMap) Init() {
	m.mapp = make(map[string]map[string]int)
	//fmt.Println("init ok")
}

func (m *MapMap) MapAdd(sw_if string, mac_string string) {
	if _, ok := m.mapp[sw_if]; ok { //exist interface here
		m.mapp[sw_if][mac_string] = 0

	} else {
		newMac := make(map[string]int) // new interface here
		newMac[mac_string] = 0
		m.mapp[sw_if] = newMac
	}
}

func (m *MapMap) ListMap() {
	for i, ii := range m.mapp {
		for mac := range ii {
			fmt.Println(i, mac)
		}

	}

}

func FillInterfaceMac(filePath []string) (MapMap, error) {
	if_init := MapMap{}
	if_init.Init()

	for i := 0; i < len(filePath); i++ { // fill all arp book to mapmap
		fmt.Println("read mac file:", filePath[i])

		f, err := os.Open(filePath[i])
		if err != nil {
			return if_init, err
		}
		defer f.Close()
		bfRd := bufio.NewReader(f)
		for {
			line, err := bfRd.ReadBytes('\n')
			everyLine := string(line)
			//if strings.Contains(everyLine, "10.10.88.15") {
			if (!strings.Contains(everyLine, "Bridge")) && (len(strings.Split(everyLine, " ")) == 6) { //not contain Bridge interface
				//fmt.Println(everyLine)
				everyLineMac := strings.Split(everyLine, " ")[1]
				everyLineInterface := strings.Split(everyLine, " ")[4]
				everyLineMgmt := strings.Split(everyLine, " ")[0]
				if_init.MapAdd(everyLineMgmt+"-"+everyLineInterface, everyLineMac)
				//fmt.Println("---",everyLineInterface,everyLineMac)

			}
			if err != nil {
				if err == io.EOF {
					break
				}
				return if_init, err
			}
		}
	}
	fmt.Println("FillInterfaceMac  over.")
	return if_init, nil
}

func FillMacIp(filePath []string) (MapMap, error) {
	if_init := MapMap{}
	if_init.Init()

	for i := 0; i < len(filePath); i++ { // fill all arp book to mapmap
		fmt.Println("read arp file:", filePath[i])

		f, err := os.Open(filePath[i])
		if err != nil {
			return if_init, err
		}
		defer f.Close()
		bfRd := bufio.NewReader(f)
		for {
			line, err := bfRd.ReadBytes('\n')
			everyLine := string(line)
			//if strings.Contains(everyLine, "Mgmt:10.10.88.1") {                //search mac only in SLP.Core
			if len(strings.Split(everyLine, " ")) == 4 { //search mac  in all L3 device
				everyLineMac := strings.Split(everyLine, " ")[1]
				everyLineIp := strings.Split(everyLine, " ")[2]
				if_init.MapAdd(everyLineMac, everyLineIp)
				//fmt.Println("---", everyLineMac, everyLineIp)

			}
			if err != nil {
				if err == io.EOF {
					break
				}
				return if_init, err
			}
		}
	}
	fmt.Println("FillMacIp  over.")
	return if_init, nil
}

func FillIeeeMac(filePth string) (MapMap, error) {
	if_init := MapMap{}
	if_init.Init()

	f, err := os.Open(filePth)
	if err != nil {
		return if_init, err
	}
	defer f.Close()
	bfRd := bufio.NewReader(f)
	for {
		line, err := bfRd.ReadBytes('\n')
		everyLine := string(line)
		if len(strings.Split(everyLine, ",")) > 3 {
			everyIeeeMac := strings.Split(everyLine, ",")[1]
			everyIeeeOem := strings.Split(everyLine, ",")[2]
			if_init.MapAdd(strings.ToLower(everyIeeeMac[:4]+"."+everyIeeeMac[4:6]), everyIeeeOem)
			//fmt.Println("---", everyIeeeMac, everyIeeeOem)

		}
		if err != nil {
			if err == io.EOF {
				return if_init, nil
			}
			return if_init, err
		}
	}
	fmt.Println("FillIeeeMac  over.")
	return if_init, nil
}
