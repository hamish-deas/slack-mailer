# Slack Mailer
Make copy-pasting messages in Slack a thing of the past. This is a python script that allows you to mass-message users in your Slack Workspace.

Messages will be sent from your Slack account, not from a bot user.

# Usage
Slack Mailer will message any users with email addresses listed in slackMailer.csv (or any other specified CSV).

Edit the script and add your message in `regular_message` and `onleave_message.

Once the CSV is populated with email addresses, simply run `python3 slack-mailer.py`.

# Credentials 
You will need a Slack App added to your workspace, with the following user token scopes:
* chat:write
* users:read
* users:read.email
* identity.email

Once set up, add SLACK_MAILER_TOKEN into your .env and assign your user OAuth token.
