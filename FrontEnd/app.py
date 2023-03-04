import os
import socket
from flask import Flask, render_template, request, redirect


# Parameters:
CHUNK_SIZE = 2048 # For socket messages size
current_cat = 0 # For initial cat from the cat list
MAX_CATS = 19 # The maximum number of cats in the bucket
images_folder = os.path.join('static', 'Images') # Path to the site's Images folder


# This function simply iterates current_cat form 0 to MAX_CATS, according to the number of cats in the bucket
def iterate_cats(current_cat, MAX_CATS):
    current_cat += 1
    if current_cat == MAX_CATS:
        current_cat = 0
        return current_cat
    return current_cat

# This function opens a socket
def initiazlie_socket():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('IP', 42069))
    return client_socket

# This functions sends the backend which cat it wants to get, and gets a URL to the cat from it
# The function then closes the socket
def get_url(session):
    session.send(bytes(str(current_cat), "utf-8"))
    url_piece = session.recv(CHUNK_SIZE).decode("utf-8")
    url = url_piece
    while url_piece:
        url_piece = session.recv(CHUNK_SIZE).decode("utf-8")
        url = url + url_piece
    print("URL Received Seccessfully:")
    print(url)
    session.close()
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
            client_socket = initiazlie_socket() # Start the socket
            current_cat = iterate_cats(current_cat, MAX_CATS) # Iterate to the next cat
            url = get_url(client_socket) # Get the URL
    return render_template("homepage.html", url = url) #Render and return the HTML document, with the correct URL.

# Explanation page
@app.route('/explanation')
def explanation_page():
    solution_image = os.path.join(app.config['UPLOAD_FOLDER'], 'solution.png')
    return render_template('explanation.html', solution_image = solution_image)

if __name__  == '__main__':
    app.run(debug = True, host = '0.0.0.0', port = 8000)
    # The debug argument allows continous running of the webapp when changing something in the files and saving, the app will be refreshed automatically.
    # The port argument is optional, the default value is 5000.
