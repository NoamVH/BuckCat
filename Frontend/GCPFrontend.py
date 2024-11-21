import os                                                   # For file handling.
import random                                               # For random strings.
import string                                               # For random strings.
from google.cloud import pubsub_v1                          # For GCP Pub/Sub clients.
from flask import Flask, render_template, request, redirect # Flask library.


# Global Variables
PROJECT_ID                = os.getenv("PROJECT_ID")
LOCATION_ID               = "us-east1"
current_cat               = 0                        # For initial cat from the cat list.
MAX_CATS                  = 19                       # The maximum number of cats in the bucket.
CATS_REQUESTS_TOPIC_ID    = "cats_requests"
CATS_URLS_SUBSCRIPTION_ID = "cats_urls_subscription"


#Initialize the application
app = Flask(__name__)

def initialize_publisher_client():
    return pubsub_v1.PublisherClient()

def initialize_subscriber_client():
    return pubsub_v1.SubscriberClient()

def create_random_deduplication_id():
    '''
    Creates a random string that is eight letters long
    The string is used as a deduplication ID for GCP tasks.
    '''
    id_length = 8
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(id_length))

def iterate_cats(current_cat, MAX_CATS):
    current_cat += 1
    return 0 if current_cat == MAX_CATS else current_cat

def publish_cat_request(publisher_client, current_cat):
    topic_path = publisher_client.topic_path(PROJECT_ID, CATS_REQUESTS_TOPIC_ID)
    data = str(current_cat).encode("utf-8")
    future = publisher_client.publish(topic_path, data)
    print(f"Published request for cat {current_cat}: {future.result()}")

def get_cat_url(subscriber_client, publisher_client):
    subscription_path = subscriber_client.subscription_path(PROJECT_ID, CATS_URLS_SUBSCRIPTION_ID)
    #streaming_pull_future = subscriber_client.pull(subscription_path, callback=lambda message: callback(message, publisher_client))
    response = subscriber_client.pull(
        request={"subscription": subscription_path, "max_messages": 1}
    )
    
    if response.received_messages:
        message = response.received_messages[0]
        cat_url = message.message.data.decode("utf-8")
        # message.ack()
        return cat_url
    return None

# Main inital page.
@app.route('/', methods = ["GET", "POST"]) # "GET" is required for internal files.
def home_page():
    return render_template("homepage.html", url = '')

# Cat request route, same page but with a cat.
@app.route('/request_cat', methods=["POST"])
def request_cat():
    global current_cat
    publisher_client = app.config['PUBLISHER_CLIENT']
    subscriber_client = app.config['SUBSCRIBER_CLIENT']

    publish_cat_request(publisher_client, current_cat)

    cat_url = get_cat_url(subscriber_client, publisher_client)

    current_cat = iterate_cats(current_cat, MAX_CATS)

    return render_template("homepage.html", url=cat_url or "No cat URL found")

# Explanation page.
@app.route('/explanation')
def explanation_page():
    solution_image = app.config['SOLUTION_IMAGE']
    return render_template('explanation.html', solution_image = solution_image)

def main():  
    subscriber_client = initialize_subscriber_client()
    publisher_client = initialize_publisher_client()
    
    solution_image = os.path.join('static', 'Images', 'solution.png') # Path to the site's Images folder

    app.config['SUBSCRIBER_CLIENT'] = subscriber_client
    app.config['PUBLISHER_CLIENT'] = publisher_client
    app.config['SOLUTION_IMAGE'] = solution_image
    
    # The debug argument allows continous running of the webapp when changing something in the files and saving, the app will be refreshed automatically.
    # The port argument is optional, the default value is 5000.
    # app.run(debug = True, host = '0.0.0.0')
    app.run(debug = False, host = '0.0.0.0', port = 80)

if __name__  == '__main__':
    main()
