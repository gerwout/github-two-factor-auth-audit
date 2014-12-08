import os
import functions
import argparse

cur_path = os.getcwd()
if (os.name == 'nt'):
    path_seperatot = "\\"
else:
    path_seperatot = "/"

if os.path.isfile(cur_path + path_seperatot + 'local_config.py'):
    import local_config as config
else:
    import config

if config.GitHubAuthKey == "":
    print "Please add your Github api key (Settings -> Applications -> Personal Access Tokens) to config.py\n"
    exit()
if config.Organisation == "":
    print "Please add your Github organisation (https://github.com/settings/organizations) to config.py\n"
    exit()

parser = argparse.ArgumentParser(description='Add github user to a team within an organisation.')
parser.add_argument('usernames', metavar='<user name>', nargs='*',
                    help='1 or more Github user names that should be added')

args = parser.parse_args()

users = args.usernames
count = len(users)
if (count == 0):
    parser.print_help()
else:
    if not config.DefaultTeamId:
        print "Please setup a default team in config.py!"
        exit()
    for user in users:
        response = functions.do_github_api_request('https://api.github.com/teams/' + str(config.DefaultTeamId)
                                        + '/memberships/' + user, method='put')
        message = response.get('message', None)
        if message:
            print(message)
            print("Do you have the admin:org scope enabled?")
            exit()
        else:
            state = response.get('state', None)
            if state == "pending":
                print(user + " added, awaiting confirmation from the user!")
            elif state == "active":
                print(user + " is already a member!")