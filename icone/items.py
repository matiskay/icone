# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class Product(Item):
    name = Field()
    description = Field()
    price = Field()
    image = Field()

    def __str__(self):
        return "Product: name=%s price=%s" % (self['name'], self['price'])
