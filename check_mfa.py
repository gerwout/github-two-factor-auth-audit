import config
import functions

if config.GitHubAuthKey == "":
    print "Please add your Github api key (Settings -> Applications -> Personal Access Tokens) to config.py\n"
    exit()
if config.Organisation == "":
    print "Please add your Github organisation (https://github.com/settings/organizations) to config.py\n"
    exit()


# get all the users that don't have 2 factor authentication enabled
json_list = functions.do_github_api_request('https://api.github.com/orgs/' + config.Organisation + '/members?filter=2fa_disabled')
users = []

for user in json_list:
    user_dict = functions.do_github_api_request(user['url'])
    users.append(user_dict)

email = functions.construct_email(users)

functions.sendemail(config.FromAddress, config.Receivers, "Github Two Factor authentication audit", email)

