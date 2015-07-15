github-two-factor-auth-audit
============================
A bunch off Python scripts that you can use to audit if every GIT user within your organization has two factor authentication enabled.

**check_mfa.py**    
Configurable python script that checks 2fa for every Github user in your organization.
It will create an overview of all the users that haven't enabled 2 factor authentication.
It will send this overview to predefined email addresses.
It can optionally send an email to the affected users with some instructions (i.e. SEND_EMAIL_TO_USERS and GITHUB_INSTRUCTIONS_DOC configuration settings).
It has 2 optional arguments:
--skip-sending-email Don't send an email, show it instead
--dont-update-counter Don't update the alert counter in the sqlite database

**get_all_teams_for_org.py**
Gives an overview of all the teams that are available for your organization.

**get_member_details.py**
Helper script that shows details from a Github user

**add_member_to_org.py**
Add a github user to a team within the organization that is defined in config.py

**delete_member_from_org.py**
Remove a github user from the organization that is defined in config.py

Setup Windows
=============
- Install Python 2.7 (http://docs.python-guide.org/en/latest/starting/install/win/)
- git clone https://github.com/gerwout/github-two-factor-auth-audit.git
- cd github-two-factor-auth-audit
- Create a virtual environment (i.e. virtualenv github-mfa-audit)
- Switch to that virtual environment (i.e. run activate.bat in the virtual environment)
- Install the requirements (i.e. pip install -r requirements.txt)
- Configure the script (i.e. edit config.py)
- You can now run python check_mfa.py

Setup Debian based Linux
========================
- Install Python 2.7
    -   apt-get install python2.7 python-pip
- Install virtual environment
    -   pip install virtualenv
    -   pip install virtualenvwrapper
    -   mkdir ~/virtualenvs
    -   edit ~/.bashrc
    Add the following lines:
    export WORKON_HOME=~/virtualenvs
    source /usr/local/bin/virtualenvwrapper.sh
- Create a virtual environment
    - mkvirtualenv github-mfa-audit
- git clone https://github.com/gerwout/github-two-factor-auth-audit.git
- Install the requirements (i.e. pip install -r requirements.txt)
- Configure the script (i.e. edit config.py)
- You can now run python check_mfa.py

Configuration
=============
All the configuration settings are defined in the config.py file.
It's also possible to create a local_config.py script that contains these settings. If you have a config.py and a local_config.py the local_config.py will have preference.

```python
GitHubAuthKey = ""
```
OAUTH Token: a Github personal access token is needed to be able to query the Github api.
Logon to Github and navigate to settings -> applications -> personal access tokens to generate one.
The read:org scope is needed for the check_mfa.py script to function properly.
To be able to add and/or delete users from an organization the admin:org scope is needed.

```python
Organisation = "" 
```
Name of the organisation 
Go to https://github.com/settings/organizations to find the correct name.

```python
DefaultTeamId = "" 
```
Default team id for adding users to an organization, use the get_all_teams_for_org.py to find the id

```python
SMTPServer = "" 
```
Mail server that will send the email (i.e. 127.0.0.1:25)

```python
SMTPAuth = False
```
Do you need to authenticate on the smtp server? (True or False)

```python
SMTPUser = ""
```
SMTP user name (optional, only set when SMTPAuth = True)

```python
SMTPPass = ""
```
SMTP password (optional, only set when SMTPAuth = True)

```python
FromAddress = "githubauditor@example.com"
```
The Address that sends the email

```python
Receivers = []
Receivers.append("example@email.com")
Receivers.append("example2@email.com")
```
Add email addresses that need to receive the email

```python
SQLFile = ""
```
The location of the Sqlite database (if it does not exists, it will be created).
On Windows escape the backslash, i.e.: c:\\\\databases\\\\multi_factor.db

```python
LDAP_REQUIRE_VALID_CERT = True
```
Your ldap/active directory server sends a certificate, this should be validated (value needs to be True or False).
It's not a good idea to turn this off, it makes your SSL/TLS connection vulnerable for MITM attacks.

```python
LDAP_CA_CERT_ISSUER = ""
```
The certificate of the certificate authority that has signed the certificate from the LDAP/Active Directory server
This needs to be a base64 encoded pem file
On Windows escape the backslash, i.e.: c:\\trusted-certs\\certificate.pem
Only used when LDAP_REQUIRE_VALID_CERT = True

```python
LDAP_HOST = ""
```
Hostname of the LDAP / Active Directory server.
i.e. ldap://ad.domain.local:389 or ldaps://ad.domain.local:636

```python
LDAP_SCHEMA_FIELD = ''
```
Name of the field that contains the Github user name, it's case sensitive.
i.e. extensionAttribute1 can be used if you don't want to change your AD schema.

```python
LDAP_USER = ""
```
Username that is going to query the LDAP / Active Directory server i.e. username@domain.local.

```python
LDAP_PASS = ""
```
Password that is used to authenticate.

```python
LDAP_DOMAIN = ""
```
Domain that is going to be queried (i.e. domain.local).

```python
LDAP_OU_LIST = []
LDAP_OU_LIST.append('MyBusiness')
```
Organisational unit(s) that will be used when searching the LDAP / Active Directory server

```python
LDAP_IGNORE_GITHUB_USERS = []
LDAP_IGNORE_GITHUB_USERS.append("ignoreuser")
```
Github user names that will be ignored if they are found while using the get_gitgub_users_from_ad.py script
```python
SEND_EMAIL_TO_USERS = False
```
Send an email with Github 2fa instructions to the user (True or False)
```python
GITHUB_INSTRUCTIONS_DOC = "c:\\docs\\multi_factor.pdf"
```
Location of the document that contains instructions to setup 2fa in Github

check_mfa.py: Using a custom email template for the users email 
===============================================================
If the configuration option SEND_EMAIL_TO_USERS = True and the GITHUB_INSTRUCTIONS_DOC setting is set, it will send an email with instructions to all the affected users.
The default email text is defined in templates/email_instructions.html. If you copy this file in templates/custom/email_instructions.html this file will be used instead.
This way it's possible to customize the text within the email.