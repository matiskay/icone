import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.contrib.loader import XPathItemLoader

from icone.items import Product


def slug(string):
    """
    Generate a slug string
    This is not a real implementation of sluglify but this works in this
    particular case

    """
    slugify = string.replace(' ', '-')
    return slugify


def remove_last(url):
    """
    Remove the last element of a url /(\d+)/
    """

    url = re.sub(r'\d+\/$', '', url)
    return url


class IconeSpider(BaseSpider):
    """
    """

    name = 'icone'
    allowed_domains = ['icone.co.uk']
    start_urls = ['http://www.icone.co.uk']

    def parse(self, response):
        """
        Parse and sluglify the options values from a combo box
        """
        hxs = HtmlXPathSelector(response)

        # Remove the first element becuase it doesn't provide any item
        product_types = hxs.select(
            '//select[@name="prod_type"]/option/text()') \
            .extract()[1:]

        for product_type in product_types:
            product_type = slug(product_type)
            # TODO: There is a problem adding 0
            url = "%s/designer-living/product-type/%s/0/" %  \
                (response.url, product_type)

            yield Request(url=url, callback=self.parse_pages)

    def parse_pages(self, response):
        """
        Parse the page product types to get the links from the pagination
        """
        hxs = HtmlXPathSelector(response)

        # TODO: Refactor this code. Many websites only has pagination for
        # some pages. [1][2][3]....[90][91]
        pages = hxs.select(
            '//table/tr/td/table/tr[3]/td/table/tr[2]/td/form/table/tr[3]/td/ \
            table/tr/td/b/text()') \
            .re(r'\[Page \d+ of (\d+)\]')

        if pages:
            pages = int(pages[0])
        else:
            pages = 1

        for number in range(0, pages):
            url = "%s%s/" % (remove_last(response.url), number)
            # dont_filter=True beacuse the spider doesn't read the first
            # request /0/
            yield Request(url=url, callback=self.parse_products,
                dont_filter=True)

    def parse_products(self, response):
        """
        Parse each product to get the url from the product.
        """
        hxs = HtmlXPathSelector(response)

        products = hxs.select('//table/tr/td/table/tr[3]/td/table/tr/td/form/ \
            table/tr[2]/td/table/tr')

        for product in products:
            url = product.select('./td[@class="itemlist_design"]/a/@href') \
                .extract()
            yield Request(url=url[0], callback=self.parse_product)

    def parse_product(self, response):
        """
        Gather all the information from the product

        name
        price
        description
        image_urls

        """
        l = XPathItemLoader(item=Product(), response=response)

        l.add_xpath('name', '//table/tr/td/table/tr[3]/td/table/ \
            tr/td[2]/h1/text()')

        l.add_xpath('description', '//table/tr/td/table/tr[3]/td/table/ \
            tr/td[2]/div[@class="content"][2]/text()')

        # price
        l.add_xpath('price', '//td[@class="midcol"]/form/table/ \
            tr[2]/td[2]/strong/text()')

        l.add_xpath('price', '//td[@class="midcol"]/form/table/ \
            tr[3]/td[2]/strong/text()')
        l.add_xpath('price', '//td[@class="midcol"]/form/table/ \
            tr[4]/td[2]/strong/text()')
        l.add_xpath('price', '//td[@class="midcol"]/form/table/ \
            tr[5]/td[2]/strong/text()')
        l.add_xpath('price', '//td[@class="midcol"]/ \
            div[@class="content"][3]/form/table/tr[3]/td[2]/strong/text()')
        l.add_xpath('price', '//td[@class="midcol"]/ \
            div[@class="content"][3]/form/table/tr[4]/td[2]/strong/text()')

        l.add_xpath('image_urls', '//table/tr/td/table/ \
            tr[3]/td/table/tr/td/form/table/tr/td/strong/a/@href'
            , re="'(.*?)'"
        )

        return l.load_item()
