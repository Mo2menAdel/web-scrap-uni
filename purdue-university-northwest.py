import os
from scrapy.crawler import CrawlerProcess
import scrapy
import logging

class PurdueSpider(scrapy.Spider):
    name = 'purdue'
    page_number = 2
    start_urls = [
        'https://catalog.pnw.edu/content.php?catoid=11&navoid=1623&fbclid=IwAR2w6o35FmuXM8ZKMcDJQtJA_fVpvK_1ApJfxDdh9b-uC10HTi7OBLJwuuQ'
    ]



    def parse(self, response, **kwargs):
        #items = QuotetutorialItem()
        items = {}

        all_subs = response.css(".width a::attr(href)").getall()

        for sub in all_subs:
            yield response.follow(sub, callback=self.parse2)

        next_page = "https://catalog.pnw.edu/content.php?catoid=11&catoid=11&navoid=1623&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D=" + str(PurdueSpider.page_number) + "#acalog_template_course_filter"

        if PurdueSpider.page_number <= 27:
            PurdueSpider.page_number += 1
            yield response.follow(next_page, callback=self.parse)



    def parse2(self, response):
        item = {}
        titleAndCode = response.css('#course_preview_title::text').extract()
        temp = titleAndCode[0]
        temp2 = ""
        temp3 = ""
        i = 0
        dot_count = 0
        item['code'] = titleAndCode[0].split()[0] + " " + titleAndCode[0].split()[1]
        x = ""
        for title in titleAndCode[0].split()[2:]:
            x += title + " "
        item['title'] = x[1:].strip()


        # Credit houres is appended in desc. seperate them
        if len(response.css('.block_content strong::text').extract()) >= 2:
            if response.css('.block_content strong::text')[1].extract() == 'Prerequisite(s):':
                desc = response.css('td.block_content::text')[3].extract()
            else:
                desc = max(response.css('td.block_content::text')[1:6].extract(), key=len)
        else:
            desc = max(response.css('td.block_content::text')[1:6].extract(), key=len)


        for ch in desc:
            if ch == '.':
                dot_count +=1
                if dot_count == 2 & ~desc[i+6].isdigit():
                    break
            temp2 += ch
            i += 1
        item['credit'] = temp2.lower().replace('credits', '').replace('hours', '').replace('credit', '').replace('hours', '').replace(',', '').replace(':', '').strip()
            # os.system('touch test2.txt')
                # print("---------------------------------***************************--------------------")
        for ch in desc[i:]:
            temp3 += ch
        item['description'] = temp3
        yield item
# strong:nth-child(11)

crawler = CrawlerProcess(settings={
    "FEEDS":{"output/purdue-university-northwest.csv":{"encoding":"utf8","format":"csv", "overwrite": True}},
    "LOG_LEVEL":logging.DEBUG
})
crawler.crawl(PurdueSpider)
crawler.start(stop_after_crawl=True)
