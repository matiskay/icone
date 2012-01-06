import re

from scrapy import log
from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request      

from icone.items import Product 


# Generate a string form a list trimming the values
def clear(l):
    r_list = []
    for x in l:
        pattern = re.compile(r'\s+')
        x = re.sub(pattern, ' ', x)
        x = x.strip()
        r_list.append(x)

    return ' '.join(r_list)


class IconeSpider(BaseSpider):

    name = 'icone'
    allowed_domains = ['icone.co.uk']
    start_urls = ['http://www.icone.co.uk/designer-living/product-type/Lighting-Floor',
#        'http://www.icone.co.uk/designer-living/product-type/',
#        'http://www.icone.co.uk/designer-living/brand/',
#        'http://www.icone.co.uk/designer-living/designer/',
    ]

    rules = [Rule(SgmlLinkExtractor(allow=('/\d+',)), callback='parse', follow=True), ]

    def parse(self, response):
        log.msg('A response from %s just arrived!' % response.url)

        hxs = HtmlXPathSelector(response)

        pages = len(hxs.select('//table/tr/td/table/tr[3]/td/table/tr[2]/td/form/table/tr[3]/td/table/tr/td/a'))

        for number in range(0, pages):
            url = "%s/%s/" % (response.url, number)
            yield Request(url=url, callback=self.parse_products)

    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        
        products = hxs.select('//table/tr/td/table/tr[3]/td/table/tr/td/form/table/tr[2]/td/table')
        items = []
    
        for product in products:

            item = Product()
            item['name'] = clear(product.select('./tr/td[@class="itemlist_design"]/strong/text()').extract())
            item['description'] = clear(product.select('./tr/td[@class="itemlist_desc"]/text()').extract())
            item['price'] = clear(product.select('./tr/td[@class="itemlist_price"]/a/span/strong/text()').extract()) 
            item['image'] = clear(product.select('./tr/td[@class="itemlist_img"]/a/img/@src').extract())

            items.append(item)

        return items
