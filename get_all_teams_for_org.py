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

teams = functions.do_github_api_request('https://api.github.com/orgs/' + config.Organisation + '/teams')
for team in teams:
    print("id: "+ str(team['id']) + " - " + team['name'] + " - " + team['url'])
