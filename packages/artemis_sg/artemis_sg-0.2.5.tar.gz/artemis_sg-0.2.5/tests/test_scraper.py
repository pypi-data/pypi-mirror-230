import json
import logging
import os
import time
from unittest.mock import Mock

import pytest
from selenium.common.exceptions import NoSuchElementException

import artemis_slide_generator.items as items
import artemis_slide_generator.scraper as scraper


@pytest.fixture()
def mock_delay():
    def my_delay(num):
        return

    return my_delay


@pytest.fixture()
def sample_item_list():
    isbn13a = "9780802157003"
    isbn13b = "9780691025551"
    description_a = "Cool item Dude!"
    description_b = "Totally awesome item!"
    item_list = [
        ["ISBN", "description"],
        [isbn13a, description_a],
        [isbn13b, description_b],
    ]
    return item_list


@pytest.fixture()
def sample_scraped_data():
    isbn13a = "9780802157003"
    isbn13b = "9780691025551"
    isbn10a = "0802157009"
    isbn10b = "069102555X"
    description_a = "Cool item Dude!"
    description_b = "Totally awesome item!"
    image_urls = [
        "https://example.com/images/image_001.jpg",
        "https://example.com/images/image_002.jpg",
    ]
    sample_data = {
        isbn13a: {
            "isbn10": isbn10a,
            "description": description_a,
            "image_urls": image_urls,
        },
        isbn13b: {
            "isbn10": isbn10b,
            "description": description_b,
            "image_urls": image_urls,
        },
    }
    return sample_data


@pytest.fixture()
def expected_scraped_data():
    isbn13a = "9780802157003"
    isbn13b = "9780691025551"
    isbn10a = "0802157009"
    isbn10b = "069102555X"
    description_a = "Cool item Dude!"
    description_b = "Totally awesome item!"
    image_urls = [
        "https://example.com/images/image_001.jpg",
        "https://example.com/images/image_002.jpg",
    ]
    sample_data = {
        isbn13a: {
            "ISBN": isbn13a,
            "isbn10": isbn10a,
            "description": description_a,
            "image_urls": image_urls,
        },
        isbn13b: {
            "ISBN": isbn13b,
            "isbn10": isbn10b,
            "description": description_b,
            "image_urls": image_urls,
        },
    }
    return sample_data


@pytest.fixture()
def items_collection(sample_item_list):
    collection = items.Items(
        sample_item_list[0],
        sample_item_list[1:],
        "ISBN",
    )
    return collection


@pytest.fixture()
def valid_datafile(tmp_path_factory, sample_scraped_data):
    path = tmp_path_factory.mktemp("data")
    file_name = os.path.join(path, "valid.json")
    json_string = json.dumps(sample_scraped_data)
    with open(file_name, "w") as filepointer:
        filepointer.write(json_string)
    yield file_name


@pytest.fixture()
def empty_datafile(tmp_path_factory):
    path = tmp_path_factory.mktemp("data")
    file_name = os.path.join(path, "empty.json")
    yield file_name


class TestBaseScraper:
    # {{{
    def test_create_scraper(self):
        """
        GIVEN BaseScraper class
        WHEN we create Scraper object with driver and url
        THEN object's selenium_driver and base_url attributes
             are set to the given values
        """
        scrapr = scraper.BaseScraper("driver", "baseUrl")

        assert scrapr.selenium_driver == "driver"
        assert scrapr.base_url == "baseUrl"

    # }}}


