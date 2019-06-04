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
folder_name = os.getcwd()+'/../data/remax/'+date

if not os.path.isdir(folder_name):
		try:
			os.mkdir(folder_name)
		except:
			os.rmdir(folder_name)
			os.mkdir(folder_name)

def make_folder_adv(folder_name):

	date = '{}.{}.{}'.format(dt.datetime.now().year,dt.datetime.now().month,dt.datetime.now().day)
	#folder_name = os.getcwd()+'/../data/remax/'+date

	if not os.path.isdir(folder_name):
		try:
			os.mkdir(folder_name)
		except:
			os.rmdir(folder_name)
			os.mkdir(folder_name)

class Remax(scrapy.Spider):
	name = 'remax'
	allowed_domains = ['remax.pe']
	start_urls = ['https://www.remax.pe/propiedades.php']

	#make_folder_adv()

	def start_requests ( self ):
		yield scrapy.Request('https://www.remax.pe/propiedades.php?search=2&combopais=1&combotipo=1', self.parse)

	def parse(self,response):
		for product in response.xpath('//*[@class="bot-detalle left"]/a'):
			href = response.urljoin((product.xpath('@href').extract_first()))
			yield scrapy.Request(href, callback=self.parse_product,errback=self.error_parse_product)

		nextUrl = response.urljoin(response.xpath('//*[@title="Página Siguiente"]').attrib['href'])
		if(nextUrl):
			yield scrapy.Request(nextUrl,callback=self.parse)

	def parse_product(self,response):
		if response.xpath('//*[@class="col-xs-12 id_propiedad"]//text()'):
			data = {}
			data['id']=response.xpath('//*[@class="col-xs-12 id_propiedad"]//text()').get().replace('\n','').replace('\t','').split(' - ')[0]
			data['tipo']=response.xpath('//*[@class="col-xs-12 id_propiedad"]//text()').get().replace('\n','').replace('\t','').split(' - ')[1]
			keys=list()
			vals=list()
			for key in response.xpath('//*[@class="etiqueta"]/text()').getall()[:-1]:
				keys.append(key.replace('\n','').replace('\t',''))
			for val in response.xpath('//*[@class="print"]/text()').getall():
				vals.append(val.replace('\n','').replace('\t',''))
			for i in range(len(keys)):
				data[keys[i]]=vals[i]

			data['descripcion']=response.xpath('//*[@class="descripcion_prop"]/text()').getall()
			data['agente']=response.xpath('//*[@class="name_agente"]/a/text()').get()
			data['rango_agente']=response.xpath('//*[@class="d_agente"]/text()').get().replace('\n','').replace('\t','')
			data['precio-soles']=response.xpath('//*[@class="precio"]/text()[2]').get().replace('\n','').replace('\t','')
			data['precio-dolares']=response.xpath('//*[@class="precio"]/text()[1]').get().replace('\n','').replace('\t','')
			data['latitud']=response.xpath('//*[@id="textll1"]/@value').get()
			data['longitud']=response.xpath('//*[@id="textll2"]/@value').get()
			with open(folder_name+'/datos.txt','a') as f:
				f.write('{}\n'.format(data));
		else:
			print('Sorry, redirected.')

	def error_parse_product(self, failure):
		print('error')

if __name__ == '__main__':
	folder_name = os.getcwd()+'/../data/remax/'+date
	make_folder_adv(folder_name)