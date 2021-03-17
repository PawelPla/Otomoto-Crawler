import requests
from bs4 import BeautifulSoup, NavigableString


class Car:
    def __init__(self, parameters, values):
        for (key, value) in zip(parameters, values):
            self.__dict__[key] = value


# FOLLOWING functions act upon primary search page
def ask_for_manufacturer() -> str:
    manuf = input('Enter the car Manufacturer: ')
    return manuf.lower().strip()


def ask_for_model() -> str:
    model = input('Enter the car Model: ')
    return model.lower().strip()


def assemble_url_page() -> str:
    producer = ask_for_manufacturer()
    model = ask_for_model()
    return f'https://www.otomoto.pl/osobowe/{producer}/{model}/'


def page_is_404(response) -> bool:
    if response.status_code == 404:
        return True
    elif response.status_code == 200:
        return False


def request_redirected(requested_url: str, response) -> bool:
    if requested_url != response.url:
        return True
    elif requested_url == response.url:
        return False


def page_not_found(url: str) -> bool:
    '''
    Checks whether http code is 404 or response page is not the one requested due to redirection
    :param url: requested URL
    :return: True if requested page not found. False if found
    '''
    response = requests.get(url)
    if request_redirected(requested_url=url, response=response):
        return True
    elif page_is_404(response=response):
        return True
    return False


def get_page(url: str):
    '''
    Provides the BeautifulSoup object for a given url
    :param url: String of url to the certain page
    :return: BS_object
    '''
    return BeautifulSoup(requests.get(url).text, 'html.parser')


def get_search_page_links(result_tag) -> list:
    '''
    Searches for all offers links on the single search page via result_tag BS_object
    :param result_tag: BeautifulSoup_object that is a result tag for offers on a given search page
    :return: Returns a list of all offers links found on the particular page
    '''
    return [res.attrs['data-href'] for res in result_tag.find_all('article') if not isinstance(res, NavigableString)]


def num_search_pages(bs_obj) -> str:
    '''
    :param bs_obj: BeautifulSoup whole search-page object
    :return: str of Number of search pages
    '''
    pages_tag = bs_obj.find('ul', {'class': 'om-pager rel'})
    if pages_tag is None:
        return ''
    num = 0
    for page in pages_tag.find_all('span', {'class': 'page'}):
        num = page.get_text()
    return num


def all_offers_links(
        bs_obj,
        url: str,
        pages_counter=num_search_pages,
        search_url: str = '?search%5Border%5D=created_at%3Adesc&page=',
        links_finder=get_search_page_links):
    '''
    :param bs_obj: First search page BeautifulSoup object
    :param url: URL of the first search page
    :param pages_counter: Function that returns total number of search pages
    :param search_url: string of search url
    :param links_finder: Function that finds links to the offers on a given BS-page object
    :return: Returns full list of links to the offers
    '''
    links = links_finder(bs_obj)
    num_pages = pages_counter(bs_obj)
    if not num_pages:
        return links
    for page_num in range(2, int(num_pages) + 1):
        bs = get_page(url + search_url + str(page_num))
        links.extend(links_finder(bs))
    return links


# FOLLOWING functions act upon single offer page:
def get_params_tag(bs_obj):
    """
    Gets BS tag where all crucial offer parameters are located
    :param bs_obj: General BS_object of the page
    :return: BS_tag or None if the offer's expired
    """
    with_vin = bs_obj.find('div', {'class': 'offer-params with-vin'})
    without_vin = bs_obj.find('div', {'class': 'offer-params'})
    expired = bs_obj.find('span', {'class': 'subtitle'})
    if with_vin is not None:
        return with_vin.ul
    elif without_vin is not None:
        return without_vin.ul
    elif expired is not None:
        print('Expired offer')
        return None


def expired_offer(param_tag):
    if param_tag is None:
        return True


def parameter_key(param_tag):
    return param_tag.span.get_text().strip()


def parameter_value(param_tag):
    return param_tag.div.get_text().strip()


def get_params_dict(params_tag):
    data = {}
    for param in params_tag:
        if isinstance(param, NavigableString):
            continue
        if 'offer-params__item' in param.attrs['class']:
            data[parameter_key(param)] = parameter_value(param)
    return data


def get_params_obj(params_tag, car_instance) -> object:
    '''
    Function traversing through all offer parameters and assigning them into instance of the class
    :param params_tag: BeautifulSoup tag object that contains all offer parameters
    :param car_instance: class that holds offer parameters as attributes
    :return: Instance of an object with attrs. of all parameters provided
    '''
    if expired_offer(params_tag):
        return None
    params = []
    values = []
    for param in params_tag:
        if isinstance(param, NavigableString):
            continue
        if 'offer-params__item' in param.attrs['class']:
            params.append(parameter_key(param))
            values.append(parameter_value(param))
    return car_instance(params, values)


def cars_list(links: list, car_class) -> list:
    '''
    Function that creates a list of Car objects
    :param links: List of offers links
    :param car_class: Car class
    :return: List of Car class objects
    '''
    return [get_params_obj(get_params_tag(get_page(link)), car_class) for link in links]
