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

base_dn = ""
dc_string = ""
for ou in config.LDAP_OU_LIST:
    base_dn = "OU="+ ou + ","

domain_list = config.LDAP_DOMAIN.split(".")
dc_string = ""
for part in domain_list:
    dc_string = dc_string + "DC="+part+","
dc_string = dc_string[:-1]
base_dn = base_dn + dc_string

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
    # lets send an overview email
    functions.send_mail(config.FromAddress, config.Receivers, "Github Two Factor authentication audit", email,
                        type="plain")
    if config.SEND_EMAIL_TO_USERS:
        ldap_conn = functions.connect_and_bind_to_ldap(config.LDAP_HOST.lower(), config.LDAP_USER, config.LDAP_PASS)
        email_users = functions.get_email_address_for_users(ldap_conn, base_dn, users)
        ldap_conn.unbind()
        # check if we have a custom email template
        if os.path.isfile(cur_path+"/templates/custom/email_instructions.html"):
            file_name = cur_path+"/templates/custom/email_instructions.html"
        else:
            file_name = cur_path+"/templates/email_instructions.html"

        with open (file_name, "r") as my_file:
            message=my_file.read().replace('\n', '')

        for email in email_users:
            functions.send_mail(config.FromAddress, email, "Please enable 2-factor authentication in Github", message,
                                files=[config.GITHUB_INSTRUCTIONS_DOC,])


