import calendar
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE
import smtplib
from datetime import datetime
import requests
import sqlite3
import time
import os
import sys
import re
import ldap
import hashlib
from os.path import basename
import tempfile
import cPickle as pickle

cur_path = os.path.dirname(os.path.realpath(__file__))
if (os.name == 'nt'):
    path_seperator = "\\"
else:
    path_seperator = "/"

if os.path.isfile(cur_path + path_seperator + 'local_config.py'):
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

def insert_user_row_in_db(conn, curs, user, dont_update_counter):
    login = user.get('login', False)
    cur_date = datetime.now().strftime("%Y-%m-%d")
    if login:
        select_sql = "SELECT count(*) as count FROM github_users WHERE github_login = ?"
        res = curs.execute(select_sql, (login,))
        if not dont_update_counter:
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
        if item:
            first_alert = item[2]
            alert_count = item[3]
        else:
            first_alert = 1
            alert_count = 1
        return first_alert, alert_count

def do_github_api_request(url, params={}, method='get'):
    tmp_dir = tempfile.gettempdir() + path_seperator
    cache_name = tmp_dir + hashlib.md5(url + str(params) + method).hexdigest()

    if config.CACHE_GITHUB_CALLS and method == "get" and os.path.isfile(cache_name):
        file_time = os.path.getmtime(cache_name)
        cur_time = calendar.timegm(time.gmtime())
        if cur_time - file_time <= config.CACHE_TIME_IN_SECONDS:
            use_cache = True
        else:
            use_cache = False
    else:
        use_cache = False

    if method == 'get':
        if not 'page' in params.keys():
            params["page"] = 1
        # 100 is the maximum for Github
        if not 'per_page' in params.keys():
            params['per_page'] = 100

    if not use_cache:
        headers = {'User-Agent': 'two_factor_auth_auditor', 'Authorization': "token " + config.GitHubAuthKey}
        if method == 'get':
            response = requests.get(url, params=params, headers=headers)
            http_code = response.status_code
            if http_code == 200:
                results = response.json()
                pickle.dump(results, open(cache_name, "wb"))
                if len(results) == params['per_page']:
                    params['page'] = params['page'] + 1
                    results = results + do_github_api_request(url, params=params)
                    return results
                else:
                    return results
            elif http_code == 403:
                rate_limit_remaining = response.headers.get('x-ratelimit-remaining', False)
                if rate_limit_remaining == '0':
                    raise Exception, 'The given token has been rate limited, please retry in an hour'
                return response.status_code, False, response.json()
            else:
                # print(response.json())
                # print(response.headers)
                return response.status_code, False, response.json()
        elif method == 'put':
            response = requests.put(url, headers=headers)
            try:
                return response.json()
            except:
                return response.status_code, False
        elif method == 'delete':
            response = requests.delete(url, headers=headers)
            try:
                return response.json()
            except:
                return response.status_code, False
    else:
        results = pickle.load(open(cache_name, "rb"))
        if len(results) == params['per_page']:
            params['page'] = params['page'] + 1
            results = results + do_github_api_request(url, params=params)
            return results
        else:
            return results


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
        message = message + name.encode('utf-8') + " - " + login.encode('utf-8') + " - " + html_url.encode('utf-8') + \
                  " - " + first_alert.encode('utf-8') + " - " + alert_count.encode('utf-8') + "\n"

    return message

def connect_and_bind_to_ldap(ldap_host, ldap_user, ldap_pass):
    try:
        result = re.match("^(?P<protocol>ldap[s]{0,1})://(?P<hostname>.*)$", ldap_host)
        protocol = result.group('protocol')
    except:
        print "LDAP_HOST needs to start with ldap:// or ldaps:// and it needs to be a valid hostname"
        print "i.e. ldaps://exampledomain.local:636"
        print "i.e. ldap://exampledomain.local:389"
        exit()
    if not config.LDAP_REQUIRE_VALID_CERT:
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    else:
        ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, config.LDAP_CA_CERT_ISSUER)
    try:
        conn = ldap.initialize(ldap_host)
    except ldap.LDAPError as e:
        if type(e.message) == dict:
            if e.message.has_key('desc'):
                print e.message['desc']
            if e.message.has_key('info'):
                print e.message['info']
            sys.exit()
    try:
        if protocol == "ldap":
            conn.start_tls_s()
    except ldap.CONNECT_ERROR as e:
        if type(e.message) == dict:
            if e.message.has_key('desc'):
                print e.message['desc']
            if e.message.has_key('info'):
                print e.message['info']
            sys.exit()
    try:
        conn.simple_bind_s(ldap_user, ldap_pass)
    except ldap.LDAPError as e:
        if type(e.message) == dict:
            if e.message.has_key('desc'):
                print e.message['desc']
            if e.message.has_key('info'):
                print e.message['info']
            sys.exit()
    return conn

def search_ldap(conn, base_dn, search_filter):
    try:
        ldap_result_id = conn.search(base_dn, ldap.SCOPE_SUBTREE, search_filter)
        result_set = []
        while 1:
            result_type, result_data = conn.result(ldap_result_id, 0)
            if (result_data == []):
                break
            elif result_type == ldap.RES_SEARCH_ENTRY:
                result_set.append(result_data)
        return result_set
    except ldap.LDAPError as e:
        if type(e.message) == dict:
            if e.message.has_key('desc'):
                print e.message['desc']
            if e.message.has_key('info'):
                print e.message['info']
            sys.exit()

def get_ad_users_from_github_name(ldap_conn, base_dn, user_name):
        search_filter = "(&(objectCategory=user)(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2))(" \
                        + config.LDAP_SCHEMA_FIELD + "=" + ldap.dn.escape_dn_chars(user_name) + "))"
        result = search_ldap(ldap_conn, base_dn, search_filter)

        return result

def get_email_address_for_users(conn, base_dn, users):
    email_users = []
    for user in users:
        result = get_ad_users_from_github_name(conn, base_dn, user['login'])
        count = len(result)
        if count == 1:
            user_details = result[0][0][1]
            email_users.append(user_details['userPrincipalName'])

    return email_users

# @type: html or plain
def send_mail(send_from, send_to, subject, text, files=None, type="html"):
    assert isinstance(send_to, list)
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Subject'] = subject
    msg.attach(MIMEText(text, type))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(fil.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % basename(f))
            msg.attach(part)
    try:
        smtp = smtplib.SMTP(config.SMTPServer)
        smtp.starttls()
        if (config.SMTPAuth):
            smtp.login(config.SMTPUser, config.SMTPPass)

        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.quit()
    except:
        type, value, traceback = sys.exc_info()
        print("Could not send an email!")
        print(type)
        print(value)
