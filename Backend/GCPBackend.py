import os                                   # For GCP credentials environment variable.
from google.cloud import storage, pubsub_v1 # For GCP clients.
import datetime                             # For URL expiration.


# Needs to be removed in production?
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../Infrastructure/prefab-lamp-440513-v5-61362c8c30d4.json'

# Global variables - consider swapping with a configuration file.
PROJECT_ID = "prefab-lamp-440513-v5"
LOCATION_ID = "us-east1"
BUCKCAT_NAME = "buckcat"
CATS_URLS_TOPIC_ID = "cats_urls"
CATS_REQUESTS_SUBSCRIPTION_ID = "cats_requests_subscription"
SUBSCRIBER_TIMEOUT = 5.0


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
        expiration=datetime.timedelta(minutes=2),
        method="GET"
    )

    return cat_url

def publish_cat_url(publisher_client, cat_url):
    topic_path = publisher_client.topic_path(PROJECT_ID, CATS_URLS_TOPIC_ID)
    data = cat_url.encode("utf-8")
    future = publisher_client.publish(topic_path, data)
    print(future.result())

def callback(message: pubsub_v1.subscriber.message.Message, publisher_client, buckcat, cats_list):
    print(f"Received {message}.")
    # The topic message includes a single integer (which comes as a string).
    cat_request = int(message.data.decode('utf-8'))
    cat_url = generate_cat_url(buckcat, cats_list[cat_request])
    publish_cat_url(publisher_client, cat_url)
    message.ack()

def get_cat_request(subscriber_client, publisher_client, buckcat, cats_list):
    subscription_path = subscriber_client.subscription_path(PROJECT_ID, CATS_REQUESTS_SUBSCRIPTION_ID)
    streaming_pull_future = subscriber_client.subscribe(subscription_path, callback=lambda message: callback(message, publisher_client, buckcat, cats_list))
    print(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber_client:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            streaming_pull_future.result(timeout=SUBSCRIBER_TIMEOUT)
        except TimeoutError:
            print("Subscriber Pull Timed Out.")
            streaming_pull_future.cancel()  # Trigger the shutdown.
            streaming_pull_future.result()  # Block until the shutdown is complete.

def main():
    buckcat = initialize_buckcat_client()
    subscriber_client = initialize_subscriber_client()
    publisher_client = initialize_publisher_client()
    
    cats_list = get_cats_list(buckcat)

    get_cat_request(subscriber_client, publisher_client, buckcat, cats_list)
        
        
if __name__ == "__main__":
    main()
