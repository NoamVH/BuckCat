import os                                                   # For file handling.
import random                                               # For random strings.
import string                                               # For random strings.
from google.cloud import tasks_v2                           # For GCP tasks clients.
from flask import Flask, render_template, request, redirect # Flask library.


# Global Variables
PROJECT_ID = "prefab-lamp-440513-v5"
LOCATION_ID = "us-east1"
current_cat = 0                                 # For initial cat from the cat list
MAX_CATS = 19                                   # The maximum number of cats in the bucket
FRONT_TO_BACK_QUEUE_ID = "front-to-back-queue"
BACK_TO_FRONT_QUEUE_ID = "back-to-front-queue"


#Initialize the application
app = Flask(__name__)

def initialize_tasks_client():
    return tasks_v2.CloudTasksClient()


# This function creates a random string 
def create_random_deduplication_id():
    '''
    Creates a random string that is eight letters long
    The string is used as a deduplication ID for GCP tasks.
    '''
    length = 8
    letters = string.ascii_lowercase
    random_string = ''.join(random.choice(letters) for i in range(length))
    return random_string

def iterate_cats(current_cat, MAX_CATS):
    current_cat += 1
    if current_cat == MAX_CATS:
        current_cat = 0
        return current_cat
    return current_cat

def request_cat(tasks_client, current_cat):
    parent = tasks_client.queue_path(PROJECT_ID, LOCATION_ID, FRONT_TO_BACK_QUEUE_ID)

    task = {
        "http_request": {
            "http_method": tasks_v2.HttpMethod.POST,
            "url": f"https://backend.buckcat/?cat_number={current_cat}",
            "headers": {"Content-Type": "text/plain"},
        }
    }

    cat_request = tasks_v2.CreateTaskRequest(parent=parent, task=task)

    tasks_client.create_task(request=cat_request)

def get_cats_queue_tasks(tasks_client):
    parent = tasks_client.queue_path(PROJECT_ID, LOCATION_ID, BACK_TO_FRONT_QUEUE_ID)

    try:
        return tasks_client.list_tasks(request={"parent": parent})
        
    except Exception as tasks_exception:
        print(f"Exception type: {type(tasks_exception).__name__}")
        print("Failed in getting tasks, exception: " + str(tasks_exception))


def get_cat_url(cat):
    print("body" + cat.http_request.body.decode('utf-8'))

    return cat.http_request.body.decode('utf-8')

# Main page
@app.route('/', methods = ["GET", "POST"]) # "GET" is required for internal files.
def home_page():
    global current_cat
    url = '' # Initial empty URL so the homepage can be sent at first run.
    tasks_client = app.config['TASKS_CLIENT']

    if request.method == "POST":
        print("requesting cat")
        request_cat(tasks_client, current_cat)
        cats = get_cats_queue_tasks(tasks_client)
        current_cat = iterate_cats(current_cat, MAX_CATS)
        
        for cat in cats:
            url = get_cat_url(cat)
            tasks_client.delete_task(request={"name": cat.name})
            break

    return render_template("homepage.html", url = url)

# Explanation page
@app.route('/explanation')
def explanation_page():
    solution_image = app.config['SOLUTION_IMAGE']
    return render_template('explanation.html', solution_image = solution_image)

def main():  
    tasks_client = initialize_tasks_client()
    
    solution_image = os.path.join('static', 'Images', 'solution.png') # Path to the site's Images folder

    app.config['TASKS_CLIENT'] = tasks_client
    app.config['SOLUTION_IMAGE'] = solution_image
    
    # The debug argument allows continous running of the webapp when changing something in the files and saving, the app will be refreshed automatically.
    # The port argument is optional, the default value is 5000.
    app.run(debug = True, host = '0.0.0.0')
    # app.run(debug = False, host = '0.0.0.0', port = 80)

if __name__  == '__main__':
    main()
