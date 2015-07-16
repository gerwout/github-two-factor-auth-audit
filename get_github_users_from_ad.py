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

parser = argparse.ArgumentParser(description='Check if all Github users within an organisation are registered in LDAP')
parser.add_argument('--skip-sending-email', nargs='?', default=False, help='Don\'t send an email, show it instead', const=True)
args = parser.parse_args()
skip_sending_email = args.skip_sending_email

conn = functions.connect_and_bind_to_ldap(config.LDAP_HOST.lower(), config.LDAP_USER, config.LDAP_PASS)
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

search_filter = "(&(objectCategory=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2))(objectClass=user)(" + config.LDAP_SCHEMA_FIELD + "=*))"
result_set = functions.search_ldap(conn, base_dn, search_filter)

ldap_github_users = []

for user in result_set:
    user_details = user[0][1]
    account_details = user_details["userAccountControl"]
    disabled_user = (int(account_details[0]) & 2) == 2
    if not disabled_user:
        github_user_name = user_details[config.LDAP_SCHEMA_FIELD][0]
        ldap_github_users.append(github_user_name.lower())

github_members = functions.do_github_api_request('https://api.github.com/orgs/' + config.Organisation + '/members')

github_users = []
for member in github_members:
    login = member['login'].lower()
    if not login in (name.lower() for name in config.LDAP_IGNORE_GITHUB_USERS):
        github_users.append(login)

not_in_list = list(set(github_users) - set(ldap_github_users))
count = len(not_in_list)
if count > 0:
    message = "The following Github users are not set in the LDAP server:\n\n"
    for username in not_in_list:
        username = username.encode('utf-8')
        message = message + username + " (https://github.com/" + username  + ")\n"
    message = message + "\nPlease edit the " + config.LDAP_SCHEMA_FIELD + " property and add the Github user name.\n"
    if skip_sending_email:
        print message
    else:
        functions.send_mail(config.FromAddress, config.Receivers, "Github users that are not registered in LDAP",
                            message, type="plain")

conn.unbind()