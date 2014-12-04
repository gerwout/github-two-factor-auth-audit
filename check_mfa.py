import os
if os.path.isfile('local_config.py'):
    import local_config as config
else:
    import config
import functions

if config.GitHubAuthKey == "":
    print "Please add your Github api key (Settings -> Applications -> Personal Access Tokens) to config.py\n"
    exit()
if config.Organisation == "":
    print "Please add your Github organisation (https://github.com/settings/organizations) to config.py\n"
    exit()
if config.SQLFile == "":
    print "Please add a SQLite database to config.py\n"
    exit()

if not os.path.isfile(config.SQLFile):
    conn, curs = functions.connect_db()
    functions.create_db_structure(conn, curs)
else:
    conn, curs = functions.connect_db()

# get all the users that don't have 2 factor authentication enabled
json_list = functions.do_github_api_request('https://api.github.com/orgs/' + config.Organisation + '/members?filter=2fa_disabled')
users = []

for user in json_list:
    user_dict = functions.do_github_api_request(user['url'])
    user_dict['first_alert'], user_dict['alert_count'] = functions.insert_user_row_in_db(conn, curs, user_dict)
    users.append(user_dict)

conn.close()
email = functions.construct_email(users)
functions.sendemail(config.FromAddress, config.Receivers, "Github Two Factor authentication audit", email)