class TestAmznScraper:
    # {{{
    def test_scrape_description_with_review(self, monkeypatch, mock_delay):
        """
        GIVEN a AmznScraper object with webdriver and amazon url
        AND Amazon item page with editorial review is loaded in browser
        WHEN we call scrape_description() on object
        THEN the result is the editorial review without the first two lines
        """
        # {{{
        review_text = """Editorial Reviews
Review
Praise for Earthlings:
A New York Times Book Review Editors’ Choice
Named a Best Book of the Year by TIME and Literary Hub
Named a Most Anticipated Book by the New York Times, TIME, USA Today, \
Entertainment Weekly, the Guardian, Vulture, Wired, Literary Hub, Bustle, \
Popsugar, and Refinery29
“To Sayaka Murata, nonconformity is a slippery slope . . . Reminiscent of certain \
excellent folk tales, expressionless prose is Murata’s trademark . . . \
In Earthlings, being an alien is a simple proxy for being alienated. The characters \
define themselves not by a specific notion of what they are—other—but by a general \
idea of what they are not: humans/breeders . . . The strength of [Murata’s] voice \
lies in the faux-naïf lens through which she filters her dark view of humankind: \
We earthlings are sad, truncated bots, shuffling through the world in a dream of \
confusion.”—Lydia Millet, New York Times Book Review"""
        # }}}

        class MockElement(object):
            def __init__(self, text):
                self.text = text

        global find_element_counter
        find_element_counter = 0

        def mock_find_element(*args, **kwargs):
            global find_element_counter
            find_element_counter += 1
            print("mock_find_element count = %r" % find_element_counter)
            return MockElement(review_text)

        def mock_noop(*args, **kwargs):
            pass

        class MockDriver(object):
            def find_element():
                pass

            def get():
                pass

        driver = MockDriver()
        monkeypatch.setattr(driver, "find_element", mock_find_element)
        monkeypatch.setattr(driver, "get", mock_noop)
        scrapr = scraper.AmznScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)
        scrapr.load_item_page("item_number")
        description = scrapr.scrape_description()

        expected_text = review_text.splitlines()
        expected_text.pop(0)
        expected_text.pop(0)
        expected_text = "\n".join(expected_text)
        assert description == expected_text

    def test_scrape_description_without_review(self, monkeypatch, mock_delay):
        """
        GIVEN Amazon item page without editorial review is loaded
        WHEN scrape_description is executed
        THEN description is returned
        """

        class MockElement(object):
            def __init__(self, counter):
                if counter < 2:
                    raise NoSuchElementException
                else:
                    self.text = (
                        "As a child, Natsuki doesn’t fit into her family. "
                        "Her parents favor her sister, and her best friend "
                        "is a plush toy hedgehog named Piyyut who has "
                        "explained to her that he has come from the planet "
                        "Popinpobopia on a special quest to help her save "
                        "the Earth."
                    )

        global find_element_counter
        find_element_counter = 0

        def mock_find_element(*args, **kwargs):
            global find_element_counter
            find_element_counter += 1
            print("mock_find_element count = %r" % find_element_counter)
            return MockElement(find_element_counter)

        def mock_noop(*args, **kwargs):
            pass

        class MockDriver(object):
            def find_element():
                pass

            def get():
                pass

        driver = MockDriver()
        monkeypatch.setattr(driver, "find_element", mock_find_element)
        monkeypatch.setattr(driver, "get", mock_noop)
        scrapr = scraper.AmznScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)
        scrapr.load_item_page("item_number")
        description = scrapr.scrape_description()

        assert "As a child" in description

    def test_scrape_item_image_urls(self, monkeypatch, mock_delay):
        """
        GIVEN Amazon item page with multiple item images
        WHEN scrape_item_image_urls is executed
        THEN a list of urls is returned
        """

        class MockElement(object):
            def __init__(self, counter):
                if counter < 10:
                    self.text = (
                        "https://m.media-example.com/images/I/"
                        "image-{counter}._AC_SX75_CR,0,0,75,75_.jpg"
                    ).format(counter=counter)
                else:
                    raise NoSuchElementException

            def find_element():
                pass

            def click(self):
                pass

            @staticmethod
            def get_attribute(*args, **kwargs):
                return "https://m.media-example.com/images/I/image-enterNumberHere._AC_SX75_CR,0,0,75,75_.jpg"

        global find_element_counter
        find_element_counter = 0

        def mock_find_element(*args, **kwargs):
            global find_element_counter
            find_element_counter += 1
            print("mock_find_element count = %r" % find_element_counter)
            return MockElement(find_element_counter)

        def mock_noop(*args, **kwargs):
            pass

        class MockDriver(object):
            def find_element():
                pass

            def get():
                pass

            def get_attribute():
                pass

        monkeypatch.setattr(MockDriver, "find_element", mock_find_element)
        monkeypatch.setattr(MockElement, "find_element", mock_find_element)
        driver = MockDriver()
        monkeypatch.setattr(driver, "get", mock_noop)
        scrapr = scraper.AmznScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)
        monkeypatch.setattr(scrapr, "timeout", 0)
        monkeypatch.setattr(time, "sleep", lambda x: None)

        scrapr.load_item_page("item_number")
        urls = scrapr.scrape_item_image_urls()

        assert isinstance(urls, list)
        assert (
            "https://m.media-example.com/images/I/image-enterNumberHere.jpg" in urls[0]
        )

    # }}}


