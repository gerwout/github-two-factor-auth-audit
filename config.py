# Github Api Key (Settings -> Applications -> Personal Access Tokens)
GitHubAuthKey = ""
# name of the organisation in Github
Organisation = ""
# default team id for adding users to an organization, use the get_all_teams_for_org.py to find the id
DefaultTeamId = ""
# SMTP server to send email (hostname:port)
SMTPServer = ""
# do you need to authenticate on the smtp server?
SMTPAuth = False
# SMTP user name (optional, only set when SMTPAuth = True)
SMTPUser = ""
# SMTP password (optional, only set when SMTPAuth = True)
SMTPPass = ""
# the Address that sends the email
FromAddress = ""
# add email addresses that need to receive the email
Receivers = []
#Receivers.append("example@email.com")
#Receivers.append("example2@email.com")
# location of the sql lite database
# On Windows escape the backslash, i.e.: c:\\databases\\multi_factor.db
SQLFile = ""
# Your ldap/active directory server sends a certificate, this should be validated (value needs to be True or False)
# it's not a good idea to turn this off, it makes your SSL/TLS connection vulnerable for MITM attacks
LDAP_REQUIRE_VALID_CERT = True
# The certificate of the certificate authority that has signed the certificate from the LDAP/Active Directory server
# This needs to be a base64 encoded pem file
# On Windows escape the backslash, i.e.: c:\\trusted-certs\\certificate.pem
# Only used when LDAP_REQUIRE_VALID_CERT = True
LDAP_CA_CERT_ISSUER = ""
# Hostname of the LDAP / Active Directory server
# i.e. ldap://ad.domain.local:389 or ldaps://ad.domain.local:636
LDAP_HOST = ""
# Name of the field that contains the Github user name, it's case sensitive
# i.e. extensionAttribute1 can be used if you don't want to change your AD schema
LDAP_SCHEMA_FIELD = ''
# username that is going to query the LDAP / Active Directory server i.e. username@domain.local
LDAP_USER = ""
# Password that is used to authenticate
LDAP_PASS = ""
# DOMAIN that is going to be queried (i.e. domain.local)
LDAP_DOMAIN = ""
# Organisational unit(s) that will be used when searching the LDAP / Active Directory server
LDAP_OU_LIST = []
LDAP_OU_LIST.append('MyBusiness')
# Github user names that will be ignored if they are found while using the get_gitgub_users_from_ad.py script
LDAP_IGNORE_GITHUB_USERS = []
LDAP_IGNORE_GITHUB_USERS.append("ignoreuser")
