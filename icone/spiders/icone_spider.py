import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from icone.items import Product


# Generate a string from a list of trimming the values
def clean(i_list):
    r_list = []
    for x in i_list:
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


# Remove the last element of a url /(\d+)/
def remove_last(url):

    url = re.sub(r'\d+\/$', '', url)
    return url


class IconeSpider(BaseSpider):

    name = 'icone'
    allowed_domains = ['icone.co.uk']
    start_urls = ['http://www.icone.co.uk']

    def parse(self, response):
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
        hxs = HtmlXPathSelector(response)

        products = hxs.select('//table/tr/td/table/tr[3]/td/table/tr/td/form/ \
            table/tr[2]/td/table/tr')

        items = []
        for product in products:
            url = product.select('./td[@class="itemlist_design"]/a/@href') \
                .extract()
            yield Request(url=url[0], callback=self.parse_product)

    def parse_product(self, response):
        hxs = HtmlXPathSelector(response)

        item = Product()

        item['name'] = clean(hxs.select(
            '//table/tr/td/table/tr[3]/td/table/tr/td[2]/h1/text()') \
            .extract()
            )

        item['description'] = clean(hxs.select(
            '//table/tr/td/table/tr[3]/td/table/tr/td[2]/ \
            div[@class="content"][2]/text()') \
            .extract()
            )

        price = hxs.select(
            '//table/tr/td/table/tr[3]/td/table/tr/td[2]/form/ \
            table/tr[4]/td[2]/strong/text()') \
            .extract()

        if not price:
            price = hxs.select(
                '//table/tr/td/table/tr[3]/td/table/tr/td[2]/form/ \
                table/tr[3]/td[2]/strong/text()') \
                .extract()
            if not price:
                price = hxs.select(
                    '//td[@class="midcol"]/form/table/tr[4]/td[2]/ \
                    strong/text()') \
                    .extract()
                if not price:
                    price = hxs.select(
                        '//td[@class="midcol"]/div[@class="content"][3]/form/ \
                        table/tr[3]/td[2]/strong/text()') \
                        .extract()
                    if not price:
                        price = hxs.select(
                            '//td[@class="midcol"]/form/table/tr[2]/td[2]/ \
                            strong/text()') \
                            .extract()
                        if not price:
                            price = hxs.select(
                                '//td[@class="midcol"]/form/table/ \
                                tr[5]/td[2]/strong/text()') \
                                .extract()
                            if not price:
                                price = hxs.select(
                                    '//td[@class="midcol"]/ \
                                    div[@class="content"][3]/form/ \
                                    table/tr[4]/td[2]/strong/text()') \
                                    .extract()

        item['price'] = clean(price)

        item['image'] = hxs.select(
            '//table/tr/td/table/tr[3]/td/table/tr/td/form/table/ \
            tr/td/strong/a/@href') \
            .re(r"\('(.*?)'\)")

        return item
