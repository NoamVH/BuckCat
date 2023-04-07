import boto3 # AWS Python SDK library.
from botocore.client import Config # For using the s3v4 signing.

# Parameters:
BUCKET_NAME = 'buck-cat' # The name of the bucket used in AWS.
BACK_TO_FRONT_QUEUE = 'https://sqs.eu-central-1.amazonaws.com/283890144470/back-to-front-queue.fifo'
FRONT_TO_BACK_QUEUE = 'https://sqs.eu-central-1.amazonaws.com/283890144470/front-to-back-queue'


# This function gets the names of the files in the bucket and returns them as a list.
def cats_collection(s3_client, BUCKET_NAME):
    cats_list = []
    for object in s3_client.list_objects(Bucket = BUCKET_NAME)['Contents']:
        cats_list.append(object['Key'])
    return cats_list

# This function asks for URL for the current cat and sends it to the front end through the socket.
def get_URL(s3_client, BUCKET_NAME, cats_list, cat):
    temp_url = s3_client.generate_presigned_url( # Generate a URL according to the parameters, expire in 10 seconds.
        ClientMethod = "get_object",
        Params = {"Bucket": BUCKET_NAME, "Key": cats_list[int(cat)]},
        ExpiresIn = 10
    )
    return temp_url

# This function initializes the TCP socket and the S3 connection.
def initialize_connections():
    s3_client = boto3.client('s3', config=Config(region_name = 'eu-central-1', signature_version = 's3v4'))
    sqs = boto3.client('sqs', config=Config(region_name = 'eu-central-1'))
    # Start a client in eu-central-1 and use AWS's recommended s3v4 signature version (this is REQUIRED to set when
    # running in a container).
    return sqs, s3_client


# Run the initialization functions
sqs, s3_client = initialize_connections()
cats_list = cats_collection(s3_client, BUCKET_NAME)

# Run the server
while True:
    cat_response = sqs.receive_message( # Receive selected cat from FrontEnd from the front-to-back SQS queue.
        QueueUrl = FRONT_TO_BACK_QUEUE,
        MaxNumberOfMessages = 1,
        MessageAttributeNames = ['All']
        )
    if 'Messages' in cat_response:
        cat_message = cat_response['Messages'][0]
        cat = cat_message['Body']
        url = get_URL(s3_client, BUCKET_NAME, cats_list, cat) # Get the URL and send it to FrontEnd.
        sqs.send_message( # Send the URL to the FrontEnd through the back-to-front SQS queue.
            QueueUrl = BACK_TO_FRONT_QUEUE,
            MessageGroupId = 'urls',
            MessageAttributes={},
            MessageBody= url
        )
        receipt_handle = cat_message['ReceiptHandle']
        sqs.delete_message(
        QueueUrl = FRONT_TO_BACK_QUEUE,
        ReceiptHandle = receipt_handle
    )