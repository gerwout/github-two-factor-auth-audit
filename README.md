github-two-factor-auth-audit
============================

Configurable python script that checks 2fa for every Github user in your organisation.
It will create an overview of all the users that haven't enabled 2 factor authentication.
It will send this overview to predefined email addresses.

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
- Install the requirements (i.e. pip install -r requirements.txt)
- Configure the script (i.e. edit config.py)
- You can now run python check_mfa.py

Configuration
=============
All the configuration settings are deined in the config.py file.

GitHubAuthKey = "<oauth token>"
A Github personal access token is needed to be able to query the Github api.
Logon to Github and navigate to settings -> applications -> personal access tokens to generate one.
The read:org scope is needed for this script to function properly.

SMTPServer = "<127.0.0.1:25>"
Mail server that will send the email

SMTPAuth = False
Do you need to authenticate on the smtp server?

SMTPUser = "<user name>"
SMTP user name (optional, only set when SMTPAuth = True)

SMTPPass = "<password>"
SMTP password (optional, only set when SMTPAuth = True)

FromAddress = "githubauditor@example.com"
The Address that sends the email

Receivers = []
Receivers.append("example@email.com")
Receivers.append("example2@email.com")
Add email addresses that need to receive the email


