import requests
from requests.auth import HTTPBasicAuth
import config
import smtplib

def sendemail(from_addr, to_addr_list, subject, message):
    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message

    server = smtplib.SMTP(config.SMTPServer)
    server.starttls()
    if (config.SMTPAuth):
        server.login(config.SMTPUser, config.SMTPPass)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()

def do_github_api_request(url):
    headers = {'User-Agent': 'two_factor_auth_auditor'}
    response = requests.get(url, auth=HTTPBasicAuth(config.GitHubAuthKey, 'x-oauth-basic'), headers=headers)
    if response.status_code == 200:
        return response.json()

def construct_email(users):
    message = "The following users don't have two factor authentication enabled:\n\n"
    for user in users:
        message = message + user.get('name', '(-not set-)') + " - " + user.get('login', '(-not set-)') + " - " \
                  + user.get('html_url', '(-no set-)') + "\n"

    return message

if config.GitHubAuthKey == "":
    print "Please add your Github api key (Settings -> Applications -> Personal Access Tokens) to config.py\n"
    exit()
if config.Organisation == "":
    print "Please add your Github organisation (https://github.com/settings/organizations) to config.py\n"
    exit()


# get all the users that don't have 2 factor authentication enabled
json_list = do_github_api_request('https://api.github.com/orgs/' + config.Organisation + '/members?filter=2fa_disabled')
users = []

for user in json_list:
    user_dict = do_github_api_request(user['url'])
    users.append(user_dict)

email = construct_email(users)

sendemail(config.FromAddress, config.Receivers, "Github Two Factor authentication audit", email)