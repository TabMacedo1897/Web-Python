import scrapy
import random
from bookscraper.items import BookItem

class BookspiderSpider(scrapy.Spider):
    #nome do spider que o crawl ira chamar
    name = "bookspider"
    #lista de dominios que gostariamos que nosso scrapy pegue, evitando que pegue varios sites da internet
    allowed_domains = ["books.toscrape.com"]
    
    #a primeira url que o spider começar, e podemos ter uma lista para buscar uma atrás da outra
    start_urls = ["https://books.toscrape.com"]

    custom_settings = {
        'FEEDS': { 'data.csv': { 'format': 'csv', 'overwrite':True}}
        }

    
    #Função que será chamada uma vez após a requisição voltar (no response)
    def parse(self, response):
        books = response.css('article.product_pod')
        for book in books:
            relative_url = book.css('h3 a ::attr(href)').get()

            if 'catalogue/' in relative_url:
                book_url = 'https://books.toscrape.com/'+ relative_url
            else:
                book_url = 'https://books.toscrape.com/catalogue/'+ relative_url

           
            yield response.follow(book_url, callback=self.parse_book_page)

        next_page = response.css('li.next a ::attr(href)').get() 
        if next_page is not None:
            #algumas páginas podem ter ou não os dados do catalolgo
            if 'catalogue/' in next_page:
                next_page_url = 'https://books.toscrape.com/'+ next_page
            else:
                next_page_url = 'https://books.toscrape.com/catalogue/'+ next_page

            #reponse.follow vai até aurl e executa uma função
            yield response.follow(next_page_url, callback=self.parse)

    def parse_book_page(self, response):
        book = response.css("div.product_main")[0]
        table_rows = response.css("table tr")
        
        book_item = BookItem()
      
        book_item['url']= response.url
        book_item['title']= book.css("h1 ::text").get()
        book_item['upc']= table_rows[0].css("td ::text").get()
        book_item['product_type']= table_rows[1].css("td ::text").get()
        book_item['price_excl_tax']= table_rows[2].css("td ::text").get()
        book_item['price_incl_tax']= table_rows[3].css("td ::text").get()
        book_item['tax']= table_rows[4].css("td ::text").get()
        book_item['availability']= table_rows[5].css("td ::text").get()
        book_item['num_reviews']= table_rows[6].css("td ::text").get()
        book_item['stars']= book.css("p.star-rating").attrib['class']
        book_item['category']= book.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get()
        book_item['description']= book.xpath("//div[@id='product_description']/following-sibling::p/text()").get()
        book_item['price']= book.css('p.price_color ::text').get()
    
        
        yield book_item
        