#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from time import sleep

import click
from dotenv import load_dotenv
from selenium.common.exceptions import NoSuchWindowException

import artemis_slide_generator.scraper as scraper
import artemis_slide_generator.spreadsheet as spreadsheet

load_dotenv()

MODULE = os.path.splitext(os.path.basename(__file__))[0]


@click.group()
@click.option("-V", "--verbose", is_flag=True, help="enable verbose mode")
@click.option("-D", "--debug", is_flag=True, help="enable debug mode")
def cli(verbose, debug):
    namespace = f"{MODULE}.cli"
    if debug:
        click.echo("Debug mode enabled")
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
        logging.debug(f"{namespace}: Debug mode enabled.")
    elif verbose:
        click.echo("Verbose mode enabled")
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
        logging.info(f"{namespace}: Verbose mode enabled.")
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s")


@cli.command()
@click.argument("vendor")
@click.argument("sheet_id")
@click.argument("sheet_tab")
def scrape(vendor, sheet_id, sheet_tab):
    """
    Scrape Amazon data for vendor from sheet_id/sheet_tab
    """
    namespace = f"{MODULE}.scrape"

    sdb = os.environ["ASG_SCRAPED_DATAFILE"]
    logging.debug(f"{namespace}: Scraped Items Database is: {sdb}")
    logging.debug(f"{namespace}: VENDOR is: {vendor}")
    logging.debug(f"{namespace}: SHEET_ID is: {sheet_id}")
    logging.debug(f"{namespace}: SHEET_TAB is: {sheet_tab}")
    click.echo(f"Running scraper for '{vendor}'")
    click.echo(f"on tab: '{sheet_tab}' of id: '{sheet_id}'")
    click.echo(f"saving to '{sdb}'...")

    scraper_wrapper(vendor, sheet_id, sheet_tab, sdb)


@cli.command()
def download():
    """
    Download scraped images
    """
    namespace = f"{MODULE}.download"

    download_path = os.environ["ASG_SAVED_IMAGES_DIR"]
    logging.debug(f"{namespace}: Download path is: {download_path}")
    click.echo("Running image downloader...")

    img_downloader_wrapper()


@cli.command()
def upload():
    """
    Upload local images to Google Cloud Storage Bucket
    """
    namespace = f"{MODULE}.upload"

    upload_source = os.environ["ASG_UPLOAD_SOURCE"]
    logging.debug(f"{namespace}: Upload source path is: {upload_source}")
    click.echo("Running Google Cloud uploader...")

    gcloud_wrapper()


@cli.command()
@click.option("-t", "--title", default="New Arrivals", help="Slide deck title")
@click.argument("vendor")
@click.argument("sheet_id")
@click.argument("sheet_tab")
def generate(title, vendor, sheet_id, sheet_tab):
    """
    Generate a Google Slide Deck
    """
    namespace = f"{MODULE}.generate"

    sdb = os.environ["ASG_SCRAPED_DATAFILE"]
    logging.debug(f"{namespace}: Scraped Items Database is: {sdb}")
    logging.debug(f"{namespace}: Slide deck title is: {title}")
    logging.debug(f"{namespace}: VENDOR is: {vendor}")
    logging.debug(f"{namespace}: SHEET_ID is: {sheet_id}")
    logging.debug(f"{namespace}: SHEET_TAB is: {sheet_tab}")
    click.echo(f"Running slide generator to create slide deck '{title}' for '{vendor}'")
    click.echo(f"using tab: '{sheet_tab}' of id: '{sheet_id}'...")

    slide_generator_wrapper(vendor, sheet_id, sheet_tab, sdb, title)


@cli.command()
@click.option("--output", "out", default="out.xlsx", help="Output file")
@click.argument("vendor")
@click.argument("workbook")
@click.argument("worksheet")
def sheet_image(out, vendor, workbook, worksheet):
    """
    Insert item thumbnail images into spreadsheet
    """
    namespace = f"{MODULE}.sheet_image"

    image_directory = os.path.join(os.environ["ASG_SAVED_IMAGES_DIR"], "thumbnails")
    logging.debug(f"{namespace}: VENDOR is: {vendor}")
    logging.debug(f"{namespace}: WORKBOOK is: {workbook}")
    logging.debug(f"{namespace}: Worksheet is: {worksheet}")
    logging.debug(f"{namespace}: Thumbnail Image Directory is: {image_directory}")
    msg = (
        f"Running sheet-image on '{workbook}/{worksheet}' for '{vendor}'"
        f"with images from '{image_directory}', saving to '{out}'..."
    )
    click.echo(msg)

    sheet_image_wrapper(vendor, workbook, worksheet, image_directory, out)


