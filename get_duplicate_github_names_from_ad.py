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

parser = argparse.ArgumentParser(description='Check for Github user names that are registered multiple times in LDAP')
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
    github_user_name = user_details[config.LDAP_SCHEMA_FIELD][0]
    ldap_github_users.append(github_user_name.lower())

duplicate_names = set([x for x in ldap_github_users if ldap_github_users.count(x) > 1])
# nothing to do, it all looks fine
if len(duplicate_names) == 0:
    exit()

message = "The following Github users are registered multiple times in AD:\n\n"
for name in duplicate_names:
    users = functions.get_ad_users_from_github_name(conn, base_dn, name)
    message = message + name + ": "
    for user in users:
        message = message + str(user[0][1]["distinguishedName"]) + " "
    message = message + "\n"

if skip_sending_email:
    print message
else:
    functions.send_mail(config.FromAddress, config.Receivers, "Github users that are registered multiple times in LDAP",
                        message, type="plain")
conn.unbind()
