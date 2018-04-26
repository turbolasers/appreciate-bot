import flask
import requests
from flask import Flask
from flask import request

application = Flask(__name__)

@application.route('/APR', methods=['POST'])
def hello():
    origin_url = request.form['response_url']
    submitting_user_id = request.form['user_id']
    submitting_user = request.form['user_name']
    print("Appreciation submitted by " + submitting_user_id + " aka " + submitting_user)
    entire_message = (request.form['text'])
    receiving_user, appreciation_text = entire_message.split(" ", 1)
    receiving_user_id = receiving_user.split("|")[0] + ">"
    print("Appreciation to be recieved by " + receiving_user)
    print(appreciation_text)
    watercooler_url = "https://hooks.slack.com/services/url"
    def do_post(origin_url, receiving_user, appreciation_text):
        import time
        time.sleep(1)
        r = requests.post(watercooler_url, json = {"text" : receiving_user + " " + appreciation_text, "response_type" : "in_channel"})
        print(r.text)
    from threading import Thread
    thread = Thread(target=do_post, kwargs={'origin_url': origin_url, 'receiving_user': receiving_user, 'appreciation_text': appreciation_text})
    thread.start()
    return ""

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@application.route('/s3cr3tshutd0wnhax', methods=['GET'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run(host='0.0.0.0', port=80)

