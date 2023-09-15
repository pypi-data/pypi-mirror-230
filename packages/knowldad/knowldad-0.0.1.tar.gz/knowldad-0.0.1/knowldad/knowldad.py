class Knowldad:
    def __init__(self):
        print('Hello, world!')

# import crawldad
# import tiktoken
# 
# embedding_model = 'text-embedding-ada-002'
# encoding = tiktoken.encoding_for_model(embedding_model)
# 
# def on_soup_event(soup, url):
#     print(url)
#     if url.startswith('https://pigweed.dev'):
#         main_content = soup.find('div', class_='main')
#         sections = main_content.find_all('section')
#         for section in sections:
#             token_count = len(encoding.encode(section.prettify()))
#             print(token_count)
# 
# def main():
#     crawler = crawldad.Crawler('https://pigweed.dev')
#     crawler.set_event_listener('soup', on_soup_event)
#     crawler.crawl()
# 
# if __name__ == '__main__':
#     main()
