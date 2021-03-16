from crawler_world import get_page, all_offers_links, Car, cars_list


def crawler():
    print('Hello to the Otomoto Crawler.\n Example address: https://www.otomoto.pl/osobowe/volkswagen/caravelle/')
    url = input('Please give a URL search address from Otomoto page: ')
    bs = get_page(url)
    links = all_offers_links(bs, url)
    print(f'Number of offers found: {len(links)}.\nAnalyzing offers...')
    return cars_list(links, Car)


if __name__ == '__main__':
    data = crawler()
    expired_counter = 0
    for car in data:
        if car == 'Expired':
            expired_counter += 1
            continue
        print(dir(car))
    print(f'Number of expired offers: {expired_counter}')


