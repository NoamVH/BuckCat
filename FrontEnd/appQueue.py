import os
import socket
from flask import Flask, render_template, request, redirect


# Parameters:
CHUNK_SIZE = 2048 # For socket messages size
current_cat = 0 # For initial cat from the cat list
MAX_CATS = 19 # The maximum number of cats in the bucket
images_folder = os.path.join('static', 'Images') # Path to the site's Images folder
BACK_TO_FRONT_QUEUE = 'https://sqs.eu-central-1.amazonaws.com/283890144470/back-to-front-queue'
FRONT_TO_BACK_QUEUE = 'https://sqs.eu-central-1.amazonaws.com/283890144470/front-to-back-queue'


# This function simply iterates current_cat form 0 to MAX_CATS, according to the number of cats in the bucket
def iterate_cats(current_cat, MAX_CATS):
    current_cat += 1
    if current_cat == MAX_CATS:
        current_cat = 0
        return current_cat
    return current_cat

# This function reads a message from the Back-to-Front SQS queue.
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

# This functions sends the backend which cat it wants to get, and gets a URL to the cat from it
# The function uses the queues send and receive functions to get and send the messages.
def get_url(current_cat):
    send_message(FRONT_TO_BACK_QUEUE, bytes(str(current_cat), "utf-8") )
    url = receive_message(BACK_TO_FRONT_QUEUE).decode("utf-8")
    print("URL Received Seccessfully:")
    print(url)
    return url

#Initialize the application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = images_folder

# Main page
@app.route('/', methods = ["GET", "POST"])
def home_page():
    global current_cat
    url = ''
    # Check if the reqeust method is POST
    if request.method == "POST":
        animal = request.form['animal'] # Get the information from the form
        if animal == 'cat':
            current_cat = iterate_cats(current_cat, MAX_CATS) # Iterate to the next cat
            url = get_url(current_cat) # Get the URL, by using the queue
    return render_template("homepage.html", url = url) #Render and return the HTML document, with the correct URL.

# Explanation page
@app.route('/explanation')
def explanation_page():
    solution_image = os.path.join(app.config['UPLOAD_FOLDER'], 'solution.png')
    return render_template('explanation.html', solution_image = solution_image)

if __name__  == '__main__':
    app.run(debug = False, host = '0.0.0.0', port = 80)
    # The debug argument allows continous running of the webapp when changing something in the files and saving, the app will be refreshed automatically.
    # The port argument is optional, the default value is 5000.