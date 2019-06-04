# -*- coding: utf-8 -*-
import scrapy
from slugify import slugify
import os
import sys
import json
from urllib.parse import urlparse, urljoin
import datetime as dt
import re

date = '{}.{}.{}'.format(dt.datetime.now().year,dt.datetime.now().month,dt.datetime.now().day)
folder_name = os.getcwd()+'/../data/adondevivir/'+date

if not os.path.isdir(folder_name):
		try:
			os.mkdir(folder_name)
		except:
			os.rmdir(folder_name)
			os.mkdir(folder_name)

def make_folder_adv(folder_name):

	date = '{}.{}.{}'.format(dt.datetime.now().year,dt.datetime.now().month,dt.datetime.now().day)
	#folder_name = os.getcwd()+'/../data/adondevivir/'+date

	if not os.path.isdir(folder_name):
		try:
			os.mkdir(folder_name)
		except:
			os.rmdir(folder_name)
			os.mkdir(folder_name)

class AdondevivirSpider(scrapy.Spider):
	name = 'adondevivir'
	allowed_domains = ['adondevivir.com']
	start_urls = ['https://adondevivir.com/']

	#make_folder_adv()

	def start_requests ( self ):
		yield scrapy.Request('https://www.adondevivir.com/inmuebles-en-venta-ordenado-por-fechaonline-descendente.html', self.parse)

	def parse(self,response):
		for product in response.xpath('//h3[has-class("posting-title")]/a'):
			href = response.urljoin((product.xpath('@href').extract_first()))
			yield scrapy.Request(href, callback=self.parse_product,errback=self.error_parse_product)

		nextUrl = response.urljoin(response.xpath("//*[@class='pag-go-next']/a").attrib['href'])
		if(nextUrl):
			yield scrapy.Request(nextUrl,callback=self.parse)

	def parse_product(self,response):
		data = {}
		data['tipo']=response.xpath('//h2[@class="title-type-sup"]/b/text()').get().split(' ')[0]
		keys = response.xpath('//*[@class="icon-feature"]//span/text()').getall()
		vals = response.xpath('//*[@class="icon-feature"]//b/text()').getall()

		for i in range(len(keys)):
			data[keys[i]]=vals[i]

		data['vinetas']=response.xpath('//ul[@class="section-bullets"]/li//text()').getall()
		data['descripcion']=response.xpath('//div[@id="verDatosDescripcion"]//text()').getall()
		data['anunciante']=response.xpath('//h3[@class="publisher-subtitle"]/b/text()').get()
		data['precio-soles']=response.xpath('//div[@class="price-items"]//text()').getall()[0]
		data['precio-dolares']=response.xpath('//div[@class="price-items"]//text()').getall()[1]
		try:
			coords=re.split('center=|&zoom',response.xpath('//img[@id="static-map"]').attrib['src'])[1]
			data['coordenadas']=[float(item) for item in coords.split(',')]
		except:
			data['coordenadas']=[]
		with open(folder_name+'/datos.txt','a') as f:
			f.write('{}\n'.format(data));

	def error_parse_product(self, failure):
		print('error')

if __name__ == '__main__':
	folder_name = os.getcwd()+'/../data/adondevivir/'+date
	make_folder_adv(folder_name)