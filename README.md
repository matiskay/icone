# A spider for Icone 

This spider loops though all the product items using the filters to get the
information from the product.

- name
- price
- description
- images_uls
- images

In order to get the results. Just run 

```bash
  scrapy crawl icone -o items.json -t json
```

Then check the items.json file. 

## TODO
- Refactoring


## DONE
- Clean up the strings
- Clean description: Now it is a list [, , , ]
- Pagination
- Scrape the other urls 


## Instalation

1. `virtualenv --site-no-packages env`
2. `source /env/bin/activate`
3. `pip install scrapy`
4. `pip install pil`


## Useful commands

- Check the list of spiders

```bash
  scrapy list
```


- Save the scraped data into a json file

```bash
  scrapy crawl icone -o items.json -t json
```


## References

- [Scrapy Documentation](http://doc.scrapy.org/en/0.14/index.html)
- [Scrapy Tutorial](http://readthedocs.org/docs/scrapy/en/0.14/intro/tutorial.html)
- [Scrapy - Requests and Responses](http://readthedocs.org/docs/scrapy/en/0.14/topics/request-response.html)
- [Scrapy - Spiders](http://readthedocs.org/docs/scrapy/en/latest/topics/spiders.html)
- [Ideas from BManojlovic](http://pastie.org/3133918)
- [Scrapy - Item Loaders](http://doc.scrapy.org/en/latest/topics/loaders.html)
- [Scrapy - Downloading Item Images](http://doc.scrapy.org/en/latest/topics/images.html)