@cli.command()
@click.option(
    "--image-directory",
    default=os.environ["ASG_SAVED_IMAGES_DIR"],
    help="Image directory",
)
def mkthumbs(image_directory):
    """
    Create thumbnails of images in IMAGE_DIRECTORY
    """
    namespace = f"{MODULE}.mkthumbs"

    logging.debug(f"{namespace}: Image Directory is: {image_directory}")
    click.echo(f"Running mkthumbs on images in '{image_directory}'...")

    mkthumbs_wrapper(image_directory)


@cli.command()
@click.option("--email", "email", default="", help="TB Customer email to impersonate")
@click.argument("vendor")
@click.argument("workbook")
@click.argument("worksheet")
def order(email, vendor, workbook, worksheet):
    """
    Add items to be ordered to website cart of vendor from spreadsheet
    """
    namespace = f"{MODULE}.order"

    logging.debug(f"{namespace}: VENDOR is: {vendor}")
    logging.debug(f"{namespace}: WORKBOOK is: {workbook}")
    logging.debug(f"{namespace}: Worksheet is: {worksheet}")
    msg = (
        f"Running order on '{workbook}/{worksheet}' for '{vendor}'"
        f"Adding items to cart..."
    )
    click.echo(msg)

    order_wrapper(email, vendor, workbook, worksheet)


cli.add_command(scrape)
cli.add_command(download)
cli.add_command(upload)
cli.add_command(generate)
cli.add_command(sheet_image)
cli.add_command(mkthumbs)


# wrappers to make the cli testable
def slide_generator_wrapper(vendor, sheet_id, sheet_tab, sdb, title):
    import artemis_slide_generator.slide_generator as slide_generator

    slide_generator.main(vendor, sheet_id, sheet_tab, sdb, title)


def gcloud_wrapper():
    import artemis_slide_generator.gcloud as gcloud

    gcloud.main()


def img_downloader_wrapper():
    import artemis_slide_generator.img_downloader as img_downloader

    img_downloader.main()


def scraper_wrapper(vendor, sheet_id, sheet_tab, sdb):
    import artemis_slide_generator.scraper as scraper

    scraper.main(vendor, sheet_id, sheet_tab, sdb)


def sheet_image_wrapper(vendor, workbook, worksheet, image_directory, out):
    spreadsheet.sheet_image(vendor, workbook, worksheet, image_directory, out)


def mkthumbs_wrapper(image_directory):
    spreadsheet.mkthumbs(image_directory)


def order_wrapper(email, vendor, workbook, worksheet):
    order_items = spreadsheet.get_order_items(vendor, workbook, worksheet)
    if vendor == "tb":
        if not email:
            raise Exception(
                f"Vendor '{vendor}' requires the '--email' option to be set."
            )
        driver = scraper.get_driver()
        scrapr = scraper.TBScraper(driver)
    elif vendor == "gj":
        driver = scraper.get_driver()
        scrapr = scraper.GJScraper(driver)
    elif vendor == "sd":
        driver = scraper.get_driver()
        scrapr = scraper.SDScraper(driver)
    else:
        raise Exception(f"Vendor '{vendor}' is not supported by the order command.")

    scrapr.load_login_page()
    scrapr.login()
    if vendor == "tb":
        scrapr.impersonate(email)
    for item, qty in order_items:
        if vendor == "tb":
            item = scrapr.search_item_num(item)
            if not item:
                continue
        res = scrapr.load_item_page(item)
        if res:
            scrapr.add_to_cart(qty)
    scrapr.load_cart_page()
    delay = 600
    print("********    USER INPUT REQUIRED    ********")
    print("Locate the selenium controlled browser")
    print("and manually review and complete your order.")
    print("********  WAITING FOR USER INPUT   ********")
    print()
    print(f"WARNING:  The browser session will terminate in {delay} seconds!!!!")
    print("COUNTING DOWN TIME REMAINING...")
    countdown(delay, driver)


def countdown(delay, driver=None):
    while isBrowserAlive(driver) and delay > 0:
        print(delay, end="\r")
        sleep(1)
        delay -= 1


def isBrowserAlive(driver):
    try:
        driver.current_url
        return True
    except (AttributeError, NoSuchWindowException):
        return False


if __name__ == "__main__":
    cli()
