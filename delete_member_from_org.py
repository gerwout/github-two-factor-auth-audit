import config
import functions
import argparse

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