class TestTBScraper:
    # {{{
    def test_scrape_description(self, monkeypatch, mock_delay):
        """
        GIVEN TB item page
        WHEN scrape_description is executed
        THEN description is returned
        """

        class MockElement(object):
            def __init__(self, counter):
                self.text = """NO AMAZON SALES

Discover the mystery and power of the natural and human worlds in this \
beautifully illustrated coloring book.

Featuring tarot cards, healing herbs and flowers, mandalas, and curious \
creatures of the night, Believe in Magic is a spellbinding celebration \
of modern witchcraft with a focus on healing, mindfulness, and meditation."""

        global find_element_counter
        find_element_counter = 0

        def mock_find_element(*args, **kwargs):
            global find_element_counter
            find_element_counter += 1
            print("mock_find_element count = %r" % find_element_counter)
            return MockElement(find_element_counter)

        def mock_noop(*args, **kwargs):
            pass

        class MockDriver(object):
            def find_element():
                pass

            def get():
                pass

        driver = MockDriver()
        monkeypatch.setattr(driver, "find_element", mock_find_element)
        monkeypatch.setattr(driver, "get", mock_noop)
        scrapr = scraper.TBScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)
        scrapr.load_item_page("item_number")
        description = scrapr.scrape_description()

        assert "NO AMAZON SALES" not in description
        assert description.startswith("Discover the mystery")

    def test_scrape_item_image_urls(self, monkeypatch, mock_delay):
        """
        GIVEN TB item page
        WHEN scrape_item_image_urls is executed
        THEN a URL list is returned
        AND the list contains the expected URL
        """
        url = "http://example.org/foo/bar.jpg"
        style = f'This is a URL "{url}"'

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        driver.find_element.side_effect = [
            elem,
            elem,
            elem,
            elem,
            elem,
            NoSuchElementException,
            NoSuchElementException,
            NoSuchElementException,
            NoSuchElementException,
            NoSuchElementException,
            NoSuchElementException,
            NoSuchElementException,
        ]
        elem.get_attribute.side_effect = [
            style,
            NoSuchElementException,
        ]
        scrapr = scraper.TBScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)
        monkeypatch.setattr(scrapr, "timeout", 0)
        monkeypatch.setattr(time, "sleep", lambda x: None)

        urls = scrapr.scrape_item_image_urls()

        assert len(urls) > 0
        assert url in urls

    def test_login(self, capsys, monkeypatch, mock_delay):
        """
        GIVEN TB login page is loaded
        WHEN `login` is executed
        THEN user input message is displayed
        """
        expected_output = "USER INPUT REQUIRED"
        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        driver.find_element.side_effect = lambda *args: elem
        scrapr = scraper.TBScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)

        scrapr.load_login_page()

        scrapr.login()
        captured = capsys.readouterr()
        assert expected_output in captured.out

    def test_impersonate(self, monkeypatch, mock_delay):
        """
        GIVEN TBScraper instance
        WHEN `impersonate` is executed with a given valid email
        THEN the result is True
        AND the email has been searched for via the 'customers-grid' XPATH
        """
        email = "foo@example.org"
        email_xpath = (
            f"//div[@id='customers-grid']/table/tbody/tr/td/a[text()='{email}']"
        )

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        driver.find_element.side_effect = lambda *args: elem
        driver.find_elements.side_effect = lambda *args: [elem]

        scrapr = scraper.TBScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)

        res = scrapr.impersonate(email)

        assert res is True
        driver.find_element.assert_any_call("xpath", email_xpath)

    def test_impersonate_multiple_customer_records(
        self, caplog, monkeypatch, mock_delay
    ):
        """
        GIVEN TBScraper instance
        AND an email associated with multiple customer records
        WHEN `impersonate` is executed with that email
        THEN an exception is thrown
        """
        email = "foo@example.org"
        email_xpath = (
            f"//div[@id='customers-grid']/table/tbody/tr/td/a[text()='{email}']"
        )

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        driver.find_element.side_effect = lambda *args: elem
        driver.find_elements.side_effect = lambda *args: [elem, elem]

        scrapr = scraper.TBScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)

        try:
            res = scrapr.impersonate(email)
            driver.find_element.assert_any_call("xpath", email_xpath)
            assert res is True
        except Exception:
            assert (
                "root",
                logging.ERROR,
                (
                    "TBScraper.impersonate: Found multiple customer records for "
                    "email '{email}' to impersonate"
                ).format(email=email),
            ) in caplog.record_tuples

    def test_add_to_cart(self, monkeypatch, mock_delay):
        """
        GIVEN TB item page
        WHEN add_to_cart is executed with a given quantity
        THEN the cart contains the given quantity of the item
        """
        qty = "42"

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        driver.find_element.side_effect = [
            elem,
            elem,
            elem,
        ]
        elem.text = "999"
        scrapr = scraper.TBScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)

        res = scrapr.add_to_cart(qty)

        assert res == int(qty)

    def test_add_to_cart_adjust_qty(self, monkeypatch, mock_delay):
        """
        GIVEN TB item page
        WHEN add_to_cart is executed with a given quantity
             that is greater than available
        THEN the available quantity is returned
        """
        qty = "42"
        available = "10"

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        driver.find_element.side_effect = [
            elem,
            elem,
            elem,
        ]
        elem.text = f"Availability: {available} in stock"
        scrapr = scraper.TBScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)

        res = scrapr.add_to_cart(qty)

        assert res == int(available)

    def test_load_cart_page(self, monkeypatch, mock_delay):
        """
        GIVEN an TBScraper object
        WHEN `load_cart_page` is executed on that object
        THEN the result is True
        """
        driver = Mock(name="mock_driver")

        scrapr = scraper.TBScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)

        res = scrapr.load_cart_page()

        assert res

    # }}}


