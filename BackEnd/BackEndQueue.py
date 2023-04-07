import socket
import boto3 # AWS Python SDK library.
from botocore.client import Config # For using the s3v4 signing.

# Parameters:
CHUNK_SIZE = 2048 # For socket messages size.
BUCKET_NAME = 'buck-cat' # The name of the bucket used in AWS.
BACK_TO_FRONT_QUEUE = 'https://sqs.eu-central-1.amazonaws.com/283890144470/back-to-front-queue'
FRONT_TO_BACK_QUEUE = 'https://sqs.eu-central-1.amazonaws.com/283890144470/front-to-back-queue'


# This function gets the names of the files in the bucket and returns them as a list.
def cats_collection(s3_client, BUCKET_NAME):
    cats_list = []
    for object in s3_client.list_objects(Bucket = BUCKET_NAME)['Contents']:
        cats_list.append(object['Key'])
    return cats_list

# This function asks for URL for the current cat and sends it to the front end through the socket.
def get_URL(socket_session, s3_client, BUCKET_NAME, cats_list, cat):
    temp_url = s3_client.generate_presigned_url( # Generate a URL according to the parameters, expire in 10 seconds.
        ClientMethod = "get_object",
        Params = {"Bucket": BUCKET_NAME, "Key": cats_list[int(cat)]},
        ExpiresIn = 10
    )
    temp_url = bytes(temp_url, 'utf-8') # Convert the URL into bytes.
    return temp_url

# This function reads a message from the Front-to-Back SQS queue.
def receive_message(queue):
    """
    Receive a message in a request from an SQS queue.

    :param queue: The queue from which to receive messages.
    :return: The list of Message objects received. These each contain the body
             of the message and metadata and custom attributes.
    """
    messages = queue.receive_message(
        MessageAttributeNames=['All'],
    )
    return messages

# This function sends a message to the Back-to-Front SQS queue.
def send_message(queue, message_body, message_attributes=None):
    """
    Send a message to an Amazon SQS queue.

    :param queue: The queue that receives the message.
    :param message_body: The body text of the message.
    :param message_attributes: Custom attributes of the message. These are key-value
                               pairs that can be whatever you want.
    :return: The response from SQS that contains the assigned message ID.
    """
    if not message_attributes:
        message_attributes = {}
        response = queue.send_message(
            MessageBody=message_body,
            MessageAttributes=message_attributes
        )
    else:
        return response

# This function initializes the TCP socket and the S3 connection.
def initialize_connections():
    s3_client = boto3.client('s3', config=Config(region_name = 'eu-central-1', signature_version = 's3v4'))
    # Start a client in eu-central-1 and use AWS's recommended s3v4 signature version (this is REQUIRED to set when
    # running in a container).
    return s3_client


# Run the initialization functions
s3_client = initialize_connections()
cats_list = cats_collection(s3_client, BUCKET_NAME)
print(cats_list)

# Run the server
while True:
    cat = receive_message(FRONT_TO_BACK_QUEUE).decode('utf-8') # Receive selected cat from FrontEnd.
    url = get_URL(s3_client, BUCKET_NAME, cats_list, cat) # Get the URL and send it to FrontEnd.
    send_message(BACK_TO_FRONT_QUEUE, url) # Send URL to queue

# Test comment for git