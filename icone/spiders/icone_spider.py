import re
from urlparse import urlparse

from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request      

from icone.items import Product 


# Generate a string form a list trimming the values
def clean(l):
    r_list = []
    for x in l:
        pattern = re.compile(r'\s+')
        x = re.sub(pattern, ' ', x)
        x = x.strip()
        r_list.append(x)

    return ' '.join(r_list)


# Generate a slug string
# This is not a real implemention of slug but it works in this case
def slug(s):
    slug = s.replace(' ', '-')
    return slug


# Remove the last element of a url
# TODO: Refactor this code
# TODO: Use regular expressions
def remove_last(url):
    url = urlparse(url)

    n_elements = len(url.path.split('/'))

    # Remove the last element of the path
    path = '/'.join(url.path.split('/')[1:n_elements - 2])

    url = 'http://%s/%s/' % (url.netloc, path)

    return url


class IconeSpider(BaseSpider):

    name = 'icone'
    allowed_domains = ['icone.co.uk']
    start_urls = ['http://www.icone.co.uk',
#        'http://www.icone.co.uk/designer-living/product-type/',
#        'http://www.icone.co.uk/designer-living/brand/',
#        'http://www.icone.co.uk/designer-living/designer/',
    ]


    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        # Remove the first element becuase it doesn't provide any item
        product_types = hxs.select('//select[@name="prod_type"]/option/text()').extract()[1:] 

        for product_type in product_types:
            product_type = slug(product_type)
            # TODO: There is a problem adding 0
            url = "%s/designer-living/product-type/%s/0/" % (response.url, product_type)
            yield Request(url=url, callback=self.parse_pages)


    def parse_pages(self, response):

        hxs = HtmlXPathSelector(response)

        pages = len(hxs.select('//table/tr/td/table/tr[3]/td/table/tr[2]/td/form/table/tr[3]/td/table/tr/td/a'))

        if pages == 0:
            pages = 1

        for number in range(0, pages):
            url = "%s%s/" % (remove_last(response.url), number)
            # dont_filter=True beacuse the spider doesn't read the first request /0/
            yield Request(url=url, callback=self.parse_products, dont_filter=True)


    def parse_products(self, response):
        hxs = HtmlXPathSelector(response)
        
        products = hxs.select('//table/tr/td/table/tr[3]/td/table/tr/td/form/table/tr[2]/td/table')
        items = []
    
        for product in products:

            item = Product()
            item['name'] = clean(product.select('./tr/td[@class="itemlist_design"]/strong/text()').extract())
            item['description'] = clean(product.select('./tr/td[@class="itemlist_desc"]/text()').extract())
            item['price'] = clean(product.select('./tr/td[@class="itemlist_price"]/a/span/strong/text()').extract())
            item['image'] = clean(product.select('./tr/td[@class="itemlist_img"]/a/img/@src').extract())

            items.append(item)

        return items
