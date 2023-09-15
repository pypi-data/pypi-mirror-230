import os
from unittest.mock import Mock

import pytest
from click.testing import CliRunner

import artemis_slide_generator.cli as cli


@pytest.fixture()
def target_directory(tmp_path_factory):
    path = tmp_path_factory.mktemp("data")
    yield path


@pytest.fixture()
def mock_countdown():
    def my_countdown(num, driver):
        return

    return my_countdown


def test_scrape_without_vendor(monkeypatch):
    """
    GIVEN cli
    WHEN the scrape sub-command is called without a vendor argument
    THEN an error exit code occurs
    AND usage text is displayed
    """

    def mock_method(*args):
        pass

    monkeypatch.setattr(cli, "scraper_wrapper", mock_method)

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["scrape"])

    assert result.exit_code != 0
    assert "Try 'cli scrape --help'" in result.output


def test_scrape_with_args_and_debug(monkeypatch):
    """
    GIVEN cli
    WHEN the scrape sub-command is called with a vendor argument
    AND a sheet_id argument
    AND a sheet_tab argument
    AND the debug flag
    THEN scraper is run with vendor
    AND debug mode is enabled
    """

    def mock_method(*args):
        pass

    monkeypatch.setattr(cli, "scraper_wrapper", mock_method)

    vendor_code = "AWESOME_VENDOR"
    sheet_id = "TEST_SHEET_ID"
    sheet_tab = "TEST_SHEET_TAB"

    runner = CliRunner()
    result = runner.invoke(
        cli.cli, ["--debug", "scrape", vendor_code, sheet_id, sheet_tab]
    )

    assert result.exit_code == 0
    assert "Debug mode enabled" in result.output
    assert f"Running scraper for '{vendor_code}'" in result.output
    assert f"on tab: '{sheet_tab}' of id: '{sheet_id}'" in result.output
    assert "saving to 'scraped_items.json'..." in result.output


def test_download(monkeypatch):
    """
    GIVEN cli
    WHEN the download sub-command is called
    THEN image downloader is run
    """

    def mock_method(*args):
        pass

    monkeypatch.setattr(cli, "img_downloader_wrapper", mock_method)

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["download"])

    assert result.exit_code == 0
    assert "Running image downloader..." in result.output


def test_upload(monkeypatch):
    """
    GIVEN cli
    WHEN the upload sub-command is called
    THEN Google Cloud uploader is run
    """

    def mock_method(*args):
        pass

    monkeypatch.setattr(cli, "gcloud_wrapper", mock_method)

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["upload"])

    assert result.exit_code == 0
    assert "Running Google Cloud uploader..." in result.output


@pytest.mark.parametrize("option", ("-t", "--title"))
def test_generate(option, monkeypatch):
    """
    GIVEN cli
    WHEN the generate sub-command is called with a title and vendor
    THEN slide generator is run with given title and vendor
    """

    def mock_method(*args):
        pass

    monkeypatch.setattr(cli, "slide_generator_wrapper", mock_method)

    title = "Badass Deck"
    vendor_code = "AWESOME_VENDOR"
    sheet_id = "TEST_SHEET_ID"
    sheet_tab = "TEST_SHEET_TAB"

    runner = CliRunner()
    result = runner.invoke(
        cli.cli, ["generate", option, title, vendor_code, sheet_id, sheet_tab]
    )

    assert result.exit_code == 0
    assert (
        f"Running slide generator to create slide deck '{title}' for '{vendor_code}'"
        in result.output
    )
    assert f"using tab: '{sheet_tab}' of id: '{sheet_id}'..." in result.output


def test_generate_no_title(monkeypatch):
    """
    GIVEN cli
    WHEN the generate sub-command is called without a title
    AND with a vendor
    THEN slide generator is run with default title
    """

    def mock_method(*args):
        pass

    monkeypatch.setattr(cli, "slide_generator_wrapper", mock_method)

    title = "New Arrivals"
    vendor_code = "AWESOME_VENDOR"
    sheet_id = "TEST_SHEET_ID"
    sheet_tab = "TEST_SHEET_TAB"

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["generate", vendor_code, sheet_id, sheet_tab])

    assert result.exit_code == 0
    assert (
        f"Running slide generator to create slide deck '{title}' for '{vendor_code}'"
        in result.output
    )
    assert f"using tab: '{sheet_tab}' of id: '{sheet_id}'..." in result.output


def test_generate_no_vendor(monkeypatch):
    """
    GIVEN cli
    WHEN the generate sub-command is called without a vendor
    THEN an error exit code occurs
    AND usage text is displayed
    """

    def mock_method(*args):
        pass

    monkeypatch.setattr(cli, "slide_generator_wrapper", mock_method)

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["generate"])

    assert result.exit_code != 0
    assert "Try 'cli generate --help'" in result.output


