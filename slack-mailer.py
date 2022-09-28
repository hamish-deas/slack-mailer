import os
import logging
import readline
import csv
import time
from slack_sdk import WebClient
from dotenv import load_dotenv

# ### --- DO NOT EDIT ABOVE THIS LINE --- ###

# *** TO ENABLE DEBUG LOGGING, UNCOMMENT LINE ***
# logging.basicConfig(level=logging.DEBUG)

# slackMailer.csv is the name of the file containing the list of email addresses.
# Must provide full filepath unless the file is in the same directory as this script.
# Feel free to use your own filename.
user_csv = 'slackMailer.csv'

# Customise message for those who are not sick or on holiday
regular_message = ""
# Customise message for those are ARE on sick leave or holiday
onleave_message = ""

# If no message is set, no message will be sent to the users in that "scope".
# For more info on message formatting have a look at https://api.slack.com/reference/surfaces/formatting

# ### --- DO NOT EDIT BELOW THIS LINE --- ###
load_dotenv()

auth_token = os.getenv('SLACK_MAILER_TOKEN')
client = WebClient(token=auth_token)

# Auth token permissions required are:
# chat:write
# users:read
# users:read.email
# identity.email

def main(file_path):
    userlist = [] # create an empty list
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        for user in reader:
            user = str(user)[2:-2] # strips brackets and apostrophes from start and end of each line, otherwise looks like ['email@domain.com']
            if user not in userlist:
                userlist.append(user)
                try:
                    user_response = client.users_lookupByEmail(
                        email = user
                    )
                    if user_response['ok']:
                        user = user_response['user']
                        userid = str(user['id'])
                        fname = user['real_name'].split(' ')[0] # real_name contains first name and last name in columns, so grabs the first column
                        lname = user['real_name'].split(' ')[1] # grabs last name from second column
                        user_profile = user['profile']
                        status_emoji = user_profile['status_emoji']
                        status_text = user_profile['status_text'] # we don't do anything with this, yet
                        # If user is on holiday or on sick leave, allow sending of an alternative message
                        if status_emoji == ":palm_tree:" or status_emoji == ":face_with_thermometer:":
                            if onleave_message == "": # if no onleave_message set, skip
                                print(f"No onleave_message set, skipping {userid} - {fname} {lname} as either on holiday or sick leave")
                            else:
                                message_response = client.chat_postMessage(
                                    channel=userid,
                                    text=f"Hi {fname}\n\n{onleave_message}"
                                )
                                print(f"On-leave Message has successfully been sent to {userid} - {fname} {lname}") 
                        else:
                            if regular_message == "": # if no regular_message set, skip
                                print(f"No regular_message set, skipping {userid} - {fname} {lname}")
                            elif regular_message != "":
                                message_response = client.chat_postMessage(
                                    channel=userid,
                                    text=f"Hi {fname}\n\n{regular_message}"
                                )
                                print(f"Message has successfully been sent to {userid} - {fname} {lname}") 
                            # There is a rate limit of "several hundred messages per minute" across the workspace, so this limits
                            # the script to 120 messages per minute
                                time.sleep(0.5)
                            else:
                                raise Exception(user_response['error'])
                except Exception as e:
                    print(f'Error sending message to {user}. Error returned: {e}')

def prestage():
    print("** -- Slack Mailer -- **")
    print("Please enter your email address:")
    admin_email = input()
    if admin_email != "":
        user_response = client.users_lookupByEmail(
            email = admin_email
        )
        if user_response['ok']:
            user = user_response['user']
            userid = str(user['id'])
            fname = user['real_name'].split(' ')[0]
            lname = user['real_name'].split(' ')[1]
            user_profile = user['profile']
            print("You will now receive two messages in Slack showing what users will be sent")
            time.sleep(0.5)
            message_response = client.chat_postMessage(
                channel=userid,
                text=f"{regular_message}"
            )
            print(f"Regular Message has successfully been sent to {userid} - {fname} {lname}")
            time.sleep(1)
            message_response = client.chat_postMessage(
                channel=userid,
                text=f"{onleave_message}"
            )
            print(f"On-leave Message has successfully been sent to {userid} - {fname} {lname}")
        else:
            raise Exception(user_response['error'])
            time.sleep(0.5)

    while True:
        answer = input("Would you like to proceed, using the messages you've just received? (y/n)\n")
        if answer not in ('y', 'n'):
            print(f"Your response \"{answer}\" wasn't recognised. Please try again.")
            continue
        if answer == 'y':
            main(user_csv)
            break
        else:
            print("Exiting...")
            break

prestage()