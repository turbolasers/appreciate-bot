#!/usr/bin/python3

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
# TODO: slack user directly
# TODO; check for duplicates in receiving_users[] ?
#

@application.route('/APR', methods=['POST'])
def hello():
    logger.info("===================================================================")
    accepted_format = "Accepted format: /appreciate [@user] [message]"
    origin_url = request.form['response_url']
    submitting_user_id = request.form['user_id']
    submitting_user_name = request.form['user_name']
    logger.info("Appreciation submitted by " + submitting_user_id + " aka " + submitting_user_name)

    original_message = (request.form['text'])
    entire_message = original_message.replace("[", "").replace("]", "")
    logger.info("INFO: entire_message = " + entire_message)

    if entire_message.lower() == "help":
        logger.info("INFO: Help requested")
        stas_user_id = "U"
        return("Need help? Sure thing! Try the following to correctly format your message. \n" + accepted_format + "\n If you help with something else, or have feedback, slack <@" + stas_user_id + "> directly.")

    try:
        receiving_user, appreciation_message = entire_message.split(" ", 1)
    except:
        logger.error("ERROR: Could not split entire_message")
        return("Hmm, your message doesn't appear to be formatted correctly. Try the following. \n" + accepted_format)

    receiving_user_id_formatted = receiving_user.split("|")[0] + ">"
    if not receiving_user_id_formatted.startswith("<@"):
        logger.error("ERROR: Message did not begin with a receiving_user")
        return("Hmm, slack could not find a valid user to address your appreciation to. Double check your message formatting. \n" + accepted_format)
    receiving_user_id = receiving_user_id_formatted.replace("<", "").replace("@", "").replace(">", "")

    # import string
    # stripped_message = ''.join(st for st in appreciation_message if st not in string.punctuation and not st == ' ')
    stripped_message = appreciation_message    # delete this line if you uncomment the above two
    logger.info("INFO: stripped_message = " + stripped_message)

    if profanity.contains_profanity(stripped_message):
        logger.info("UH-OH: We've got ourselves a potty mouth.")
        return("NO SWEARING!")
    logger.info("Appreciation to be recieved by " + receiving_user)
    logger.info(appreciation_message)

    watercooler_url = "https://hooks.slack.com/services/url"
    watercooler_id = "C" # <#C|watercooler>
    appreciate_url = "https://hooks.slack.com/services/url"
    appreciate_id = "C" # <#C|appreciate>

    invite_url = "https://slack.com/api/channels.invite"
    debug_auth_token = "xoxp-token"
    natbot_auth_token = "xoxp-token"

    def do_post(origin_url, receiving_user, appreciation_message):
        import time
        time.sleep(1)
        r_post_watercooler = requests.post(watercooler_url, json = {"text" : receiving_user + " " + appreciation_message, "response_type" : "in_channel"})
        r_post_appreciate = requests.post(appreciate_url, json = {"text" : receiving_user + " " + appreciation_message, "response_type" : "in_channel"})
        r_invite_watercooler = requests.post(invite_url, headers={'Authorization' : 'Bearer ' + natbot_auth_token, 'Content-type' : 'application/json; charset=utf-8'}, json = {"channel" : watercooler_id, "user" : receiving_user_id})
        r_invite_appreciate = requests.post(invite_url, headers={'Authorization' : 'Bearer ' + natbot_auth_token, 'Content-type' : 'application/json; charset=utf-8'}, json = {"channel" : appreciate_id, "user" : receiving_user_id})
        logger.info("requests.post() message to watercooler returns: " + r_post_watercooler.text)
        logger.info("requests.post() message to appreciate returns: " + r_post_appreciate.text)
        logger.info("requests.post() invite " + receiving_user + " to watercooler returns: " + r_invite_watercooler.text)
        logger.info("requests.post() invite " + receiving_user + " to appreciate returns: " + r_invite_appreciate.text)

    from threading import Thread
    thread = Thread(target=do_post, kwargs={'origin_url': origin_url, 'receiving_user': receiving_user, 'appreciation_message': appreciation_message})
    thread.start()
    return ""

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@application.route('/natbot/s3cr3tshutd0wnhax', methods=['GET'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

@application.route('/healthcheck', methods=['GET'])
def healthcheck():
    return 'Server is healthy'

if __name__ == "__main__":
    application.debug = True
    application.run(host='0.0.0.0', port=80)

