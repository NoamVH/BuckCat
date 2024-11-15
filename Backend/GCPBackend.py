import os                                  # For GCP credentials environment variable.
import datetime                            # For URL expiration.
from google.cloud import storage, tasks_v2 # For GCP clients.


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../Infrastructure/prefab-lamp-440513-v5-61362c8c30d4.json'


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

def handle_incoming_queue_task(tasks_client):
    parent = tasks_client.queue_path(PROJECT_ID, LOCATION_ID, FRONT_TO_BACK_QUEUE_ID)
    
    try:
        response = tasks_client.list_tasks(request={"parent": parent})
        
        for task in response:
            print(f"Task Name: {task.name}")
            if task.http_request:
                print(f"HTTP Method: {task.http_request.http_method}")
                print(f"URL: {task.http_request.url}")
                if task.http_request.body:
                    print(f"Body: {task.http_request.body.decode('utf-8')}")
            print("-" * 20)

            tasks_client.delete_task(request={"name": task.name})

        cat_number = 0

        return cat_number
        
    except Exception as tasks_exception:
        print(f"Exception type: {type(tasks_exception).__name__}")
        print("Failed in getting a task, exception: " + str(tasks_exception))

def generate_cat_url(buckcat, cat_name):
    cat = buckcat.blob(cat_name)

    cat_url = cat.generate_signed_url(
        version="v4",
        # This URL is valid for 2 minutes
        expiration=datetime.timedelta(minutes=2),
        # Allow GET requests using this URL.
        method="GET",
    )

    return cat_url

def send_cat_url(tasks_client, cat_url):
    parent = tasks_client.queue_path(PROJECT_ID, LOCATION_ID, BACK_TO_FRONT_QUEUE_ID)
    
    task = {
        "http_request": {  # Using HTTP target
            "http_method": tasks_v2.HttpMethod.POST,
            "url": "https://frontend.buckcat/endpoint",  # Replace with your endpoint
            "headers": {"Content-Type": "application/json"},
            "body": cat_url.encode()  # Ensure the body is bytes
        }
    }
    
    # Construct the request.
    request = tasks_v2.CreateTaskRequest(parent=parent, task=task)

    # Make the request.
    response = tasks_client.create_task(request=request)

    # Handle the response.
    print(response)

    return None


def main():
    buckcat = initialize_buckcat_client()
    tasks_client = initialize_tasks_client()
    
    cats_list = get_cats_list(buckcat)
    print(cats_list)
    
    cat_number = handle_incoming_queue_task(tasks_client)

    cat_url = generate_cat_url(buckcat, cats_list[cat_number])

    print(cat_url)

    send_cat_url(tasks_client, cat_url)

if __name__ == "__main__":
    main()
