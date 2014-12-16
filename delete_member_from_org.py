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

parser = argparse.ArgumentParser(description='Delete github user from an organisation.')
parser.add_argument('username', metavar='<user name>', nargs=1,
                    help='Github user name that should be removed from the organization ' + config.Organisation)

args = parser.parse_args()

user = args.username[0]

response = functions.do_github_api_request('https://api.github.com/orgs/' + config.Organisation + '/members/' + user,
                                           method='delete')

try:
    message = response.get('message', None)
    print(message)
except:
    response_code, result = response
    if (response_code == 204):
        print("User: " + user + " has been removed from the organization: " + config.Organisation)