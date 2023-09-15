# -*- coding: utf-8 -*-

import datetime
import logging
import math
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont


class SlideGenerator:
    # constants
    LINE_SPACING = 1
    TEXT_WIDTH = 80
    MAX_FONTSIZE = 18

    SLIDE_MAX_BATCH = 100
    SLIDE_PPI = 96
    SLIDE_W = 10.0
    SLIDE_H = 5.625
    GUTTER = 0.375
    LOGO_H = 1
    LOGO_W = 1
    ADDL_IMG_H = 1.5
    ADDL_IMG_W = 3
    BLACK = {"red": 0.0, "green": 0.0, "blue": 0.0}
    WHITE = {"red": 1.0, "green": 1.0, "blue": 1.0}
    EMU_INCH = 914400
    LOGO_URL = "https://images.squarespace-cdn.com/content/v1/6110970ca45ca157a1e98b76/e4ea0607-01c0-40e0-a7c0-b56563b67bef/artemis.png?format=1500w"  # noqa: E501

    BLACKLIST_KEYS = [
        "IMAGE",
        "ON HAND",
        "ORDER QTY",
        "GJB SUGGESTED",
        "DATE RECEIVED",
        "SUBJECT",
        "QTYINSTOCK",
        "SALESPRICE",
        "AVAILABLE START DATE",
        "CATEGORY",
        "LINK",
    ]

    # methods
    def __init__(self, slides, gcloud, vendor):
        self.slides = slides
        self.gcloud = gcloud
        self.vendor = vendor
        self.slides_api_call_count = 0

    ########################################################################################################
    def gj_binding_map(self, code):
        code = code.upper()
        return {
            "P": "Paperback",
            "H": "Hardcover",
            "C": "Hardcover",
            "C NDJ": "Cloth, no dust jacket",
            "CD": "CD",
        }.get(code, code)

    def gj_type_map(self, code):
        code = code.upper()
        return {"R": "Remainder", "H": "Return"}.get(code, code)

    def get_req_update_artemis_slide(
        self, deckID, bookSlideID, item, text_bucket_prefix, g_reqs
    ):
        namespace = (
            f"{type(self).__name__}.{self.get_req_update_artemis_slide.__name__}"
        )
        image_count = len(item.image_urls)
        main_dim = self.get_main_image_size(image_count)

        logging.info(f"{namespace}: background to black")
        g_reqs += self.get_req_slide_bg_color(bookSlideID, self.BLACK)

        logging.info(f"{namespace}: cover image on book slide")
        cover_url = item.image_urls.pop()
        g_reqs += self.get_req_create_image(
            bookSlideID,
            cover_url,
            main_dim,
            (self.GUTTER, self.GUTTER),
        )

        for i, url in enumerate(item.image_urls):
            if i > 2:
                continue

            logging.info(f"{namespace}: {str(i + 2)} image on book slide")
            g_reqs += self.get_req_create_image(
                bookSlideID,
                url,
                (self.ADDL_IMG_W, self.ADDL_IMG_H),
                (
                    (self.GUTTER + ((self.ADDL_IMG_W + self.GUTTER) * i)),
                    (self.SLIDE_H - self.GUTTER - self.ADDL_IMG_H),
                ),
            )

        logging.info(f"{namespace}: Create text")
        text_box_dim, max_lines = self.get_text_box_size_lines(image_count)
        big_text = self.create_slide_text(item, max_lines)

        logging.info(f"{namespace}: Create text image")
        text_file = self.create_text_image_file(
            item.isbn, text_bucket_prefix, big_text, text_box_dim
        )

        logging.info(f"{namespace}: Upload text image to GC storage")
        blob_name = text_file
        self.gcloud.upload_cloud_blob(text_file, blob_name)
        logging.debug(f"{namespace}: Deleting local text image")
        os.remove(text_file)
        logging.info(f"{namespace}: Create URL for text image")
        url = self.gcloud.generate_cloud_signed_url(blob_name)
        logging.info(f"{namespace}: text image to slide")
        g_reqs += self.get_req_create_image(
            bookSlideID, url, text_box_dim, (self.SLIDE_W / 2, self.GUTTER)
        )

        logging.info(f"{namespace}: ISBN text on book slide")
        text_box_w = self.SLIDE_W
        text_box_h = self.GUTTER  # FIXME: with a better constant
        text_fields = self.create_text_fields_via_batchUpdate(
            deckID,
            self.get_req_create_text_box(
                bookSlideID,
                (self.SLIDE_W - 1.0, self.SLIDE_H - self.GUTTER),
                (text_box_w, text_box_h),
            ),
        )  # FIXME: remove magic number
        textFieldID = text_fields[0]
        text_d = {textFieldID: item.isbn}
        g_reqs += self.get_req_insert_text(text_d)
        g_reqs += self.get_req_text_field_fontsize(textFieldID, 6)
        g_reqs += self.get_req_text_field_color(textFieldID, self.WHITE)

        logging.info(f"{namespace}: logo image on book slide")
        g_reqs += self.get_req_create_logo(bookSlideID)

        return g_reqs

    def create_text_fields_via_batchUpdate(self, deckID, reqs):
        textObjectIdList = []
        rsp = self.slide_batchUpdate(deckID, reqs, True)
        for obj in rsp:
            textObjectIdList.append(obj["createShape"]["objectId"])
        return textObjectIdList

    def create_book_slides_via_batchUpdate(self, deckID, bookList):
        namespace = (
            f"{type(self).__name__}.{self.create_book_slides_via_batchUpdate.__name__}"
        )

        logging.info(f"{namespace}: Create slides for books")
        bookSlideIDList = []
        reqs = []
        for i in range(len(bookList)):
            reqs += [
                {"createSlide": {"slideLayoutReference": {"predefinedLayout": "BLANK"}}}
            ]
        rsp = self.slide_batchUpdate(deckID, reqs, True)
        for i in rsp:
            bookSlideIDList.append(i["createSlide"]["objectId"])
        return bookSlideIDList

    def slide_batchUpdate(self, deckID, reqs, get_replies=False):
        if get_replies:
            return (
                self.slides.presentations()
                .batchUpdate(body={"requests": reqs}, presentationId=deckID)
                .execute()
                .get("replies")
            )
        else:
            return (
                self.slides.presentations()
                .batchUpdate(body={"requests": reqs}, presentationId=deckID)
                .execute()
            )

    def get_req_create_image(self, slideID, url, size, translate):
        w, h = size
        translate_x, translate_y = translate
        reqs = [
            {
                "createImage": {
                    "elementProperties": {
                        "pageObjectId": slideID,
                        "size": {
                            "width": {
                                "magnitude": self.EMU_INCH * w,
                                "unit": "EMU",
                            },
                            "height": {
                                "magnitude": self.EMU_INCH * h,
                                "unit": "EMU",
                            },
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": self.EMU_INCH * translate_x,
                            "translateY": self.EMU_INCH * translate_y,
                            "unit": "EMU",
                        },
                    },
                    "url": url,
                },
            }
        ]
        return reqs

    def get_req_create_logo(self, slideID):
        # Place logo in upper right corner of slide
        translate_x = self.SLIDE_W - self.LOGO_W
        translate_y = 0
        return self.get_req_create_image(
            slideID,
            self.LOGO_URL,
            (self.LOGO_W, self.LOGO_H),
            (translate_x, translate_y),
        )

    def get_req_slide_bg_color(self, slideID, rgb_d):
        reqs = [
            {
                "updatePageProperties": {
                    "objectId": slideID,
                    "fields": "pageBackgroundFill",
                    "pageProperties": {
                        "pageBackgroundFill": {
                            "solidFill": {
                                "color": {
                                    "rgbColor": rgb_d,
                                }
                            }
                        }
                    },
                },
            },
        ]
        return reqs

    def get_req_text_field_color(self, fieldID, rgb_d):
        reqs = [
            {
                "updateTextStyle": {
                    "objectId": fieldID,
                    "textRange": {"type": "ALL"},
                    "style": {
                        "foregroundColor": {
                            "opaqueColor": {
                                "rgbColor": rgb_d,
                            }
                        }
                    },
                    "fields": "foregroundColor",
                }
            }
        ]
        return reqs

    def get_req_text_field_fontsize(self, fieldID, pt_size):
        reqs = [
            {
                "updateTextStyle": {
                    "objectId": fieldID,
                    "textRange": {"type": "ALL"},
                    "style": {
                        "fontSize": {
                            "magnitude": pt_size,
                            "unit": "PT",
                        }
                    },
                    "fields": "fontSize",
                }
            },
        ]
        return reqs

    def get_req_insert_text(self, textDict):
        reqs = []
        for key in textDict.keys():
            reqs.append(
                {
                    "insertText": {
                        "objectId": key,
                        "text": textDict[key],
                    },
                }
            )
        return reqs

    def get_req_create_text_box(self, slideID, coord=(0, 0), field_size=(1, 1)):
        reqs = [
            {
                "createShape": {
                    "elementProperties": {
                        "pageObjectId": slideID,
                        "size": {
                            "width": {
                                "magnitude": self.EMU_INCH * field_size[0],
                                "unit": "EMU",
                            },
                            "height": {
                                "magnitude": self.EMU_INCH * field_size[1],
                                "unit": "EMU",
                            },
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": self.EMU_INCH * coord[0],
                            "translateY": self.EMU_INCH * coord[1],
                            "unit": "EMU",
                        },
                    },
                    "shapeType": "TEXT_BOX",
                },
            }
        ]
        return reqs

    def create_slide_text(self, item, max_lines):
        namespace = f"{type(self).__name__}.{self.create_slide_text.__name__}"

        big_text = ""
        logging.debug(f"{namespace}: Item.data: {item.data}")
        for key in item.data:
            key = key.strip().upper()
            if key in self.BLACKLIST_KEYS:
                continue
            t = item.data[key]
            if key == "AUTHOR":
                t = "by " + t
            if key in ["PUB LIST", "LISTPRICE"]:
                t = "List price: " + t
            if key in ["NET COST", "YOUR NET PRICE"]:
                t = "Your net price: " + t
            if key in ["PUB DATE", "PUBLISHERDATE"]:
                t = "Pub Date: " + t
            if key == "BINDING":
                t = "Format: " + self.gj_binding_map(t)
            if key == "FORMAT":
                t = "Format: " + t
            if key == "TYPE":
                t = "Type: " + self.gj_type_map(t)
            if key == "PAGES":
                t = "Pages: " + t + " pp."
            if key == "SIZE":
                t = "Size: " + t
            if key in ["ITEM#", "TBCODE"]:
                t = "Item #: " + t
            if key == item.isbn_key:
                t = "ISBN: " + t
            line_count = big_text.count("\n")
            t = textwrap.fill(
                t, width=self.TEXT_WIDTH, max_lines=max_lines - line_count
            )
            t = t + "\n\n"
            big_text += t
        return big_text

    def create_text_image_file(self, isbn, text_bucket_prefix, text, size):
        namespace = f"{type(self).__name__}.{self.create_text_image_file.__name__}"

        w, h = size
        if os.name == "posix":
            typeface = "LiberationSans-Regular.ttf"
        else:
            typeface = "arial.ttf"

        image = Image.new(
            "RGB",
            (int(w * self.SLIDE_PPI), int(h * self.SLIDE_PPI)),
            (0, 0, 0),
        )

        fontsize = 1
        font = ImageFont.truetype(typeface, fontsize)
        draw = ImageDraw.Draw(image)

        # dynamically size text to fit box
        while (
            draw.multiline_textbbox(
                xy=(0, 0), text=text, font=font, spacing=self.LINE_SPACING
            )[2]
            < image.size[0]
            and draw.multiline_textbbox(
                xy=(0, 0), text=text, font=font, spacing=self.LINE_SPACING
            )[3]
            < image.size[1]
            and fontsize < self.MAX_FONTSIZE
        ):
            fontsize += 1
            font = ImageFont.truetype(typeface, fontsize)

        fontsize -= 1
        logging.info(f"{namespace}: Font size is '{fontsize}'")
        font = ImageFont.truetype(typeface, fontsize)

        # center text
        _delme1, _delme2, t_w, t_h = draw.multiline_textbbox(
            xy=(0, 0), text=text, font=font, spacing=self.LINE_SPACING
        )
        y_offset = math.floor((image.size[1] - t_h) / 2)

        draw.multiline_text(
            (0, y_offset), text, font=font, spacing=self.LINE_SPACING
        )  # put the text on the image
        text_file = "%s_text.png" % isbn
        text_file = os.path.join(text_bucket_prefix, text_file)
        image.save(text_file)
        return text_file

    ########################################################################################################
    def generate(self, items, bucket_prefix, deck_title=None):
        namespace = f"{type(self).__name__}.{self.generate.__name__}"
        # hack a text_bucket_prefix value
        text_bucket_prefix = bucket_prefix.replace("images", "text")
        if text_bucket_prefix == bucket_prefix:
            text_bucket_prefix = bucket_prefix + "_text"
        if not os.path.isdir(text_bucket_prefix):
            os.mkdir(text_bucket_prefix)

        logging.info(f"{namespace}: Create new slide deck")
        title = "%s Artemis Slides %s" % (
            self.vendor.vendor_name,
            datetime.datetime.now(),
        )
        DATA = {"title": title}
        rsp = self.slides.presentations().create(body=DATA).execute()
        self.slides_api_call_count += 1
        deckID = rsp["presentationId"]

        titleSlide = rsp["slides"][0]
        titleSlideID = titleSlide["objectId"]
        titleID = titleSlide["pageElements"][0]["objectId"]
        subtitleID = titleSlide["pageElements"][1]["objectId"]

        reqs = []
        logging.info(f"{namespace}: req Insert slide deck title+subtitle")
        subtitle = self.vendor.vendor_name
        if deck_title:
            subtitle = "%s, %s" % (subtitle, deck_title)
        titleCardText = {
            titleID: "Artemis Book Sales Presents...",
            subtitleID: subtitle,
        }
        reqs += self.get_req_insert_text(titleCardText)
        reqs += self.get_req_text_field_fontsize(titleID, 40)
        reqs += self.get_req_text_field_color(titleID, self.WHITE)
        reqs += self.get_req_text_field_color(subtitleID, self.WHITE)
        reqs += self.get_req_slide_bg_color(titleSlideID, self.BLACK)
        reqs += self.get_req_create_logo(titleSlideID)

        # find images and delete books entries without images
        blob_names = self.gcloud.list_image_blobs(bucket_prefix)
        for item in items:
            if not item.isbn:
                if "TBCODE" in item.data.keys():
                    item.isbn = item.data["TBCODE"]
            # pp.pprint(item.data)
            # exit()
            imageList = [blob for blob in blob_names if item.isbn in blob]
            # sort image list
            sl = sorted(imageList)
            # generate URLs for book images on google cloud storage
            url_list = []
            for name in sl:
                url = self.gcloud.generate_cloud_signed_url(name)
                url_list.append(url)

            item.image_urls = url_list

        # update title slide
        self.slide_batchUpdate(deckID, reqs)
        # clear reqs
        reqs = []
        # create book slides
        items_with_images = items.get_items_with_image_urls()
        bookSlideIDList = self.create_book_slides_via_batchUpdate(
            deckID, items_with_images
        )

        e_books = list(zip(bookSlideIDList, items_with_images))
        batches = math.ceil(len(e_books) / self.SLIDE_MAX_BATCH)
        upper_index = len(e_books)
        offset = 0
        for b in range(batches):
            upper = offset + self.SLIDE_MAX_BATCH
            if upper > upper_index:
                upper = upper_index
            for bookSlideID, book in e_books[offset:upper]:
                reqs = self.get_req_update_artemis_slide(
                    deckID, bookSlideID, book, text_bucket_prefix, reqs
                )
            logging.info(f"{namespace}: Execute img/text update reqs")
            # pp.pprint(reqs)
            # exit()
            self.slide_batchUpdate(deckID, reqs)
            reqs = []
            offset = offset + self.SLIDE_MAX_BATCH

        logging.info(f"{namespace}: Slide deck completed")
        logging.info(f"{namespace}: API call counts")
        logging.info("    SLIDES: %r" % self.slides_api_call_count)
        # logging.info("    SHEETS: %r" % sheets_api_call_count)
        # logging.info("     CLOUD: %r" % cloud_api_call_count)
        link = f"https://docs.google.com/presentation/d/{deckID}"
        logging.info(f"{namespace}: Slide deck link: {link}")
        return link

    def get_main_image_size(self, image_count):
        w = (self.SLIDE_W / 2) - (self.GUTTER * 2)
        h = self.SLIDE_H - (self.GUTTER * 2)
        if image_count > 1:
            h = self.SLIDE_H - (self.GUTTER * 3) - (self.ADDL_IMG_H)
        return (w, h)

    def get_text_box_size_lines(self, image_count):
        w = (self.SLIDE_W / 2) - (self.GUTTER * 2)
        h = self.SLIDE_H - (self.GUTTER * 2)
        max_lines = 36
        if image_count > 2:
            h = self.SLIDE_H - (self.GUTTER * 2) - (self.ADDL_IMG_H)
            max_lines = 28
        return (w, h), max_lines

    ########################################################################################################


