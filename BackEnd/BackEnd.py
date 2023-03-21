import socket
import boto3 # AWS Python SDK library.
from botocore.client import Config # For using the s3v4 signing.

# Parameters:
CHUNK_SIZE = 2048 # For socket messages size.
BUCKET_NAME = 'buck-cat' # The name of the bucket used in AWS.


# This function gets the names of the files in the bucket and returns them as a list.
def cats_collection(s3_client, BUCKET_NAME):
    cats_list = []
    for object in s3_client.list_objects(Bucket = BUCKET_NAME)['Contents']:
        cats_list.append(object['Key'])
    return cats_list

# This function asks for URL for the current cat and sends it to the front end through the socket.
def get_URL_and_send_image(socket_session, s3_client, BUCKET_NAME, cats_list, cat):
    temp_url = s3_client.generate_presigned_url( # Generate a URL according to the parameters, expire in 10 seconds.
        ClientMethod = "get_object",
        Params = {"Bucket": BUCKET_NAME, "Key": cats_list[int(cat)]},
        ExpiresIn = 10
    )
    socket_session.send(bytes(temp_url, 'utf-8')) # Send the URL through the socket.
    print("URL Sent successfully\n")
    socket_session.close() # Close the socket.
    return None

# This function initializes the TCP socket and the S3 connection.
def initialize_connections():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Start an IPv4 TCP Socket.
    server_socket.bind(('0.0.0.0', 42069)) # Listen to all connections with the port 42069.
    server_socket.listen(10) # Up to 10 connections at a time.

    s3_client = boto3.client('s3', config=Config(region_name = 'eu-central-1', signature_version = 's3v4'))
    # Start a client in eu-central-1 and use AWS's recommended s3v4 signature version (this is REQUIRED to set when
    # running in a container).
    return server_socket, s3_client


# Run the initialization functions
server_socket, s3_client = initialize_connections()
cats_list = cats_collection(s3_client, BUCKET_NAME)
print(cats_list)


# Run the server
while True:
    print("Listening to clients sessions requests\n")
    socket_session, client_address = server_socket.accept() # Accepts connections to the socket.
    print(f"Session established with {client_address}")
    cat = socket_session.recv(CHUNK_SIZE).decode('utf-8') # Receive selected cat from FrontEnd.
    get_URL_and_send_image(socket_session, s3_client, BUCKET_NAME, cats_list, cat) # Get the URL and send it to FrontEnd.

# Test comment for git