class TestSDScraper:
    # {{{
    def test_scrape_description(self, monkeypatch, mock_delay):
        """
        GIVEN SD item page
        WHEN scrape_description is executed
        THEN description is returned
        """
        expected_description = "Hello, World!"

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        driver.find_element.side_effect = [
            elem,
            elem,
            elem,
            elem,
        ]
        monkeypatch.setattr(elem, "text", expected_description)
        scrapr = scraper.SDScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)
        scrapr.load_item_page("item_number")
        description = scrapr.scrape_description()

        assert description == expected_description

    def test_scrape_item_image_urls(self, monkeypatch, mock_delay):
        """
        GIVEN SD item page
        WHEN scrape_item_image_urls is executed
        THEN a URL list is returned
        AND the list contains the expected URL
        """

        url = "http://example.org/foo/bar.jpg"

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        driver.find_element.side_effect = [
            elem,
            elem,
            elem,
            elem,
        ]

        def mock_find_elements(*args, **kwargs):
            return [elem, elem, elem]

        def mock_get_attribute(*args, **kwargs):
            return url

        monkeypatch.setattr(driver, "find_elements", mock_find_elements)
        monkeypatch.setattr(elem, "get_attribute", mock_get_attribute)
        scrapr = scraper.SDScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)

        scrapr.load_item_page("item_number")
        urls = scrapr.scrape_item_image_urls()
        assert len(urls) > 0
        assert url in urls

    def test_login(self, capsys, monkeypatch, mock_delay):
        """
        GIVEN SD login page is loaded
        WHEN `login` is executed
        THEN user input message is displayed
        """
        expected_output = "USER INPUT REQUIRED"
        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        driver.find_element.side_effect = [
            elem,
            elem,
        ]
        scrapr = scraper.SDScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)

        scrapr.load_login_page()

        scrapr.login()
        captured = capsys.readouterr()
        assert expected_output in captured.out

    def test_add_to_cart(self, monkeypatch, mock_delay):
        """
        GIVEN SD item page
        AND user is logged into SD
        WHEN add_to_cart is executed with a given quantity
        THEN the given quantity is returned
        """
        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        driver.find_element.side_effect = [
            elem,
            elem,
            elem,
        ]
        elem.find_element.side_effect = [
            elem,
        ]
        driver.find_elements.side_effect = [
            [
                elem,
                elem,
            ]
        ]

        scrapr = scraper.SDScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)
        monkeypatch.setattr(elem, "get_attribute", lambda attr: "foo")
        monkeypatch.setattr(elem, "text", "Add to cart")

        scrapr.load_login_page()

        res = scrapr.add_to_cart("42")

        assert res == 42

    def test_add_to_cart_adjust_qty(self, monkeypatch, mock_delay):
        """
        GIVEN SD item page
        AND user is logged into SD
        WHEN add_to_cart is executed with a given quantity
             that is greater than available
        THEN the available quantity is returned
        """
        qty = "42"
        available = 10

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        driver.find_element.side_effect = [
            elem,
            elem,
            elem,
        ]
        elem.find_element.side_effect = [
            elem,
            elem,
        ]
        driver.find_elements.side_effect = [
            [
                elem,
                elem,
            ]
        ]

        scrapr = scraper.SDScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)
        monkeypatch.setattr(elem, "get_attribute", lambda attr: f"{available} in stock")
        monkeypatch.setattr(elem, "text", "Add to cart")

        scrapr.load_login_page()

        res = scrapr.add_to_cart(qty)

        assert res == available

    def test_load_cart_page(self, monkeypatch, mock_delay):
        """
        GIVEN an SDScraper object
        WHEN `load_cart_page` is executed on that object
        THEN the result is True
        """
        driver = Mock(name="mock_driver")

        scrapr = scraper.SDScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)

        res = scrapr.load_cart_page()

        assert res

    # }}}


