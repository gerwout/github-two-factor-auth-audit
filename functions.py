import smtplib
import requests
import sqlite3
from datetime import datetime
from requests.auth import HTTPBasicAuth
import os
import sys
if os.path.isfile('local_config.py'):
    import local_config as config
else:
    import config

def connect_db():
    try:
        conn = sqlite3.connect(config.SQLFile)
    except sqlite3.OperationalError:
        print "Can't connect to the " + config.SQLFile + " database, do you have the right permissions?"
        exit()
    c = conn.cursor()

    return conn, c

def create_db_structure(conn, curs):
    create_sql = """
        CREATE TABLE `github_users` (
            `id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            `github_login`	TEXT,
            `first_alert`	DATE NOT NULL,
            `alert_count`	INTEGER NOT NULL
        );"""
    index_sql = "CREATE UNIQUE INDEX login ON github_users(github_login);"
    curs.execute(create_sql)
    curs.execute(index_sql)
    conn.commit()

def insert_user_row_in_db(conn, curs, user):
    login = user.get('login', False)
    cur_date = datetime.now().strftime("%Y-%m-%d")
    if login:
        select_sql = "SELECT count(*) as count FROM github_users WHERE github_login = ?"
        res = curs.execute(select_sql, (login,))
        count = res.fetchone()[0]
        if count == 0:
            insert_sql = "INSERT INTO github_users(github_login, first_alert, alert_count) VALUES (?, ?, 1)"
            res = curs.execute(insert_sql, (login, cur_date))
        else:
            update_sql = "UPDATE github_users SET alert_count=alert_count + 1 WHERE github_login = ?"
            res = curs.execute(update_sql, (login, ))
        conn.commit()
        select_sql = "SELECT * FROM github_users WHERE github_login = ?"
        res = curs.execute(select_sql, (login,))
        item = res.fetchone()
        first_alert = item[2]
        alert_count = item[3]
        return first_alert, alert_count


def sendemail(from_addr, to_addr_list, subject, message):
    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message

    try:
        server = smtplib.SMTP(config.SMTPServer)
        server.starttls()
        if (config.SMTPAuth):
            server.login(config.SMTPUser, config.SMTPPass)
        problems = server.sendmail(from_addr, to_addr_list, message.encode("iso-8859-15"))
        server.quit()
    except:
        type, value, traceback = sys.exc_info()
        print("Could not send an email!")
        print('Exception details: %s' % (value.strerror))


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
    message = "The following users don't have two factor authentication enabled:\n"
    message += "Name, Login, URL, First alert, Amount of alerts\n\n"

    for user in users:
        name = user.get('name', '(-not set-)')
        login = user.get('login', '(-not set-)')
        html_url = user.get('html_url', '(-not set-)')
        first_alert = str(user.get('first_alert', '(-not set-)'))
        alert_count =  str(user.get('alert_count', '(-not set-)'))
        if name == None:
            name = '(-not set-)'
        if login == None:
            login = '(-not set-)'
        if html_url == None:
            html_url = '(-not set-)'

        message = message + name + " - " + login + " - " + html_url + " - " + first_alert + " - " + alert_count + "\n"

    return message
