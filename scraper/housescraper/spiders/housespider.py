import scrapy
import re
from housescraper.items import HouseItem


class HousespiderSpider(scrapy.Spider):
    name = "housespider"
    allowed_domains = ["house.kg"]
    start_urls = ["https://www.house.kg/kupit-kvartiru?rooms=2"]

    base_url = "https://www.house.kg"

    def parse(self, response):
        apartments_2 = response.css(".listings-wrapper .listing")

        for apartment in apartments_2:
            relative_url = apartment.css(".title a::attr(href)").get()
            house_url = self.base_url + relative_url

            yield response.follow(house_url, callback=self.parse_house_page)

        next_page = response.css("a[aria-label=Вперед]::attr(href)").get()
        page_value = int(next_page.split("page=")[1])

        if next_page is not None and page_value <= 2:
            next_page_url = self.base_url + next_page
            yield response.follow(next_page_url, callback=self.parse)

    def parse_house_page(self, response):
        house_item = HouseItem()

        upped_value = response.xpath(
            '//*[@id="homepage"]/div[7]/div/div[2]/div[3]/div[2]/div[1]/span[1]/span[2]/text()'
        ).extract_first()

        house_item['link'] = response.request.url,
        house_item['header'] = response.css(".left h1::text").get(),
        house_item['address'] =  response.css(".left .address::text").get(),
        house_item['price'] = response.css(".right .price-dollar::text").get(),
        house_item['upped'] =  upped_value if upped_value else "Не поднималось",
        house_item['image_url'] = response.css('a[itemprop="image"]::attr(href)').extract_first(),
        house_item['details'] =  self.parse_house_details(response),
        
        yield house_item

    def parse_house_details(self, response):
        result = []
        rows = response.css(".details-main .info-row")

        for row in rows:
            label = row.css(".label::text").get().strip("\n").strip()
            info = re.sub(
                r",\s+",
                ", ",
                row.css(".info::text").get().strip("\n").strip()
                if label != "Тип предложения"
                else row.css("span::text").get().strip("\n").strip(),
            )

            result.append({"label": label, "info": info})

        return result

