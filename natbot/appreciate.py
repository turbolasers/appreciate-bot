import flask
import requests
from flask import Flask
from flask import request
from flask import abort
import profanity

import logging
logger = logging.getLogger('natbot')
logger.addHandler(logging.FileHandler('natbot.log'))
logger.setLevel(logging.INFO)

application = Flask(__name__)

@application.route('/APR', methods=['POST'])
def hello():
    accepted_format = "Accepted format: /appreciate [@user] [message]"
    origin_url = request.form['response_url']
    submitting_user_id = request.form['user_id']
    submitting_user = request.form['user_name']
    print("Appreciation submitted by " + submitting_user_id + " aka " + submitting_user)
    entire_message = (request.form['text'])
    if profanity.contains_profanity(entire_message):
        print("We've got ourselves a fucker.")
        return("NO SWEARING!")
    if entire_message.lower() == "help":
        print("Help requested")
        return(accepted_format)
    try:
        receiving_user, appreciation_text = entire_message.split(" ", 1)
    except:
        print("Error: Could not split entire_message")
        return(accepted_format)
    receiving_user_id = receiving_user.split("|")[0] + ">"
    if not receiving_user_id.startswith("<@"):
        print("Error: Message did not begin with a receiving_user")
        return(accepted_format)
    print("Appreciation to be recieved by " + receiving_user)
    print(appreciation_text)
    watercooler_url = "https://hooks.slack.com/services/url"
    my_bot_and_me_url = "https://hooks.slack.com/services/url"
    def do_post(origin_url, receiving_user, appreciation_text):
        import time
        time.sleep(1)
        r = requests.post(my_bot_and_me_url, json = {"text" : receiving_user + " " + appreciation_text, "response_type" : "in_channel"})
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

