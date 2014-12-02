import functions
import argparse

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
