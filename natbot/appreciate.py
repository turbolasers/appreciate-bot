import flask
import requests
from flask import Flask
from flask import request
from flask import abort
from profanity import profanity

profanity.load_words(open("profanity.txt", encoding='latin-1').read().split('\n'))

import logging
logger = logging.getLogger('natbot')
logger.addHandler(logging.FileHandler('natbot.log'))
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

application = Flask(__name__)

#
# TODO: replace "[" & "]" with "" in entire_message
# TODO: auto restart if flask crashes
# TODO:
#

@application.route('/APR', methods=['POST'])
def hello():
    accepted_format = "Accepted format: /appreciate [@user] [message]"
    origin_url = request.form['response_url']
    submitting_user_id = request.form['user_id']
    submitting_user = request.form['user_name']
    logger.info("Appreciation submitted by " + submitting_user_id + " aka " + submitting_user)
    
    original_message = (request.form['text'])
    entire_message = original_message.replace("[", "").replace("]", "")
    logger.info("INFO: entire_message = " + entire_message)
    try:
        receiving_user, appreciation_text = entire_message.split(" ", 1)
    except:
        logger.error("ERROR: Could not split entire_message")
        return("Error: Hmm, your message doesn't appear to be formatted correctly. Try the following. \n" + accepted_format)
    receiving_user_id = receiving_user.split("|")[0] + ">"
    if not receiving_user_id.startswith("<@"):
        logger.error("ERROR: Message did not begin with a receiving_user")
        return("Error: natbot could not find a valid user to address your appreciation to. Check your message formatting. \n" + accepted_format)
    import string
    stripped_message = ''.join(st for st in appreciation_text if st not in string.punctuation and not st == ' ')
    logger.info("INFO: stripped_message = " + stripped_message)
    if profanity.contains_profanity(stripped_message):
        logger.info("UH-OH: We've got ourselves a potty mouth.")
        return("NO SWEARING!")
    if stripped_message.lower() == "help":
        logger.info("INFO: Help requested")
        return(accepted_format)
    logger.info("Appreciation to be recieved by " + receiving_user)
    logger.info(appreciation_text)
    
    my_bot_and_me_url = "https://hooks.slack.com/services/url"
    watercooler_url = "https://hooks.slack.com/services/url"
    appreciate_url = "https://hooks.slack.com/services/url"
    def do_post(origin_url, receiving_user, appreciation_text):
        import time
        time.sleep(1)
        r = requests.post(watercooler_url, json = {"text" : receiving_user + " " + appreciation_text, "response_type" : "in_channel"})
        r2 = requests.post(appreciate_url, json = {"text" : receiving_user + " " + appreciation_text, "response_type" : "in_channel"})
        logger.info("requests.post() to watercooler returns: " + r.text)
        logger.info("requests.post() to appreciate returns: " + r2.text)
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

if __name__ == "__main__":
    application.debug = True
    application.run(host='0.0.0.0', port=80)

