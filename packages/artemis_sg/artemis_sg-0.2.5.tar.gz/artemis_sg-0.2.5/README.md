![logo](resources/artemis_logo.png)

Table of contents
=================

* [What does this do?](#what-does-this-do)
* [Installation](#installation)
  * [Tool setup](#tool-setup)
* [How do I run it?](#how-do-i-run-it)
  * [Session setup](#session-setup)
  * [Slide Generator Workflow](#slide-generator-workflow)
  * [Spreadsheet Images Workflow](#spreadsheet-images-workflow)
* [CLI Command Reference](#cli-command-reference)
* [Testing](#testing)


# What does this do
This is a python application to generate Google Slide decks using Google
Sheets for the data source.  It is specifically tailored for the item data
maintained by Artemis Book Sales.

Given a Google Sheet with the appropriate data, this application will create
a Google Slide deck containing a title slide and one slide per item with
the appropriate image and text data formatted on each slide.

# Installation
You need [Python](https://python.org/downloads) 3.7 or greater and the
[pip package management tool](https://pip.pypa.io/en/stable/installation)
installed.  These instructions also assume you have [Git](https://git-scm.com)
installed for source code management.

## Clone Repo
```shell
cd desired/development/location
git clone https://gitlab.com/johnduarte/artemis_slide_generator.git
cd artemis_slide_generator
```

## Setup Python environment
Create a python virtual environment named `pyvenv` at the root of the
repository checkout and then activate it.  With the environment activated,
install the package to enable the CLI.

On Windows, open the Command shell or PowerShell
and execute the following commands to set up the
virtual environment.

In Windows Command Shell:
```cmd
cd Development\Location\artemis_slide_generator
python3 -m venv .\pyvenv
pyvenv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install --editable .
```

In Windows PowerShell:
```cmd
cd Development\Location\artemis_slide_generator
python3 -m venv .\pyvenv
.\pyvenv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install --editable .
```

On \*Nix, open the shell of your choice (the commands below use bash) and
execute the following commands to set up the virtual environment.
```bash
cd development/location/artemis_slide_generator
python3 -m venv ./pyvenv
source pyvenv/bin/activate
python -m pip install --upgrade pip
pip install --editable .
```

### Setup PowerShell activation script
Assumptions:
* Python is installed
* PowerShell is installed


#### Enable Local Scripts
PowerShell execution policy needs to be updated in order to add scripts to be
run.  We will set the policy to allow locally created scripts but deny
execution for scripts downloaded from the internet.

See [Microsoft PowerShell Exectution Policies]( https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies?view=powershell-7.2).

```powershell
PS> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

#### Ensure Profile
See if a PowerShell profile is defined:
```powershell
PS> $profile
```

The above will return `false` or a file path.  `false` means the profile is not
defined.  If a file path is returned it may not exist yet.  Check to see if the
profile path exists.
```powershell
PS> type $profile
```

If the above returns a `type: cannot find path '<PATH>' because it does not
exist` error, then the profile file does not exist.

*Only if* the profile is not defined or the profile file does not exist, Create
the file.
```powershell
PS> ni -Force $profile
```

#### Create Profile content
Find the full path to your `artemis_slide_generator` python virtual
environment.

Open the profile file in notepad
```powershell
PS> notepad $profile
```

Add the following content to your profile
```powershell
# Microsoft.PowerShell_profile.ps1

Set-Alias python-sys  $(python -c 'import sys; print(sys.executable)')

function activate-artemis-pyvenv {
& 'C:\Path\to\artemis_slide_generator\pyvenv\Scripts\Activate.ps1'
}
```

Restart your PowerShell session to load the updated profile.

#### Activate the artemis Python Virtual Environment
```powershell
activate-artemis-pyvenv
```


## Google API
The Google API client library for Python is required.
See the
[Google Slides API Quickstart](https://developers.google.com/slides/api/quickstart/python)
for instructions on setting up API authorization.

***Important:***
The setup above will produce a `credentials.json` file needed to authenticate
to the Google Slides and Sheet API.  You will need to copy/move it to the
root of the repository checkout prior to running any commands.

* Save the `credentials.json` file to the project directory.
* Modify the file permissions on the token to make it READ-ONLY.

## Google Cloud
Using Google Cloud Storage requires a private service account key as an
authentication mechanism.
Signed URLs will be generated to put the images into the slides.  This
requires a service account and service account key file.

### Enable Google Cloud Storage API
* In the Google Cloud account dashboard, click 'APIs & Services' from the
  navigation menu.
* Click '+ ENABLE APIS AND SERVICES'
* Search for 'cloud storage'
* Enable Google Cloud Storage JSON API
* Enable Google Cloud Storage

### Create Service Account
* In the Google Cloud account dashboard, select 'APIs & Services' from the
  navigation menu.  Then click 'Credentials' in the sub-menu.
* Click '+ CREATE CREDENTIALS'
* Choose 'Service Account' from the drop-down menu.
* Name the account and click 'Create'.
* Choose 'Owner' from the 'Basic' roll in the 'Grant access' section.
* Click 'Continue'
* Click 'Done'

### Create Service Account Key
* Open the service account from the Credentials list in the Google Cloud
  account.
* Click 'KEYS'
* Click 'ADD KEY'
* Click 'CREATE NEW KEY'
* Choose JSON format
* Click 'CREATE'
* Save the key to the project directory.
* Modify the file permissions on the key to make it READ-ONLY.

***Important:***
The application will not work as expected unless the Google
Cloud key is present in the root of the repository checkout.

### Development Note: Authentication from within python
Ensure that your python venv environment is setup and that the
google-cloud-storage library is installed.  Also,
ensure that the Google Cloud service account key is stored in
the project directory.

Putting the following lines in a python file will authenticate
to Google Cloud Storage.
```python
import os
from google.cloud import storage

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '<NAME-OF-KEY-FILE>'
client = storage.Client()
```

Refs:
* [YouTube tutorial](https://www.youtube.com/watch?v=pEbL_TT9cHg)
* [Google Cloud Getting Started with Python](https://cloud.google.com/python/docs/getting-started)
* [google-cloud-storage-client-library-python](https://cloud.google.com/python/docs/reference/storage/latest)

## Create .env for needed environment variables
The `.env.example` file contains all of the environment variables
needed by the application.  In order for the application to see them
it needs to be copied to `.env`.

Copy the provided `.env.example` to `.env` in the root of the repository
checkout.

You then need to update the values as necessary to work for your situation.
The values supplied are as follows:
```
ASG_UPLOAD_SOURCE=downloaded_images
GOOGLE_CLOUD_BUCKET=my_bucket
GOOGLE_CLOUD_BUCKET_PREFIX=my_bucket_prefix
GOOGLE_CLOUD_KEY_FILE=my_cloud_key.json
ASG_SCRAPED_DATAFILE=scraped_items.json
ASG_SAVED_IMAGES_DIR=downloaded_images
ASG_VENDOR_DATAFILE=vendors.json
# For pytest integration testing
ASG_TEST_SHEET_ID="GOOGLE_SHEET_ID_HERE"
ASG_TEST_SHEET_TAB="GOOGLE_SHEET_TAB_HERE"
```

The environment variables starting with "GOOGLE_CLOUD_" must be changed to
reflect the Google Cloud bucket, prefix, and key file  associated with the
Google Cloud Storage API service account key.  The environment variables
starting with "ASG_" can be left as they are.  However, if you prefer other
names for these, you may change them.

## Final Setup Checklist
Once you have completed all of the above setup [steps](#clone-repo), run
through the following checklist to make sure you are ready to proceed.

* Google API `credentials.json` is located at root of checkout.
* Google Cloud Service key is located at root of checkout.
 `.env` has been updated with valid values for the following:
    * `GOOGLE_CLOUD_BUCKET` - This should be set to a valid cloud bucket.
    * `GOOGLE_CLOUD_BUCKET_PREFIX` - This should be set to a valid cloud bucket prefix.
    * `GOOGLE_CLOUD_KEY_FILE` - This should be set to the name of your Service key file.
* `artemis_sg --help` - results in usage text showing the defined subcommands.

# How do I run it
For each work session, you will need to activate the python virtual environment
prior to executing any commands.  Once the environment is activated, you can
execute the [Slide Generator Workflow](#slide-generator-workflow) as outlined
below or run any of the commands independently as needed.

## Session Setup
Session setup comprises the following steps:

* Change directories to the root of the artemis_slide_generator repository
  checkout.
* Activate the previously created python virtual environment.
* Pull the latest changes with Git.
* Install the new version with pip.

On Windows, open the Command shell or PowerShell (the commands below use
the Command shell) and execute the following commands to set up the
session.

In Windows Command Shell:
```cmd
cd Development\Location\artemis_slide_generator
pyvenv\Scripts\activate.bat
git pull
pip install --editable .
```

In Windows PowerShell:
```powershell
cd Development\Location\artemis_slide_generator
.\pyvenv\Scripts\Activate.ps1
git pull
pip install --editable .
```

On \*Nix, open the shell of your choice (the commands below use bash) and
execute the following commands to set up the session.
```bash
cd development/location/artemis_slide_generator
source pyvenv/bin/activate
git pull
pip install --editable .
```

## Slide Generator Workflow
In order to produce a slide deck, the following workflow is prescribed.
These elements are broken into separate components so that they might be
executed without a defined pipeline if needed.

The package includes a set of subcommands under the unified CLI command
`artemis_sg` once it is installed to facilitate this workflow.  See
the complete [CLI Command Reference](#cli-command-reference) for more
detail on each of these commands.

Steps in the workflow that are a manual task not handled by the software
are highlighted with the *Manual* tag.

* [Create Spreadsheet](#create-spreadsheet) (*Manual*)
* [Upload Spreadsheet to Google Drive](#upload-spreadsheet-to-google-drive) (*Manual*)
* [Convert Spreadsheet to Google Sheet](#convert-spreadsheet-to-google-sheet) (*Manual*)
* [Add/Update Vendor](#add/update-vendor) (*Manual*)
* [Scrape Data](#scrape-data)
* [Download Images](#download-images)
* [Upload Images to Google Cloud](#upload-images-to-google-cloud)
* [Generate Slide Deck](#generate-slide-deck)

### Create Spreadsheet
*Manual*

Create spreadsheet that includes the field titles in row 1 and the desired
slide records in subsequent rows.  The spreadsheet must include a column for
ISBN numbers.  The ISBN numbers are assumed to be in the
[ISBN-13 format](https://www.isbn.org/about_ISBN_standard).  Make a
note of the location of this spreadsheet in your file system and the name of
the worksheet used.  You may want to use this information in the
[spreadsheet images workflow](#spreadsheet-images-workflow).

### Upload Spreadsheet to Google Drive
*Manual*

Upload the spreadsheet to Google Drive using a web browser to access the Google
Drive interface.

* Navigate to: https://drive.google.com/drive/my-drive .
* Click the '+ New' button.
* Select the 'File upload' menu item.
* Select your spreadsheet in the file selector window and click 'Open'.

The spreadsheet will be uploaded to the root of your Google Drive.

### Convert Spreadsheet to Google Drive
*Manual*

Convert the spreadsheet to a Google Sheets document using a web browser to
access the Google Drive interface.

* Navigate to: https://drive.google.com/drive/my-drive .
* Select and open the spreadsheet you uploaded [above](#upload-spreadsheet-to-google-drive).
* Click the 'File' menu.
* Select 'Save as Google Sheets' from the menu.

A Google Sheets document will be created and opened in a new tab.  This
document will also be saved to the root of your Google Drive.  Feel free to
move the Google Sheets and/or the uploaded spreadsheet document wherever you
like in your Google Drive file system.  We will only be referencing them by ID
going forward.

Make a note of the google ID for the Google Sheets document as well as the name
of sheet used for the data.  The ID can be found in the URI for the document.
The ID occurs between the `/d/` and the `/edit` segments of the URI.  Here is
an example URI for reference.

```
https://docs.google.com/spreadsheets/d/MY_GOOGLE_SHEET_ID_IS_HERE/edit#gid=267687802
```

The name of the sheet used for the data within the document is shown toward the
lower right corner when working in the Google Sheet document.  By default, it is
usually named "Sheet1".

### Add/Update Vendor
*Manual*

If this is your first time using this application, copy the
`vendors.json.template` to `vendors.json`.  This will provide you with
the format for the database.

On \*Nix
```bash
cp vendors.json.template vendors.json
```

On Windows
```cmd
copy vendors.json.template vendors.json
```

Open `vendors.json` in your favorite text editor.  If there is not an existing
record for the vendor, add one with the following pattern, including the field
key used for ISBN numbers.

If there is an existing record, update the spreadsheet id and sheet name.

The format is as follows:
```json
{
  "sample_vendor": {
    "name": "Sample Vendor",
    "isbn_key": "ISBN-13"
  }
}
```

### Scrape Data
Run the `artemis_sg scrape` command to save the item descriptions and image
URLs for each record in the spreadsheet to the file defined by the
environment variable `ASG_SCRAPED_DATAFILE`.  The command requires a valid
vendor code argument to map to the applicable vendor record updated in the file
referenced by the `ASG_VENDOR_DATAFILE` in the
[workflow step above](#add/update-vendor).  The command also requires a valid
Google Sheet ID and the name of the Google Sheet tab in which the item data
resides.

Example:
```shell
artemis_sg --verbose scrape sample_vendor MY_GOOGLE_SHEET_ID MY_GOOGLE_SHEET_TAB
```

### Download Images
Download images from the scraped data using the `artemis_sg download` command.

Example:
```shell
artemis_sg --verbose download
```

### Upload Images to Google Cloud
Run the `artemis_sg upload` command to upload previously download images to
Google Cloud.

Example:
```shell
artemis_sg --verbose upload
```

### Generate Slide Deck
Run the `artemis_sg generate` command to create a Google Slide deck of the
items in the spreadsheet including the description and images gathered by the
[scrape workflow step](#scrape-data).  You should set a desired slide title
using the `--title` flag.  The command requires a valid vendor code, a valid
Google Sheet ID, and the name of the Google Sheet tab in which the item data
resides.

Example:
```shell
artemis_sg generate --title "Badass presentation" sample_vendor MY_GOOGLE_SHEET_ID MY_GOOGLE_SHEET_TAB
```

## Spreadsheet Images Workflow
In order to produce a spreadsheet with thumbnail images added for items, the
following workflow is suggested.

The following steps are shared with the
[slide generator workflow](#slide-generator-workflow).  These steps are linked
 to the appropriate step in that workflow rather then duplicating them here.

* [Create Spreadsheet](#create-spreadsheet) (*Manual*)
* [Upload Spreadsheet to Google Drive](#upload-spreadsheet-to-google-drive) (*Manual*)
* [Convert Spreadsheet to Google Sheet](#convert-spreadsheet-to-google-sheet) (*Manual*)
* [Add/Update Vendor](#add/update-vendor) (*Manual*)
* [Scrape Data](#scrape-data)
* [Download Images](#download-images)

The unique steps for this workflow are:

* [Create Thumbnails](#create-thumbnails)
* [Add Thumbnails to Spreadsheet](#add-thumbnails-to-spreadsheet)

### Create Thumbnails
Create thumbnail images from previously downloaded images using the `artemis_sg
mkthumbs` command.

Example:
```shell
artemis_sg --verbose mkthumbs
```

### Add Thumbnails to Spreadsheet
Create a new Excel spreadsheet containing thumbnail images column and populated
with available thumbnails using the `artemis_sg sheet-image` command.  You will
need to supply a vendor code.  You will also
need to supply the local path to the spreadsheet file as well as the name of
the worksheet that the data is located in.  This information can be noted from
the [Create Spreadsheet](#create-spreadsheet) step.

By default, the new Excel file is saved as "out.xlsx" in the directory from
which the command was run (typically the root of the repository checkout).  The
`--output` option can be used to specify a desired output file.  The
specification for the `--output` file can include either an absolute or
relative path location for the file as well.

Example:
```cmd
artemis_sg --verbose sheet-image sample_vendor "C:\Users\john\Documents\spreadsheets\my_spreadsheet.xlsx" "Products"
```

Example, specifying output file with an absolute file path:
```cmd
artemis_sg sheet-image ^
--output "C:\Users\john\Documents\spreadsheets\my_new_spreadsheet.xlsx" ^
sample_vendor ^
"C:\Users\john\Documents\spreadsheets\my_spreadsheet.xlsx" ^
"Products"
```

Example, specifying output file with a relative file path:
```cmd
artemis_sg sheet-image ^
--output "..\..\my_new_spreadsheet.xlsx" ^
sample_vendor ^
"C:\Users\john\Documents\spreadsheets\my_spreadsheet.xlsx" ^
"Products"
```

# CLI Command Reference
The Artemis Slide Generator consists of a single `artemis_sg` command with
many subcommands.

Artemis_sg usage: `artemis_sg [OPTIONS] COMMAND [ARGS]...`

The `artemis_sg` command provides optional `--verbose` and `--debug` options
to increase the level of feedback provided during execution.

A `--help` option is available to display command usage and available subcommands.
```
artemis_sg --help
```

All `artemis_sg` subcommands also provide a `--help` option to display usage
for the given subcommand.

Example:
```
artemis_sg scrape --help
```

## Artemis_sg scrape
The `artemis_sg scrape` command iterates over the item rows in the spreadsheet
provided by the `SHEET_ID` and `SHEET_TAB` arguments.  For each ISBN, it
searches for item descriptions and images in a web browser.  It collects this
information and stores it in the file defined by the environment variable
`ASG_SCRAPED_DATAFILE`.  If data for an ISBN already exists in the datafile,
the ISBN is skipped and does not result in re-scraping data for that record.

Artemis_sg scrape usage: `artemis_sg scrape [OPTIONS] VENDOR SHEET_ID SHEET_TAB`

The command requires a `VENDOR` argument be passed to it.  This argument is a
vendor key that should match a vendor key in the datafile referenced by the
environement variable `ASG_VENDOR_DATAFILE`.  This key is used to look up the
vendor record in the `ASG_VENDOR_DATAFILE` to find the appropriate ISBN_key
associated with the vendor's data in their spreadsheets.

The command also requires `SHEET_ID` and `SHEET_TAB` arguments.  These
reference the Google Sheet ID and workbook within it to access the item rows on
which to conduct its work.

The command utilizes environment variables stored in `.env` to set the vendor
database from `ASG_VENDOR_DATAFILE` and scraped items database from
`ASG_SCRAPED_DATAFILE`.

## Artemis_sg download
The `artemis_sg download` command iterates over the data records in
the file defined by the environment variable `ASG_SCRAPED_DATAFILE`.  For
each record, it downloads the image files associated with the record to a
local directory as defined by the environment variable `ASG_SAVED_IMAGES_DIR`.

Artemis_sg download usage: `artemis_sg download [OPTIONS]`

The command takes no arguments.  Other then `--help`, no additional options
are available.

## Artemis_sg upload
The `artemis_sg upload` command uploads the files in the directory defined by
the environment variable `ASG_UPLOAD_SOURCE` to the Google Cloud bucket defined
by the environment variable `GOOGLE_CLOUD_BUCKET`.  Only the first level of the
source directory is uploaded.  Subdirectories of the source directory are not
traversed for the upload.  All uploaded files are prefixed with value defined
by the environment variable `GOOGLE_CLOUD_BUCKET_PREFIX`.

Artemis_sg upload usage: `artemis_sg upload [OPTIONS]`

The command takes no arguments.  Other then `--help`, no additional options
are available.

## Artemis_sg generate
The `artemis_sg generate` command generates a Google Slides document.

The slide deck will be given a title based on the values supplied for `VENDOR`
and `--title`.  The title slide will be in the following format:
```
Artemis Book Sales Presents...
Vendor Name, Title
```

The `artemis_sg generate` command then iterates over the item rows in the
spreadsheet/tab provided as SHEET_ID and SHEET_TAB arguments.  For each row in
the spreadsheet for which it has image data it creates a slide containing the
spreadsheet data, the description saved in the file defined by the environment
variable `ASG_SCRAPED_DATAFILE`, and the images saved in the
`GOOGLE_CLOUD_BUCKET`.  The Google sheet will be saved to the root of the
Google Drive associated with the credentials created during initial
installation.

Artemis_sg generate usage: `artemis_sg generate [OPTIONS] VENDOR SHEET_ID SHEET_TAB`

The command requires a `VENDOR` argument be passed to it.  This argument is a
vendor key that should match a key in the datafile referenced by the
environment variable `ASG_VENDOR_DATAFILE`.  This key is used to look up the
vendor record in the `ASG_VENDOR_DATAFILE` to find the appropriate ISBN_key
associated with the vendor's data as well as the vendor's name.

The command requires a `SHEET_ID` argument to be passed to it.  This argument
is Google Sheet ID whose ISBN column label matches that of the vendor's
ISBN_key.

The command requires a `SHEET_TAB` argument to be passed to it.  This argument
is the  workbook tab label in the given `SHEET_ID` that contains the data that
the command should access to conduct its work.

The command utilizes environment variables stored in `.env` to set the vendor
database from `ASG_VENDOR_DATAFILE` and scraped items database from
`ASG_SCRAPED_DATAFILE`.

### Options
The command provides optional options for overriding default
values used during execution.

* `-t` or `--title`: Sets the slide deck title used on the first slide in
  the deck.  This option *should* normally be set to prevent the default
  value of "New Arrivals" from being used.

## Artemis_sg mkthumbs
The `artemis_sg mkthumbs` command creates thumbnail images from images located
in a given directory.  These thumbnail images are saved to a `thumbnails`
subdirectory in the original image directory.  These files are given the same
names as their originals.  By default, the command will use the directory
defined by the environment variable `ASG_SAVED_IMAGE_DIR`.  All thumbnails are
130 pixels x 130 pixels in size.

For example, given the default value of `downloaded_images` for
`ASG_SAVED_IMAGE_DIR` with a single image in it, running the command would
result in the following layout.
```
downloaded_images/
├── 9780228101208.jpg
└── thumbnails
    └── 9780228101208.jpg
```

Artemis_sg mkthumbs usage: `artemis_sg mkthumbs [OPTIONS]`

### Options
The command provides optional options for overriding default
values used during execution.

* `--image-directory`: An alternate image directory to use for generating
  thumbnails should you wish to use it on a set of images other than those in
  the `ASG_SAVED_IMAGE_DIR`.

## Artemis_sg sheet-image
The `artemis_sg sheet-image` command modifies a local Excel spreadsheet file to
include thumbnail images in the second column for items in which local
thumbnail image files are available and saves it as a new file.  By default,
the thumbnail images are assumed to be in `$ASG_SAVED_IMAGE_DIR/thumbails`.  By
default, the new Excel file is saved as `out.xlsx`.

Artemis_sg sheet-image usage: `artemis_sg sheet-image [OPTIONS] VENDOR WORKBOOK WORKSHEET`

The command takes required `VENDOR`, `WORKBOOK`, and `WORKSHEET` arguments in
that order.  The `VENDOR` is needed to look up the proper ISBN field name.
The `WORKBOOK` argument is the path to the Excel spreadsheet document to which
you want to add images.  The `WORKSHEET` argument is the name of the worksheet
within the Excel `WORKBOOK` file which contains the data to which you want to
add images.

### Options
The command provides optional options for overriding default
values used during execution.

* `--output FILE`: Write the modified Excel file to a specified output file
  instead of the default `out.xlsx`.

Example:
```
artemis_sg --debug sheet-image --output Spreadsheet_with_images.xlsx sample_vendor Test_Spreadsheet.xlsx "To Slides"
```

## Artemis_sg order
The `artemis_sg order` command populates the website cart for a given vendor
with items from a local Excel spreadsheet file.  The browser instance with the
populated cart is left open for the user to review and manually complete the
order.  The user will be asked to manually login during the execution of this
command.

Artemis_sg sheet-image usage: `artemis_sg order [OPTIONS] VENDOR WORKBOOK WORKSHEET`

The command takes required `VENDOR`, `WORKBOOK`, and `WORKSHEET` arguments in
that order.  The `VENDOR` is needed to invoke the proper website for adding
items to, as well as to look up the proper ISBN field name from the
spreadsheet.  The `WORKBOOK` argument is the path to the Excel spreadsheet
document in which the items to be ordered are located.  The `WORKSHEET`
argument is the name of the worksheet within the Excel `WORKBOOK` file which
contains the order data.

### Options
The command provides optional options for overriding default
values used during execution.

* `--email EMAIL`: Use the provided email to impersonate a TB customer.

Example:
```
artemis_sg order --email foo@example.org sample_vendor Spreadsheet.xlsx Sheet1
```

**NOTE:** The `WORKBOOK` is expected to contain a column named `Order` which
contains the quantity of the items to add to the cart.

**NOTE:** The browser opened by this command is controlled by this command.
The browser will automatically close and the session will be terminated at the
end of the defined waiting period.  If the web order has not been completed by
the end of the waiting period, the cart will be lost.

# Testing
[Pytest](https://docs.pytest.org/en/7.1.x/index.html) is used for testing.
All tests are in the `tests` directory.  The
full test suite can be run with the following command.

```shell
pytest
```

Some of the tests are full integration tests that assume connections to the
internet and a Google Cloud account.  The full integration tests need access to
a Google Sheet.  The sheet for these tests should be defined in `.env` using
the following variables.  The Google sheet should also have a small number of
records in it and the ISBN column should use the heading "ISBN-13".  These
tests will generate a slide deck on the authenticated account.  Such slide
decks will need to be manually deleted since the application does not have
permission to do so.

```
ASG_TEST_SHEET_ID="GOOGLE_SHEET_ID_HERE"
ASG_TEST_SHEET_TAB="GOOGLE_SHEET_TAB_HERE"
```

The full integration tests are time consuming and can be skipped using the
following command.

```shell
pytest -m 'not integration'
```

# Release Steps (WIP)
The release steps are executed using the [hatch](https://hatch.pypa.io/latest/)
Python project manager.

Hatch will dynamically create the version number.

## Lint
Ensure that the code passes the lint checks with the following command.
```
hatch run lint
```

## Test
All "not integration" tests must pass before building a package release candidate.
Run the following command and verify that *ALL* tests pass.
```
hatch run test
```

## Build
Build source and built distribution packages and remove previous builds with
the following command.
```
hatch build -c
```

## Publish
This assumes publishing to [pypi.org](https://pypi.org/).
An API token will be necessary to authorize publication.

Publish the build using the following command.
You can set the `user` and `auth` via the environment variables
`HATCH_INDEX_USER` and `HATCH_INDEX_AUTH` respectively if you don't
want to pass them on the command line.
```
hatch publish --user __token__ --auth pypi-<SECRET_TOKEN>
```

If publishing to test.pypi.org add the `--repo test` option to the `publish`
command.
```
hatch publish -r test -u __token__ -a pypi-<SECRET_TOKEN>
```
