# import feapder
#
# class TestFeapder(feapder.AirSpider):
#     def start_requests(self):
#         yield feapder.Request("https://spidertools.cn", render=True)
#
#     def parse(self, request, response):
#         # 提取网站title
#         print(response.xpath("//title/text()").extract_first())
#         # 提取网站描述
#         print(response.xpath("//meta[@name='description']/@content").extract_first())
#         print("网站地址: ", response.url)
#
# TestFeapder().start()

from feapder.network.proxy_pool import ProxyPool

proxy_pool = ProxyPool()
proxy = proxy_pool.get_proxy()