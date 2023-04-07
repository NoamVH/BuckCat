import os # For file handling.
import boto3 # AWS Python SDK library.
from botocore.client import Config # For region setting.
from flask import Flask, render_template, request, redirect # Flask library.


# Parameters:
CHUNK_SIZE = 2048 # For socket messages size
current_cat = 0 # For initial cat from the cat list
MAX_CATS = 19 # The maximum number of cats in the bucket
images_folder = os.path.join('static', 'Images') # Path to the site's Images folder
BACK_TO_FRONT_QUEUE = 'https://sqs.eu-central-1.amazonaws.com/283890144470/back-to-front-queue'
FRONT_TO_BACK_QUEUE = 'https://sqs.eu-central-1.amazonaws.com/283890144470/front-to-back-queue'
sqs = boto3.client('sqs', config=Config(region_name = 'eu-central-1'))


# This function simply iterates current_cat form 0 to MAX_CATS, according to the number of cats in the bucket
def iterate_cats(current_cat, MAX_CATS):
    current_cat += 1
    if current_cat == MAX_CATS:
        current_cat = 0
        return current_cat
    return current_cat

# This functions sends the backend which cat it wants to get, and gets a URL to the cat from it
# The function uses the queues send and receive functions to get and send the messages.
def get_url(current_cat):
    sqs.send_message( # Send the current cat to the BackEnd through the front-to-back SQS queue.
        QueueUrl = FRONT_TO_BACK_QUEUE,
        MessageAttributes={},
        MessageBody= str(current_cat)
    )
    url = sqs.receive_message( # Receive URL from BackEnd from the back-to-front SQS queue.
        QueueUrl = BACK_TO_FRONT_QUEUE,
        MessageAttributeNames = ['All']
        )
    sqs.delete_message(
        QueueUrl = BACK_TO_FRONT_QUEUE
    )
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