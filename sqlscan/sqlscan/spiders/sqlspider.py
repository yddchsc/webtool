import scrapy
from optparse import OptionParser

class DmozSpider(scrapy.Spider):
    name = "sqlscan"
    parser = OptionParser()
    parser.add_option("-u", "--url", dest="url", type="string", help="give the url of the website") 
    (options, args) = parser.parse_args()

    host = options.url.split("/")[2]
    allowed_domains = [host]
    
    start_urls = [
        options.url
    ]

    def parse(self, response):
        item = response.meta['item']
        