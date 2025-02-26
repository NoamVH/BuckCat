import logging
import os                                # For file handling.
import random                            # For random strings.
import string                            # For random strings.
from google.cloud import pubsub_v1       # https://cloud.google.com/python/docs/reference/pubsub/latest
from flask import Flask, render_template # https://flask.palletsprojects.com/en/stable/quickstart/
from waitress import serve               # https://flask.palletsprojects.com/en/stable/deploying/waitress/


# # Uncomment for local (non-containerized) debugging.
# from dotenv import load_dotenv  
# env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
# load_dotenv(dotenv_path=env_path)
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_FILE')


PROJECT_ID                = os.getenv("PROJECT_ID")
LOCATION_ID               = "us-east1"
current_cat               = 0                        # For initial cat from the cat list.
MAX_CATS                  = 19                       # The maximum number of cats in the bucket.
CATS_REQUESTS_TOPIC_ID    = "cats_requests"
CATS_URLS_SUBSCRIPTION_ID = "cats_urls_subscription"


logger = logging.getLogger(__name__)
LOGS_FORMAT = '%(asctime)s - [%(levelname)s] - %(message)s'


#Initialize the application
app = Flask(__name__)


def initialize_publisher_client():
    return pubsub_v1.PublisherClient()

def initialize_subscriber_client():
    return pubsub_v1.SubscriberClient()

def iterate_cats(current_cat, MAX_CATS):
    current_cat += 1
    return 0 if current_cat == MAX_CATS else current_cat

def publish_cat_request(publisher_client, current_cat):
    topic_path = publisher_client.topic_path(PROJECT_ID, CATS_REQUESTS_TOPIC_ID)
    data = str(current_cat).encode("utf-8")
    future = publisher_client.publish(topic_path, data)
    logger.info(f"Published request for cat {current_cat}: {future.result()}")

def get_cat_url(subscriber_client):
    subscription_path = subscriber_client.subscription_path(PROJECT_ID, CATS_URLS_SUBSCRIPTION_ID)
    response = subscriber_client.pull(
        request={"subscription": subscription_path, "max_messages": 1}
    )

    ack_ids = []
    for received_message in response.received_messages:
        print(f"Received: {received_message.message.data}.")
        ack_ids.append(received_message.ack_id)

    
    if response.received_messages:
        message = response.received_messages[0]
        cat_url = message.message.data.decode("utf-8")
        subscriber_client.acknowledge(
            request={"subscription": subscription_path, "ack_ids": ack_ids}
        )

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

    cat_url = get_cat_url(subscriber_client)

    current_cat = iterate_cats(current_cat, MAX_CATS)

    return render_template("homepage.html", url=cat_url or "No cat URL found")

# Explanation page.
@app.route('/gcp-explanation')
def gcp_explanation_page():
    solution_image = app.config['GCP_SOLUTION_IMAGE']
    return render_template('explanation-gcp.html', solution_image = solution_image)

@app.route('/aws-explanation')
def aws_explanation_page():
    solution_image = app.config['AWS_SOLUTION_IMAGE']
    return render_template('explanation-aws.html', solution_image = solution_image)

def main():  
    logging.basicConfig(format=LOGS_FORMAT, level = logging.INFO)
    
    subscriber_client = initialize_subscriber_client()
    publisher_client = initialize_publisher_client()
    
    aws_solution_image = os.path.join('static', 'Images', 'aws-solution.png')
    gcp_solution_image = os.path.join('static', 'Images', 'gcp-solution.png')

    app.config['SUBSCRIBER_CLIENT'] = subscriber_client
    app.config['PUBLISHER_CLIENT'] = publisher_client
    app.config['GCP_SOLUTION_IMAGE'] = gcp_solution_image
    app.config['AWS_SOLUTION_IMAGE'] = aws_solution_image
    
    # The debug argument allows continous running of the webapp when changing something in the files and saving, the app will be refreshed automatically.
    # The port argument is optional, the default value is 5000.
    # app.run(debug = True, host = '0.0.0.0')
    serve(app, host='0.0.0.0', port=80)

if __name__  == '__main__':
    main()
