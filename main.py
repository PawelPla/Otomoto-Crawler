from crawler_world import get_page, all_offers_links, Car, cars_list, assemble_url_page, page_not_found


def crawler():
    print('Hello to the Otomoto Crawler.\n\nExample input: volkswagen\tgolf')
    url = assemble_url_page()
    while page_not_found(url):
        print('Page not found!\nPlease try again!')
        url = assemble_url_page()
    bs = get_page(url)
    links = all_offers_links(bs, url)
    print(f'Number of offers found: {len(links)}.\nAnalyzing offers...')
    return cars_list(links, Car)


if __name__ == '__main__':
    data = crawler()
    expired_counter = 0
    for car in data:
        if car is None:
            expired_counter += 1
            continue
        print(dir(car))
    print(f'Number of offers expired during runtime: {expired_counter}')