class TestGJScraper:
    # {{{
    def test_scrape_description(self, monkeypatch, mock_delay):
        """
        GIVEN GJ item page
        WHEN scrape_description is executed
        THEN description is returned
        """
        expected_description = "Hello, World!"

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        monkeypatch.setattr(elem, "text", expected_description)
        driver.find_element.side_effect = [
            elem,
            elem,
            elem,
            elem,
            elem,
            elem,
            elem,
            elem,
        ]
        elem.find_element.side_effect = [
            elem,
        ]
        driver.find_elements.side_effect = [
            [
                elem,
                elem,
            ]
        ]
        scrapr = scraper.GJScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)
        scrapr.load_item_page("item_number")
        description = scrapr.scrape_description()

        assert description == expected_description

    def test_scrape_item_image_urls(self, monkeypatch, mock_delay):
        """
        GIVEN GJ item page
        WHEN scrape_item_image_urls is executed
        THEN a URL list is returned
        AND the list contains the expected URL
        """

        url = "http://example.org/foo/bar.jpg"

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        driver.find_element.side_effect = [
            elem,
            elem,
            elem,
            elem,
            elem,
            elem,
            elem,
            elem,
        ]
        elem.find_element.side_effect = [
            elem,
        ]
        driver.find_elements.side_effect = [
            [
                elem,
                elem,
            ]
        ]

        def mock_get_attribute(*args, **kwargs):
            return url

        monkeypatch.setattr(elem, "get_attribute", mock_get_attribute)
        monkeypatch.setattr(elem, "text", "foo")
        scrapr = scraper.GJScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)

        scrapr.load_item_page("item_number")
        urls = scrapr.scrape_item_image_urls()
        assert len(urls) > 0
        assert url in urls

    def test_login(self, capsys, monkeypatch, mock_delay):
        """
        GIVEN GJ login page
        WHEN login is executed
        THEN user input message is displayed
        """
        expected_output = "USER INPUT REQUIRED"

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        driver.find_element.side_effect = [
            elem,
        ]

        scrapr = scraper.GJScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)

        scrapr.load_login_page()

        scrapr.login()
        captured = capsys.readouterr()
        assert expected_output in captured.out

    def test_add_to_cart(self, monkeypatch, mock_delay):
        """
        GIVEN GJ item page
        AND user is logged into GJ
        WHEN add_to_cart is executed with a given quantity
        THEN the cart contains the given quantity of the item
        """

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        driver.find_element.side_effect = [
            elem,
            elem,
        ]
        elem.find_element.side_effect = [
            elem,
            elem,
        ]

        scrapr = scraper.GJScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)
        monkeypatch.setattr(elem, "text", "foo")

        scrapr.load_login_page()

        res = scrapr.add_to_cart("42")

        assert res == 42

    def test_add_to_cart_adjust_qty(self, monkeypatch, mock_delay):
        """
        GIVEN GJ item page
        AND user is logged into GJ
        WHEN add_to_cart is executed with a given quantity
             that is greater than available
        THEN the cart contains the available quantity of the item
        """
        qty = "42"
        available = 10

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        driver.find_element.side_effect = [
            elem,
            elem,
        ]
        elem.find_element.side_effect = [
            elem,
            elem,
        ]

        scrapr = scraper.GJScraper(driver)
        monkeypatch.setattr(scrapr, "delay", mock_delay)
        monkeypatch.setattr(elem, "text", f"{available} in stock")

        scrapr.load_login_page()

        res = scrapr.add_to_cart(qty)

        assert res == available

    # }}}
