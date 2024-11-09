import os
from google.cloud import storage


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../Infrastructure/prefab-lamp-440513-v5-61362c8c30d4.json'


BUCKCAT_NAME = "buckcat"


def create_buckcat_client():
    storage_client = storage.Client()
    return storage_client.bucket(BUCKCAT_NAME)

def get_cats_list(buckcat):
    cats_iterator = buckcat.list_blobs()
    
    cats_list = []
    
    for cat_object in cats_iterator:
        cats_list.append(cat_object.name)
    
    return cats_list

def main():
    buckcat = create_buckcat_client()
    print(get_cats_list(buckcat))

if __name__ == "__main__":
    main()
