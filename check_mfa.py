import os
import functions
import argparse

cur_path = os.path.dirname(os.path.realpath(__file__))
if (os.name == 'nt'):
    path_seperator = "\\"
else:
    path_seperator = "/"

if os.path.isfile(cur_path + path_seperator + 'local_config.py'):
    import local_config as config
else:
    import config

if config.GitHubAuthKey == "":
    print "Please add your Github api key (Settings -> Applications -> Personal Access Tokens) to config.py\n"
    exit()
if config.Organisation == "":
    print "Please add your Github organisation (https://github.com/settings/organizations) to config.py\n"
    exit()
if config.SQLFile == "":
    print "Please add a SQLite database to config.py\n"
    exit()

parser = argparse.ArgumentParser(description='Audit the Github users within your organisation to check if two factor authentication has been enabled.')
parser.add_argument('--skip-sending-email', nargs='?', default=False, help='Don\'t send an email, show it instead', const=True)
parser.add_argument('--dont-update-counter', nargs='?', default=False, help='Don\'t update the amount of alerts', const=True)

args = parser.parse_args()

dont_update_counter = args.dont_update_counter
skip_sending_email = args.skip_sending_email

if not os.path.isfile(config.SQLFile):
    conn, curs = functions.connect_db()
    functions.create_db_structure(conn, curs)
else:
    conn, curs = functions.connect_db()

# get all the users that don't have 2 factor authentication enabled
json_list = functions.do_github_api_request('https://api.github.com/orgs/' + config.Organisation + '/members',
                                            params={"filter": "2fa_disabled"})
users = []

for user in json_list:
    user_dict = functions.do_github_api_request(user['url'])
    user_dict['first_alert'], user_dict['alert_count'] = functions.insert_user_row_in_db(conn, curs, user_dict,
                                                                                         dont_update_counter)
    users.append(user_dict)

conn.close()
email = functions.construct_email(users)
if skip_sending_email:
    print email
else:
    functions.sendemail(config.FromAddress, config.Receivers, "Github Two Factor authentication audit", email)

