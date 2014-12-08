import functions
import argparse
import os
cur_path = os.getcwd()
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

parser = argparse.ArgumentParser(description='Show details Github user.')
parser.add_argument('username', metavar='<user name>', nargs=1,
                    help='Github user names that should queried')

args = parser.parse_args()

user = args.username[0]

response = functions.do_github_api_request('https://api.github.com/users/' + user)

message = response.get('message', None)
if message:
    print(message)
else:
    for key in response.keys():
        print str(key) + ": " + str(response[key])
