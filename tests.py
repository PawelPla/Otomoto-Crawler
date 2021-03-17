import unittest
from unittest.mock import patch
import requests
from bs4 import BeautifulSoup
from crawler_world import (
    get_page, page_is_404, assemble_url_page, get_search_page_links, num_search_pages, request_redirected,
)


def search_results_counter(bs_search_obj) -> int:
    counter = bs_search_obj.find('span', {'class': 'fleft tab selected'}).find('span', class_='counter').get_text()
    result_num = ''.join([char for char in counter if char.isdigit()])
    return int(result_num)

def test_search_html():
    with open('test_search.html') as f:
        data = f.read()
    return data

def test_offer_html():
    with open('test_offer.html') as f:
        data = f.read()
    return data


class SearchPageTest(unittest.TestCase):
    def setUp(self):
        self.valid_url = 'https://www.otomoto.pl/osobowe/audi/a4/'
        self.valid_url_resp = requests.get(self.valid_url)
        self.page_404 = 'https://www.otomoto.pl/osobowe/kaudi/a4/'
        self.page_404_resp = requests.get(self.page_404)
        self.page_redirected = 'https://www.otomoto.pl/osobowe/audi/jibrish/'
        self.static_search_page = test_search_html()
        self.static_search_page_bs_obj = BeautifulSoup(self.static_search_page, 'html.parser')
        self.offer_page = test_offer_html()
        self.offer_page_bs_obj = BeautifulSoup(self.offer_page, 'html.parser')

    def test_page_is_404(self):
        self.assertTrue(page_is_404(self.page_404_resp))
        self.assertFalse(page_is_404(self.valid_url_resp))

    def test_request_redirected(self):
        res = requests.get(self.valid_url)
        redirected = requests.get(self.page_redirected)
        self.assertTrue(request_redirected(self.page_redirected, redirected))
        self.assertFalse(request_redirected(self.valid_url, res))

    def test_get_page(self):
        self.assertIsInstance(get_page(self.valid_url), BeautifulSoup)

    @patch('crawler_world.ask_for_manufacturer', return_value='audi')
    @patch('crawler_world.ask_for_model', return_value='a4')
    def test_assemble_url_page(self, manuf, model):
        res = assemble_url_page()
        self.assertEqual(res, self.valid_url)
        self.assertIsInstance(res, str)

    def test_get_search_page_links(self):
        bs_obj = BeautifulSoup(requests.get(self.valid_url).text, 'html.parser')
        links = get_search_page_links(bs_obj)
        self.assertIsInstance(links, list)
        for link in links:
            self.assertEqual(requests.get(link).status_code, 200)

    def test_num_search_pages(self):
        page_obj = self.static_search_page_bs_obj
        res = num_search_pages(page_obj)
        self.assertTrue(res.isdigit())
        self.assertIsInstance(res, str)
        self.assertEqual(res, str(2))
if __name__ == '__main__':
    unittest.main()
