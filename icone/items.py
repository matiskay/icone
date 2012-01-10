# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field
from scrapy.contrib.loader.processor import MapCompose, Join


class Product(Item):
    name = Field(
        input_processor=MapCompose(unicode.strip),
        output_processor=Join(),
        )

    description = Field(
        input_processor=MapCompose(unicode.strip),
        output_processor=Join(),
    )

    price = Field(
        input_processor=MapCompose(unicode.strip),
        output_processor=Join(),
    )

    image_urls = Field()
    images = Field()

    def __str__(self):
        return "Product: name=%s price=%s" % (self['name'], self['price'])
