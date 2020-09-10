# -*- coding:utf-8 -*-
import xlrd,xlwt
import os
from datetime import date,datetime
import sys
import urllib3
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

def Find_Check_Links(driver,my_site_link,head_contents):
  #'''从自己网站上找到亚马逊，淘宝等网站的链接，并用sub_check_product_link判断是否有效'''
    http = urllib3.PoolManager()
    r = http.request('GET',my_site_link,headers=head_contents)
    html=r.data.decode("utf-8")
    bs = BeautifulSoup(html,"html.parser")
    list=["default"]
    for item in bs.find_all("a"):
        product_link=str(item.get("href"))
        if product_link.find(r"https://s.click.taobao.com") ==-1 and product_link.find(r"https://www.amazon.com")==-1:#无效链接的话，直接查找下一条
            #print("没有amazon和tmall:"+product_link)
            continue
        notexisted=True
        for c in list:
            #print("ccccccccc"+c)
            if c== product_link:
                notexisted=False
                #print("有链接相同："+c)
                break
        if notexisted:
            list.append(product_link)
        else:
            continue   #有相同链接，不执行后面语句，直接进入下一次For循环
        #print(product_link)
        if product_link.find(r"https://s.click.taobao.com")!=-1:
            #list.append(str(item.get("href")))
            result=sub_check_taobao_product_link(driver,product_link)
            if result == 0:
                #write_log(my_site_link+"\n")
                write_log("################## 没有查找到，需要确认##################\n\n")
                write_log(product_link+"\n")
            if result == 2:
                #write_log(my_site_link+"\n")
                write_log("################## 此商品已下架##################\n\n")
                write_log(product_link+"\n")
        if product_link.find(r"https://www.amazon.com")!=-1:
            if  sub_check_amazon_product_link(driver,product_link)==0:
                #write_log(my_site_link+"\n")
                write_log("################## 没有查找到，需要确认##################\n\n")
                write_log(product_link+"\n")
            if  sub_check_amazon_product_link(driver,product_link)==2:
                #write_log(my_site_link+"\n")
                write_log("################## 页面找不到了！##################\n\n")
                write_log(product_link+"\n")


def sub_check_taobao_product_link(driver,product_link):
#'''检查淘宝，亚马逊等商品的链接是否有效，好像屏蔽抓取的了。改用selenium'''
    #driver = webdriver.Chrome()
    try:
        driver.get(product_link)
        #time.sleep(5)
    except TimeoutException:
        #driver.execute_script("window.stop()")
        print("---------time out-------:"+product_link)
        driver.get(product_link)
       # time.sleep(15)
    finally:
        if driver.find_elements_by_id("J_LinkBuy") or str(driver.page_source).find("立即购买")!=-1: #立即购买标签
            return 1
        if str(driver.page_source).find("此商品已下架")!=-1 or str(driver.page_source).find("此宝贝已下架")!=-1 or str(driver.page_source).find("很抱歉，您查看的宝贝不存在，可能已下架或者被转移")!=-1:
            return 2
        return 0

def sub_check_amazon_product_link(driver,product_link):
#'''检查淘宝，亚马逊等商品的链接是否有效，好像屏蔽抓取的了。改用selenium'''
    try:
        driver.get(product_link)
        #time.sleep(5)
    except TimeoutException:
        #driver.execute_script("window.stop()")
        print("---------time out-------:"+product_link)
        driver.get(product_link)
        #time.sleep(15)
    finally:        
        if driver.find_elements_by_id("newBuyBoxPrice") or str(driver.page_source).find("Available from")!=-1 or str(driver.page_source).find("Price")!=-1 or str(driver.page_source).find('Currently, there are no sellers that can deliver this item to your location.')!=-1 or str(driver.page_source).find('Price + Shipping')!=-1:
            return 1
        if str(driver.page_source).find("Sorry! We couldn't find that page. Try searching or go to Amazon's home page."):
            return 2
        return 0
      
def write_log(context):
    file_object = open('check_result.log','a',encoding="utf-8")
    try :
        file_object.write(context+'\n')
    finally:
        file_object.close( )
        
def finished_links_log(context):
    file_object = open('Finished_MysitesLinks.log','a',encoding="utf-8")
    try :
        file_object.write(context+'\n')
    finally:
        file_object.close( )
    
if __name__=='__main__':
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.90 Safari/537.36 2345Explorer/9.5.2.18321'}
    driver = webdriver.Chrome()
    driver.minimize_window()
    #设置get的最大时间，超时会产生TimeoutException
    driver.set_page_load_timeout(40)
    driver.set_script_timeout(40)
    with open('MysitesLinks.txt', 'r') as f1:
        while 1:
            line = f1.readline()
            print(line) 
            write_log("@@@@@@@@@@@@@@@@@@@@@@@@ start  [" + line.strip('\n') + "]  start @@@@@@@@@@@@@@@@@@@@@@@@")
            if line.strip('\n'):
                Find_Check_Links(driver,line,headers)
                finished_links_log(line)
            else:
                break
            write_log("@@@@@@@@@@@@@@@@@@@@@@@@ end  [" + line.strip('\n') + "]  end @@@@@@@@@@@@@@@@@@@@@@@@")
    f1.close()
    driver.close()
