import smtplib
import requests
from requests.auth import HTTPBasicAuth
import os
if os.path.isfile('local_config.py'):
    import local_config as config
else:
    import config


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

def do_github_api_request(url, method='get'):
    headers = {'User-Agent': 'two_factor_auth_auditor'}
    if method == 'get':
        response = requests.get(url, auth=HTTPBasicAuth(config.GitHubAuthKey, 'x-oauth-basic'), headers=headers)
    elif method == 'put':
        response = requests.put(url, auth=HTTPBasicAuth(config.GitHubAuthKey, 'x-oauth-basic'), headers=headers)
    elif method == 'delete':
        response = requests.delete(url, auth=HTTPBasicAuth(config.GitHubAuthKey, 'x-oauth-basic'), headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        try:
            return response.json()
        except:
            return response.status_code, False

def construct_email(users):
    message = "The following users don't have two factor authentication enabled:\n\n"
    for user in users:
        message = message + user.get('name', '(-not set-)') + " - " + user.get('login', '(-not set-)') + " - " \
                  + user.get('html_url', '(-no set-)') + "\n"

    return message
