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
logger.setLevel(logging.DEBUG)

application = Flask(__name__)

#
# TODO: slack user directly
# TODO; check for duplicates in receiving_users[] ?
#

@application.route('/APR', methods=['POST'])
def hello():
    logger.info("===================================================================")
    accepted_format = "Accepted format: /appreciate [@user(s)] [message]"
    origin_url = request.form['response_url']
    submitting_user_id = request.form['user_id']
    submitting_user_name = request.form['user_name']
    logger.info("Appreciation submitted by " + submitting_user_id + " aka " + submitting_user_name)

    raw_message = (request.form['text'])
    entire_message = raw_message.replace("[", "").replace("]", "")
    logger.info("INFO: entire_message = " + entire_message)

    if entire_message.lower() == "help":
        logger.info("INFO: Help requested")
        stas_user_id = "U"
        return("Need help? Try the following to correctly format your message. \n" + accepted_format + "\n If you help with something else, or have feedback, slack <@" + stas_user_id + "> directly.")

    receiving_users = []
    rgx = r'<@([\d\w]+?)\|(.+?)>'
    import re
    matches = re.finditer(rgx, entire_message)
    stripped_message = entire_message
    for m in matches:
        user_id = m.group(1)
        receiving_users.append(user_id)
        stripped_message = stripped_message.replace(m.group(2), "x")
    logger.info("INFO: receiving_users = %s" % receiving_users)

    if not receiving_users:
        logger.error("ERROR: Message did not contain a receiving_user")
        return("Hmm, slack could not find a valid user to address your appreciation to. Double check your message formatting. \n" + accepted_format)

    logger.info("INFO: stripped_message = " + stripped_message)
    if profanity.contains_profanity(stripped_message):
        logger.info("UH-OH: We've got ourselves a potty mouth.")
        return("NO SWEARING!")

    watercooler_url = "https://hooks.slack.com/services/url"
    watercooler_id = "C" # <#C|watercooler>
    appreciate_url = "https://hooks.slack.com/services/url"
    appreciate_id = "C" # <#C|appreciate>

    invite_url = "https://slack.com/api/channels.invite"
    debug_auth_token = "xoxp-token"
    natbot_auth_token = "xoxp-token"

    def do_post(origin_url, receiving_users, entire_message):
        import time
        time.sleep(1)
        r_post_watercooler = requests.post(watercooler_url, json = {"text" : entire_message, "response_type" : "in_channel"})
        r_post_appreciate = requests.post(appreciate_url, json = {"text" : entire_message, "response_type" : "in_channel"})
        logger.info("INFO: requests.post() message to watercooler returns: " + r_post_watercooler.text)
        logger.info("INFO: requests.post() message to appreciate returns: " + r_post_appreciate.text)

        for user in receiving_users:
            r_invite_watercooler = requests.post(invite_url, headers={'Authorization' : 'Bearer ' + natbot_auth_token, 'Content-type' : 'application/json; charset=utf-8'}, json = {"channel" : watercooler_id, "user" : user})
            r_invite_appreciate = requests.post(invite_url, headers={'Authorization' : 'Bearer ' + natbot_auth_token, 'Content-type' : 'application/json; charset=utf-8'}, json = {"channel" : appreciate_id, "user" : user})
            logger.info("INFO: requests.post() invite " + user + " to watercooler returns: " + r_invite_watercooler.text)
            logger.info("INFO: requests.post() invite " + user + " to appreciate returns: " + r_invite_appreciate.text)

    from threading import Thread
    thread = Thread(target=do_post, kwargs={'origin_url': origin_url, 'receiving_user': receiving_user, 'entire_message': entire_message})
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

