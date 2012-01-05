# A spider for Icone 

## TODO
- Pagination
- Scrape two other urls 
- Clean up the strings

## Instalation

1. `virtualenv --site-no-packages env`
2. `source /env/bin/activate`
3. `pip install scrapy`

## Useful commands

- Check the list of spiders

```bash
  $ scrapy list
```


- Save the scraped data into a json file

```
  $ scrapy crawl icone -o items.json -t json
```


## References

- [Scrapy Documentation](http://doc.scrapy.org/en/0.14/index.html)
- [Scrapy Tutorial](http://readthedocs.org/docs/scrapy/en/0.14/intro/tutorial.html)