def test_sheet_image(monkeypatch):
    """
    GIVEN cli
    WHEN the sheet-image sub-command is called with a vendor argument
    AND a workbook
    AND a worksheet
    THEN sheet-image is run with given workbook and worksheet
    """

    def mock_method(*args):
        pass

    monkeypatch.setattr(cli, "sheet_image_wrapper", mock_method)

    thumb_dir = os.path.join("downloaded_images", "thumbnails")
    vendor_code = "AWESOME_VENDOR"
    workbook = "myWorkBook"
    worksheet = "myWorkSheet"
    runner = CliRunner()
    result = runner.invoke(cli.cli, ["sheet-image", vendor_code, workbook, worksheet])

    expected_msg = (
        f"Running sheet-image on '{workbook}/{worksheet}' for '{vendor_code}'"
        f"with images from '{thumb_dir}', saving to 'out.xlsx'..."
    )
    assert result.exit_code == 0
    assert expected_msg in result.output


def test_sheet_image_no_worksheet(monkeypatch):
    """
    GIVEN cli
    WHEN the sheet-image sub-command is called with a vendor argument
    AND a workbook
    AND without a worksheet
    THEN an error exit code occurs
    AND usage text is displayed
    """

    def mock_method(*args):
        pass

    monkeypatch.setattr(cli, "sheet_image_wrapper", mock_method)

    vendor_code = "AWESOME_VENDOR"
    workbook = "myWorkBook"
    runner = CliRunner()
    result = runner.invoke(cli.cli, ["sheet-image", vendor_code, workbook])

    assert result.exit_code != 0
    assert "Try 'cli sheet-image --help'" in result.output


def test_mkthumbs(monkeypatch, target_directory):
    """
    GIVEN cli
    WHEN the mkthumbs sub-command is called
    THEN mkthumbs is run
    """

    def mock_method(*args):
        pass

    monkeypatch.setattr(cli, "mkthumbs", mock_method)

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["mkthumbs", "--image-directory", target_directory])

    image_directory = target_directory
    assert result.exit_code == 0
    assert f"Running mkthumbs on images in '{image_directory}'..." in result.output


def test_order(monkeypatch, mock_countdown):
    """
    GIVEN cli
    WHEN the order sub-command is called with a vendor argument
    AND a workbook
    AND a worksheet
    THEN order is run for the given vendor with given workbook and worksheet
    AND spreadsheet.get_order_items is called
    """
    item_id = "foo"
    qty = "42"
    vendor_code = "gj"
    workbook = "myWorkBook"
    worksheet = "myWorkSheet"

    mock_spreadsheet = Mock(name="mock_spreadsheet")
    mock_spreadsheet.get_order_items.return_value = [(item_id, qty)]
    mock_scraper = Mock(name="mock_scraper")
    monkeypatch.setattr(cli, "spreadsheet", mock_spreadsheet)
    monkeypatch.setattr(cli, "scraper", mock_scraper)
    monkeypatch.setattr(cli, "countdown", mock_countdown)

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["order", vendor_code, workbook, worksheet])

    expected_msg = (
        f"Running order on '{workbook}/{worksheet}' for '{vendor_code}'"
        f"Adding items to cart..."
    )

    mock_spreadsheet.get_order_items.assert_called()
    mock_scraper.GJScraper().load_item_page.assert_any_call(item_id)
    mock_scraper.GJScraper().add_to_cart.assert_called_with(qty)
    assert expected_msg in result.output
    assert result.exit_code == 0


def test_order_with_email(monkeypatch, mock_countdown):
    """
    GIVEN cli
    WHEN the order sub-command is called with a vendor argument
    AND a workbook
    AND a worksheet
    AND an email
    THEN order is run for the given vendor with given workbook and worksheet and email
    AND spreadsheet.get_order_items is called
    """
    item_id = "foo"
    qty = "42"
    email = "foo@example.org"
    vendor_code = "tb"
    workbook = "myWorkBook"
    worksheet = "myWorkSheet"

    mock_spreadsheet = Mock(name="mock_spreadsheet")
    mock_spreadsheet.get_order_items.return_value = [(item_id, qty)]
    mock_scraper = Mock(name="mock_scraper")
    monkeypatch.setattr(cli, "spreadsheet", mock_spreadsheet)
    monkeypatch.setattr(cli, "scraper", mock_scraper)
    monkeypatch.setattr(cli, "countdown", mock_countdown)

    runner = CliRunner()
    result = runner.invoke(
        cli.cli, ["order", "--email", email, vendor_code, workbook, worksheet]
    )

    expected_msg = (
        f"Running order on '{workbook}/{worksheet}' for '{vendor_code}'"
        f"Adding items to cart..."
    )
    mock_spreadsheet.get_order_items.assert_called()
    mock_scraper.TBScraper().impersonate.assert_called_with(email)
    mock_scraper.TBScraper().add_to_cart.assert_called_with(qty)
    assert expected_msg in result.output
    assert result.exit_code == 0
