# -*- coding: utf-8 -*-
import scrapy
from slugify import slugify
import os
import sys
import json
from urllib.parse import urlparse, urljoin
import datetime as dt

date = '{}.{}.{}'.format(dt.datetime.now().year,dt.datetime.now().month,dt.datetime.now().day)
folder_name = os.getcwd()+'/../data/urbania/'+date

if not os.path.isdir(folder_name):
		try:
			os.mkdir(folder_name)
		except:
			os.rmdir(folder_name)

def make_folder_urb(folder_name,date):

	date = '{}.{}.{}'.format(dt.datetime.now().year,dt.datetime.now().month,dt.datetime.now().day)
	#folder_name = os.getcwd()+'/../data/urbania/'+date

	if not os.path.isdir(folder_name):
		try:
			os.mkdir(folder_name)
		except:
			os.rmdir(folder_name)
			os.mkdir(folder_name)

class UrbaniaSpider(scrapy.Spider):
	name = 'urbania'
	allowed_domains = ['urbania.pe']
	start_urls = ['https://urbania.pe/']

	#make_folder_urb()

	def start_requests ( self ):
		yield scrapy.Request('https://urbania.pe/buscar/propiedades', self.parse)

	def parse(self,response):
		for product in response.xpath("//article[contains(@class,'b-card-item')]//a[contains(@class,'b-card-item-link')]"):
			href = response.urljoin((product.xpath('@href').extract_first()))
			yield scrapy.Request(href, callback=self.parse_product,errback=self.error_parse_product)

		nextUrl = response.urljoin(response.xpath("//div[contains(@class, 'b-pagination-container')]//li/a[contains(@class,'active')]/../following-sibling::li[1]/a/@href").extract_first())
		if(nextUrl):
			yield scrapy.Request(nextUrl,callback=self.parse)

	def parse_product(self,response):

		data = {}
		keys = response.xpath('//p[@class="e-leading-data-service"][1]/text()').getall()
		vals = response.xpath('//p[@class="e-leading-data-service"][2]/text()').getall()

		for i in range(len(keys)):
			try:
				data[keys[i]]=vals[i]
			except:
				pass

		data['descripcion']=response.xpath('//p[@class="js-description"]/text()').get()
		data['vinetas']=response.xpath('//li[@class="b-section-item"]/span[2]/text()').getall()
		data['precio_dolares']=response.xpath('//p[@class="e-price-property"]/text()').getall()[1]
		data['precio_soles']=response.xpath('//p[@class="e-price-property"]/text()').getall()[2]

		yOSON = response.xpath('/html/body/script[4]/text()').get().split('var yOSON = ')[1]
		yOSON = yOSON.replace('\n','').replace('\t','').replace('JSON.parse("false")','0').replace(' ','')
		yOSON = yOSON.replace(',}','}').replace('ubigeo:','"ubigeo":').replace('freeSearch:','"freeSearch":')
		yOSON = yOSON.replace('inputEmpty:','"inputEmpty":').replace('mapForLocationPrecision','"mapForLocationPrecision"')
		yOSON = eval(yOSON[:-1])
		data['latitud']=yOSON['map']['latitud']
		data['longitud']=yOSON['map']['longitud']

		with open(folder_name+'/datos.txt','a') as f:
			f.write('{}\n'.format(data));

	def error_parse_product(self, failure):
		print('error')


if __name__ == '__main__':
	folder_name = os.getcwd()+'/../data/urbania/'+date
	make_folder_urb(folder_name)