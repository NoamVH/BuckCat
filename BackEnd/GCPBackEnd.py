from google.cloud import storage

storage_client = storage.Client()

BUCKCAT_NAME = "buckcat"

buckcat = storage_client.bucket(BUCKCAT_NAME)

print(buckcat.list_blobs())

# cat = buckcat.blob(source_blob_name)

# cat.download_to_filename("cat.png")
