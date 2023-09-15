import logging
import os
import shutil
from inspect import getsourcefile

import pytest

import artemis_slide_generator.spreadsheet as spreadsheet


@pytest.fixture()
def image_filepath():
    here = os.path.dirname(getsourcefile(lambda: 0))
    resources = os.path.abspath(os.path.join(here, "..", "resources"))
    path = os.path.join(resources, "artemis_logo.png")
    return path


@pytest.fixture()
def spreadsheet_filepath():
    here = os.path.dirname(getsourcefile(lambda: 0))
    resources = os.path.abspath(os.path.join(here, "..", "resources"))
    path = os.path.join(resources, "test_sheet.xlsx")
    return path


@pytest.fixture()
def target_directory(tmp_path_factory):
    path = tmp_path_factory.mktemp("data")
    yield path


@pytest.fixture()
def populated_target_directory(tmp_path_factory, image_filepath):
    path = tmp_path_factory.mktemp("data")
    shutil.copyfile(image_filepath, os.path.join(path, "9781680508604.jpg"))
    shutil.copyfile(image_filepath, os.path.join(path, "9780691025551.jpg"))
    shutil.copyfile(image_filepath, os.path.join(path, "9780691025552.jpg"))
    shutil.copyfile(image_filepath, os.path.join(path, "672125069899.jpg"))
    shutil.copyfile(image_filepath, os.path.join(path, "9999999999990.jpg"))
    shutil.copyfile(image_filepath, os.path.join(path, "9999999999990-1.jpg"))
    shutil.copyfile(image_filepath, os.path.join(path, "FI-1234.jpg"))
    f = open(os.path.join(path, "9999999999999.jpg"), "w")
    f.write("I am not an image file")
    f.close()
    yield path


def test_sheet_image_output_file(
    caplog, spreadsheet_filepath, target_directory, populated_target_directory
):
    """
    GIVEN a spreadsheet
    AND the workbook and worksheet references for the spreadsheet
    AND an output filepath
    WHEN sheet_image is run in debug mode
    THEN a file is saved as the given output file.
    AND log shows images inserted
    """
    caplog.set_level(logging.INFO)
    vendor_code = "sample"
    workbook = spreadsheet_filepath
    worksheet = "Sheet1"
    outfile = os.path.join(target_directory, "sheet_image_output_file.xlsx")
    image = "9780691025551.jpg"
    filepath = os.path.join(populated_target_directory, image)

    spreadsheet.sheet_image(
        vendor_code, workbook, worksheet, populated_target_directory, outfile
    )

    assert os.path.exists(outfile)
    assert (
        "root",
        logging.INFO,
        f"spreadsheet.sheet_image: Inserted '{filepath}'.",
    ) in caplog.record_tuples


def test_sheet_image_isbn_as_floats(
    caplog, spreadsheet_filepath, target_directory, populated_target_directory
):
    """
    GIVEN a spreadsheet containing ISBNs as floating point numbers
    AND the workbook and worksheet references for the spreadsheet
    AND an output filepath
    WHEN sheet_image is run in debug mode
    THEN a file is saved as the given output file.
    AND log ISBN inserted as integer
    """
    caplog.set_level(logging.INFO)
    vendor_code = "sample"
    workbook = spreadsheet_filepath
    worksheet = "Sheet1"
    outfile = os.path.join(target_directory, "sheet_image_output_file.xlsx")
    image = "9780691025552.jpg"
    filepath = os.path.join(populated_target_directory, image)

    spreadsheet.sheet_image(
        vendor_code, workbook, worksheet, populated_target_directory, outfile
    )

    assert os.path.exists(outfile)
    assert (
        "root",
        logging.INFO,
        f"spreadsheet.sheet_image: Inserted '{filepath}'.",
    ) in caplog.record_tuples


def test_mkthumbs_deletes_corrupted_image(populated_target_directory):
    """
    GIVEN a corrupted JPEG file in an image directory
    WHEN mkthumbs is run with the image directory
    THEN mkthumbs should complete without error
    AND the corrupted file should not exist in the image directory
    """
    corrupted_file = "9999999999999.jpg"
    image_directory = str(populated_target_directory)

    spreadsheet.mkthumbs(image_directory)

    assert True
    assert corrupted_file not in os.listdir(image_directory)


def test_mkthumbs_creates_thumbnails(populated_target_directory):
    """
    GIVEN a JPEG file in an image directory
    WHEN mkthumbs is run with the image directory
    THEN thumbnails subdirectory should be created
    AND the JPEG should exist in the subdirectory
    """
    image_file = "9999999999990.jpg"
    image_directory = str(populated_target_directory)
    subdir = "thumbnails"

    spreadsheet.mkthumbs(image_directory)

    assert subdir in os.listdir(image_directory)
    assert image_file in os.listdir(os.path.join(image_directory, subdir))


def test_mkthumbs_doesnt_create_supplementals(populated_target_directory):
    """
    GIVEN a JPEG file in an image directory with a '-1' suffix
    WHEN mkthumbs is run with the image directory
    THEN the JPEG should not exist in the subdirectory
    """
    image_file = "9999999999990-1.jpg"
    image_directory = str(populated_target_directory)
    subdir = "thumbnails"

    spreadsheet.mkthumbs(image_directory)

    assert image_file not in os.listdir(os.path.join(image_directory, subdir))


def test_mkthumbs_creates_invalid_isbn(populated_target_directory):
    """
    GIVEN a JPEG file in an image directory named with an invalid isbn
    WHEN mkthumbs is run with the image directory
    THEN the JPEG should exist in the subdirectory
    """
    image_file = "672125069899.jpg"
    image_directory = str(populated_target_directory)
    subdir = "thumbnails"

    spreadsheet.mkthumbs(image_directory)

    assert image_file in os.listdir(os.path.join(image_directory, subdir))


def test_mkthumbs_creates_item_with_hyphen(populated_target_directory):
    """
    GIVEN a JPEG file in an image directory named with a hyphen ("FI-1234.jpg")
    WHEN mkthumbs is run with the image directory
    THEN the JPEG should exist in the subdirectory
    """
    image_file = "FI-1234.jpg"
    image_directory = str(populated_target_directory)
    subdir = "thumbnails"

    spreadsheet.mkthumbs(image_directory)

    assert image_file in os.listdir(os.path.join(image_directory, subdir))


def test_mkthumbs_ignores_no_basename(tmp_path_factory, image_filepath):
    """
    GIVEN a JPEG file in an image directory named '.jpg'
    WHEN mkthumbs is run with the image directory
    THEN the file should not exist in the subdirectory
    """
    subdir = "thumbnails"
    image_file = ".jpg"
    image_directory = tmp_path_factory.mktemp("test_no_basename")
    shutil.copyfile(image_filepath, os.path.join(image_directory, image_file))

    spreadsheet.mkthumbs(image_directory)

    assert image_file not in os.listdir(os.path.join(image_directory, subdir))


def test_get_order_items(spreadsheet_filepath):
    """
    GIVEN a spreadsheet with "ISBN-13" and "Order" columns
    AND the spreadsheet contains rows with items and quantities
    WHEN get_order_items is run with a vendor_code
    AND the workbook and worksheet references for the spreadsheet
    THEN a list of order items is returned
    """
    expected_list = [
        ("9780300153750", "42"),
        ("9780691025551", "3"),
        ("9780691025552", "3"),
    ]
    vendor_code = "sample"
    workbook = spreadsheet_filepath
    worksheet = "Sheet1"

    order_items = spreadsheet.get_order_items(vendor_code, workbook, worksheet)

    assert isinstance(order_items, list)
    assert order_items == expected_list
