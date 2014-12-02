github-two-factor-auth-audit
============================
A bunch off Python scripts that you can use to audit if every GIT user within your organization has two factor authentication enabled.

**check_mfa.py**    
Configurable python script that checks 2fa for every Github user in your organization.
It will create an overview of all the users that haven't enabled 2 factor authentication.
It will send this overview to predefined email addresses.

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