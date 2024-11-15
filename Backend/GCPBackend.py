import os                                    # For GCP credentials environment variable.
from google.cloud import storage, tasks_v2   # For GCP clients.
from urllib.parse import urlparse, parse_qsl # For Tasks URL parsing.
import datetime                              # For URL expiration.


# Needs to be removed in production?
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../Infrastructure/prefab-lamp-440513-v5-61362c8c30d4.json'

# Global variables - consider swapping with a configuration file.
PROJECT_ID = "prefab-lamp-440513-v5"
LOCATION_ID = "us-east1"
FRONT_TO_BACK_QUEUE_ID = "front-to-back-queue"
BACK_TO_FRONT_QUEUE_ID = "back-to-front-queue"
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

def get_queue_tasks(tasks_client):
    parent = tasks_client.queue_path(PROJECT_ID, LOCATION_ID, FRONT_TO_BACK_QUEUE_ID)
    
    try:
        return tasks_client.list_tasks(request={"parent": parent})
        
    except Exception as tasks_exception:
        print(f"Exception type: {type(tasks_exception).__name__}")
        print("Failed in getting tasks, exception: " + str(tasks_exception))

def get_cat_number_from_request(cat_task):  
    print(f"Task Name: {cat_task.name}")
    
    #print(f"HTTP Method: {cat_task.http_request.http_method}")

    parsed_url = urlparse(cat_task.http_request.url)
    query_params = dict(parse_qsl(parsed_url.query))
    cat_number = int(query_params.get("cat_number"))
    
    return int(cat_number)

def generate_cat_url(buckcat, cat_name):
    cat = buckcat.blob(cat_name)

    cat_url = cat.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(minutes=2),
        method="GET"
    )

    return cat_url

def send_cat_url(tasks_client, cat_url):
    parent = tasks_client.queue_path(PROJECT_ID, LOCATION_ID, BACK_TO_FRONT_QUEUE_ID)
    
    task = {
        "http_request": {
            "http_method": tasks_v2.HttpMethod.POST,
            "url": "https://frontend.buckcat/endpoint",  # Update this.
            "headers": {"Content-Type": "text/plain"},
            "body": cat_url.encode()
        }
    }
    
    # Construct the request.
    request = tasks_v2.CreateTaskRequest(parent=parent, task=task)

    # Create a task from the request.
    tasks_client.create_task(request=request)


def main():
    buckcat = initialize_buckcat_client()
    tasks_client = initialize_tasks_client()
    cats_list = get_cats_list(buckcat)
    
    while True:
        cat_requests = get_queue_tasks(tasks_client)

        for cat_request in cat_requests:
            cat_number = get_cat_number_from_request(cat_request)
            cat_url = generate_cat_url(buckcat, cats_list[cat_number])
            send_cat_url(tasks_client, cat_url)
            tasks_client.delete_task(request={"name": cat_request.name})
        
if __name__ == "__main__":
    main()
