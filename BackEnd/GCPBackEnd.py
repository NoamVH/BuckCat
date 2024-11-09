import os
from google.cloud import storage, tasks_v2


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../Infrastructure/prefab-lamp-440513-v5-61362c8c30d4.json'


PROJECT_ID = "prefab-lamp-440513-v5"
LOCATION_ID = "us-east1"
front_to_back_queue_id = "front-to-back-queue"
BUCKCAT_NAME = "buckcat"

def initialize_buckcat_client():
    storage_client = storage.Client()
    return storage_client.bucket(BUCKCAT_NAME)

def initialize_tasks_client():
    return tasks_v2.CloudTasksClient()

def get_cats_list(buckcat):
    cats_iterator = buckcat.list_blobs()
    
    cats_list = []
    
    for cat_object in cats_iterator:
        cats_list.append(cat_object.name)
    
    return cats_list

# def get_queue_task(parent):
    



def main():
    buckcat = initialize_buckcat_client()
    print(get_cats_list(buckcat))
    
    
    front_to_back_tasks_client = initialize_tasks_client()
    parent = front_to_back_tasks_client.queue_path(PROJECT_ID, LOCATION_ID, front_to_back_queue_id)
    response = front_to_back_tasks_client.list_tasks(request={"parent": parent})

    for task in response:
        print(f"Task Name: {task.name}")
        if task.http_request:
            print(f"  HTTP Method: {task.http_request.http_method}")
            print(f"  URL: {task.http_request.url}")
            if task.http_request.body:
                print(f"  Body: {task.http_request.body.decode('utf-8')}")
        print("-" * 20)

    

if __name__ == "__main__":
    main()