def main(vendor_code, sheet_id, sheet_tab, scraped_items_db, title):
    from googleapiclient.discovery import build

    from artemis_slide_generator.app_creds import app_creds
    from artemis_slide_generator.gcloud import GCloud
    from artemis_slide_generator.items import Items
    from artemis_slide_generator.vendor import Vendor

    # vendor object
    vendr = Vendor(vendor_code)
    vendr.set_vendor_data()

    # Slides API object
    creds = app_creds()
    SLIDES = build("slides", "v1", credentials=creds)

    # GCloud object
    bucket_name = os.environ["GOOGLE_CLOUD_BUCKET"]
    cloud_key_file = os.environ["GOOGLE_CLOUD_KEY_FILE"]
    gcloud = GCloud(cloud_key_file=cloud_key_file, bucket_name=bucket_name)

    # Items dataset
    SHEETS = build("sheets", "v4", credentials=creds)
    sheet_data = (
        SHEETS.spreadsheets()
        .values()
        .get(range=sheet_tab, spreadsheetId=sheet_id)
        .execute()
        .get("values")
    )
    sheet_keys = sheet_data.pop(0)
    items_obj = Items(sheet_keys, sheet_data, vendr.isbn_key)
    items_obj.load_scraped_data(scraped_items_db)

    sg = SlideGenerator(SLIDES, gcloud, vendr)

    bucket_prefix = os.environ["GOOGLE_CLOUD_BUCKET_PREFIX"]
    slide_deck = sg.generate(items_obj, bucket_prefix, title)
    print(f"Slide deck: {slide_deck}")
