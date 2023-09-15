import json
import os
import tempfile

import pytest


@pytest.fixture(autouse=True)
def database(request):
    fh, file_name = tempfile.mkstemp()
    os.close(fh)
    os.environ["ASG_VENDOR_DATAFILE"] = file_name
    data = {
        "sample": {
            "name": "Super Sample Test Vendor",
            "isbn_key": "ISBN-13",
        }
    }
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f)
    yield
    os.unlink(file_name)
