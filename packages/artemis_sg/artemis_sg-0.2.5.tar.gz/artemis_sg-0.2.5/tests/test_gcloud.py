import logging
import os
import shutil
import time
from inspect import getsourcefile

import pytest

from artemis_slide_generator.gcloud import GCloud
from artemis_slide_generator.gcloud import main as GCloud_main


@pytest.fixture()
def valid_cloud():
    bucket_name = os.environ["GOOGLE_CLOUD_BUCKET"]
    cloud_key_file = os.environ["GOOGLE_CLOUD_KEY_FILE"]
    return GCloud(cloud_key_file=cloud_key_file, bucket_name=bucket_name)


@pytest.fixture()
def image_filepath():
    here = os.path.dirname(getsourcefile(lambda: 0))
    resources = os.path.abspath(os.path.join(here, "..", "resources"))
    path = os.path.join(resources, "artemis_logo.png")
    return path


@pytest.fixture()
def target_directory(tmp_path_factory):
    path = tmp_path_factory.mktemp("data")
    yield path


@pytest.fixture()
def populated_target_directory(tmp_path_factory, image_filepath):
    path = tmp_path_factory.mktemp("data")
    shutil.copyfile(image_filepath, os.path.join(path, "9999999999990.jpg"))
    shutil.copyfile(image_filepath, os.path.join(path, "9999999999990-1.jpg"))
    f = open(os.path.join(path, "9999999999999.jpg"), "w")
    f.write("I am not an image file")
    f.close()
    yield path


@pytest.fixture()
def source_file(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    f = d / "test_file.txt"
    f.write_text("Hello, world!")
    return f


@pytest.mark.integration()
def test_upload_cloud_blob(valid_cloud, source_file):
    """
    GIVEN a GCloud object with a valid bucket name
    AND a local file
    WHEN upload_cloud_blob method is called on the object
    THEN no exception is thrown
    """
    val = valid_cloud.upload_cloud_blob(source_file, "test_prefix/test_file.txt")

    assert val is None


@pytest.mark.integration()
def test_generate_cloud_signed_url(valid_cloud):
    """
    GIVEN a GCloud object with a valid bucket name
    WHEN generate_cloud_signed_urlupload_cloud_blob method is called on the object
    THEN a storage.googleapis.com url is returned
    """
    url = valid_cloud.generate_cloud_signed_url("test_prefix/test_file.txt")

    bucket_name = os.environ["GOOGLE_CLOUD_BUCKET"]
    expected_str = f"https://storage.googleapis.com/{bucket_name}/test_prefix/test_file.txt?X-Goog-Algorithm="
    assert isinstance(url, str)
    assert expected_str in url


@pytest.mark.integration()
def test_list_blobs(valid_cloud):
    """
    GIVEN a GCloud object with a valid bucket name
    AND an existing blob in the bucket with known prefix
    WHEN list_blobs method is called on the object with known prefix
    THEN a blob iterator object is returned
         containing a blob object with the expected name
    """
    blobs = valid_cloud.list_blobs("test_prefix")

    blob = next(blobs)

    # FIXME: should not depend on test_upload_cloud_blob
    assert blob.name == "test_prefix/test_file.txt"


@pytest.mark.integration()
def test_list_blobs_does_not_exist(valid_cloud):
    """
    GIVEN a GCloud object with a valid bucket name
    WHEN list_blobs method is called on the object with an invalid prefix
    THEN a blob object is returned with the expected name
    """
    blobs = valid_cloud.list_blobs("invalid_prefix")

    with pytest.raises(StopIteration):
        next(blobs)


@pytest.mark.integration()
def test_main_old_existing_files_not_upload(caplog, populated_target_directory):
    """
    GIVEN a local file directory
    AND it contains a file that exists as a blob in GCloud
    AND the file is old
    WHEN Gcloud.main is called
    THEN the file is not uploaded
    """
    caplog.set_level(logging.INFO)
    image_file = "9999999999990.jpg"
    image_directory = str(populated_target_directory)
    os.environ["ASG_UPLOAD_SOURCE"] = image_directory
    filepath = os.path.join(image_directory, image_file)

    # make image_file old
    one_day = 1 * 60 * 60 * 24
    old_time = time.time() - one_day
    os.utime(filepath, (old_time, old_time))

    GCloud_main()

    assert (
        "root",
        logging.INFO,
        f"gcloud.upload: File '{image_file}' found in Google Cloud bucket, not uploading.",
    ) in caplog.record_tuples


@pytest.mark.integration()
def test_main_new_existing_files_upload(caplog, populated_target_directory):
    """
    GIVEN a local file directory
    AND it contains a file that exists as a blob in GCloud
    AND the file is new
    WHEN Gcloud.main is called
    THEN the file is uploaded
    """
    caplog.set_level(logging.INFO)
    image_file = "9999999999990.jpg"
    image_directory = str(populated_target_directory)
    os.environ["ASG_UPLOAD_SOURCE"] = image_directory
    blob_name = f"{os.environ['GOOGLE_CLOUD_BUCKET_PREFIX']}/{image_file}"

    GCloud_main()

    assert (
        "root",
        logging.INFO,
        f"gcloud.upload: Uploading '{blob_name}' to Google Cloud bucket.",
    ) in caplog.record_tuples


@pytest.mark.integration()
def test_main_non_image_files_not_uploaded_deleted(caplog, populated_target_directory):
    """
    GIVEN a local file directory
    AND it contains a file that is not an image
    WHEN Gcloud.main is called
    THEN the file is not uploaded
    AND the file is deleted
    """
    caplog.set_level(logging.INFO)
    image_file = "9999999999999.jpg"
    image_directory = str(populated_target_directory)
    filepath = os.path.join(image_directory, image_file)
    os.environ["ASG_UPLOAD_SOURCE"] = image_directory

    GCloud_main()

    assert (
        "root",
        logging.ERROR,
        f"gcloud.upload: Err reading '{image_file}', deleting '{filepath}'",
    ) in caplog.record_tuples
    assert not os.path.exists(filepath)
