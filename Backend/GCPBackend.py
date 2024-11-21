import sys
import logging
import os                                   # For environment variables.
from google.cloud import storage, pubsub_v1 # For GCP clients.
import datetime                             # For URL expiration.


# Uncomment for local (non-containerized) debugging.
# from dotenv import load_dotenv
# env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
# load_dotenv(dotenv_path=env_path)
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_FILE')

# Global variables - consider swapping with a configuration file.
PROJECT_ID                     = os.getenv("PROJECT_ID")
LOCATION_ID                    = "us-east1"
BUCKCAT_NAME                   = "buckcat"
CATS_URLS_TOPIC_ID             = "cats_urls"
CATS_REQUESTS_SUBSCRIPTION_ID  = "cats_requests_subscription"


logger = logging.getLogger(__name__)
LOGS_FORMAT = '%(asctime)s - [%(levelname)s] - %(message)s'

def initialize_buckcat_client():
    storage_client = storage.Client()
    return storage_client.bucket(BUCKCAT_NAME)

def initialize_publisher_client():
    return pubsub_v1.PublisherClient()

def initialize_subscriber_client():
    return pubsub_v1.SubscriberClient()

def get_cats_list(buckcat):
    cats_iterator = buckcat.list_blobs()
    
    cats_list = []
    
    for cat_object in cats_iterator:
        cats_list.append(cat_object.name)
    
    return cats_list

def generate_cat_url(buckcat, cat_name):
    cat = buckcat.blob(cat_name)

    cat_url = cat.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(minutes=10),
        method="GET"
    )

    return cat_url

def publish_cat_url(publisher_client, cat_url):
    topic_path = publisher_client.topic_path(PROJECT_ID, CATS_URLS_TOPIC_ID)
    data = cat_url.encode("utf-8")
    future = publisher_client.publish(topic_path, data)
    logger.info(future.result())

def callback(message: pubsub_v1.subscriber.message.Message, publisher_client, buckcat, cats_list):
    logger.info(f"Received {message}.")
    # The topic message includes a single integer (which comes as a string).
    cat_request = int(message.data.decode('utf-8'))
    cat_url = generate_cat_url(buckcat, cats_list[cat_request])
    publish_cat_url(publisher_client, cat_url)
    message.ack()

def get_cat_request(subscriber_client, publisher_client, buckcat, cats_list):
    subscription_path = subscriber_client.subscription_path(PROJECT_ID, CATS_REQUESTS_SUBSCRIPTION_ID)
    streaming_pull_future = subscriber_client.subscribe(subscription_path, callback=lambda message: callback(message, publisher_client, buckcat, cats_list))
    
    logger.info(f"Listening for messages on {subscription_path}.\n")
    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber_client:
        try:
            # When `timeout` is not set, result() will block indefinitely, there's no need for timeout here since there's only one subscriber.
            streaming_pull_future.result()
        except TimeoutError:
            logger.error("Subscriber Pull Timed Out.")
            streaming_pull_future.cancel()  # Trigger the shutdown.
            streaming_pull_future.result()  # Block until the shutdown is complete.

def main():
    logging.basicConfig(format=LOGS_FORMAT, level = logging.INFO)
    
    buckcat = initialize_buckcat_client()
    subscriber_client = initialize_subscriber_client()
    publisher_client = initialize_publisher_client()
    
    cats_list = get_cats_list(buckcat)

    get_cat_request(subscriber_client, publisher_client, buckcat, cats_list)
        
        
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Received Keyboard Interrupt.")
        sys.exit(0)

