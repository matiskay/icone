import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.contrib.loader import XPathItemLoader

from icone.items import Product

XPATHS = {
    # Get the product_types from the combo box
    'product_types' : '//select[@name="prod_type"]/option/text()',
    'pages' : '//table/tr/td/table/tr[3]/td/table/tr[2]/td/form/table/ \
        tr[3]/td/table/tr/td/b/text()',
    'products' : {
        'base' : '//table/tr/td/table/tr[3]/td/table/tr/td/form/ \
            table/tr[2]/td/table/tr', 
        'url' : './td[@class="itemlist_design"]/a/@href'
        },
    'product' : { 
        'name' : '//table/tr/td/table/tr[3]/td/table/tr/td[2]/h1/text()',
        'description' : '//table/tr/td/table/tr[3]/td/table/ \
            tr/td[2]/div[@class="content"][2]/text()',
        'prices' : [
            '//td[@class="midcol"]/form/table/tr[2]/td[2]/strong/text()',
            '//td[@class="midcol"]/form/table/tr[3]/td[2]/strong/text()',
            '//td[@class="midcol"]/form/table/tr[4]/td[2]/strong/text()',
            '//td[@class="midcol"]/form/table/tr[5]/td[2]/strong/text()',
            '//td[@class="midcol"]/div[@class="content"][3]/form/table/ \
                tr[3]/td[2]/strong/text()',
            '//td[@class="midcol"]/div[@class="content"][3]/form/table/ \
                tr[4]/td[2]/strong/text()',
        ],
        # Get the images form the image pagination above the image
        'image_urls' : '//table/tr/td/table/tr[3]/td/table/tr/td/form/table/ \
            tr/td/strong/a/@href'
    }

}

def slug(string):
    '''
    Generate a slug string
    This is not a real implementation of sluglify but this works in this
    particular case

    '''
    slugify = string.replace(' ', '-')
    return slugify


def remove_last(url):
    '''
    Remove the last element of a url /(\d+)/
    '''

    url = re.sub(r'\d+\/$', '', url)
    return url


class IconeSpider(BaseSpider):
    '''
    A custom spider for http://www.icone.co.uk/
    '''

    name = 'icone'
    allowed_domains = ['icone.co.uk']
    start_urls = ['http://www.icone.co.uk']

    def parse(self, response):
        '''
        Parse and sluglify the options values from a combo box
        '''
        hxs = HtmlXPathSelector(response)

        # Remove the first element becuase it doesn't provide any item
        product_types = hxs.select(XPATHS['product_types']).extract()[1:]

        for product_type in product_types:
            product_type = slug(product_type)
            url = '%s/designer-living/product-type/%s/0/' \
                % (response.url, product_type)

            yield Request(url=url, callback=self.parse_pages)

    def parse_pages(self, response):
        '''
        Parse the page product types to get the links from the pagination
        '''
        hxs = HtmlXPathSelector(response)

        pages = hxs.select(XPATHS['pages']).re(r'\[Page \d+ of (\d+)\]')

        if pages:
            pages = int(pages[0])
        else:
            pages = 1

        for number in range(0, pages):
            url = '%s%s/' % (remove_last(response.url), number)
            # dont_filter=True beacuse the spider doesn't read the first
            # request /0/
            yield Request(url=url, callback=self.parse_products,
                dont_filter=True)

    def parse_products(self, response):
        '''
        Parse each product to get the url from the product.
        '''
        hxs = HtmlXPathSelector(response)

        products = hxs.select(XPATHS['products']['base'])

        for product in products:
            url = product.select(XPATHS['products']['url']).extract()
            yield Request(url=url[0], callback=self.parse_product)

    def parse_product(self, response):
        '''
        Gather all the information from the product

        name
        price
        description
        image_urls

        '''
        l = XPathItemLoader(item=Product(), response=response)

        l.add_xpath('name', XPATHS['product']['name'])

        l.add_xpath('description', XPATHS['product']['description'])

        # price
        for xpath in XPATHS['product']['prices']:
            l.add_xpath('price', xpath)

        l.add_xpath('image_urls', XPATHS['product']['image_urls'] \
            , re='\'(.*?)\'')

        return l.load_item()
