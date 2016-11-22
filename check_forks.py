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

parser = argparse.ArgumentParser(description='Get all repositories and associated forks for an organisation')
parser.add_argument('--skip-sending-email', nargs='?', default=False, help='Don\'t send an email, show it instead', const=True)
args = parser.parse_args()
skip_sending_email = args.skip_sending_email

def get_repos_and_forks(public):
    if public:
        params = { "type": "public" }
    else:
        params = { "type": "private" }

    # first get all the repositories for your organization
    repos = functions.do_github_api_request('https://api.github.com/orgs/' + config.Organisation + '/repos', params)

    message = ""
    for repo in repos:
        name = repo['name']
        repo_priv = repo['private']
        repo_url = repo['html_url']
        # public repository detected
        if repo_priv == False:
            message = message + "The repository " + name + " (" + repo_url + ") is defined as a public repository.\n"
        else:
            message = message + "The repository " + name + " (" + repo_url + ") is defined as a private repository.\n"
            forks = functions.do_github_api_request('https://api.github.com/repos/' + config.Organisation + '/' + name + '/forks')
            for fork in forks:
                owner_url = fork['html_url']
                message = message + "\t\tFork: " + owner_url + "\n"

    return message

# first get all the repositories for your organization
message = "Public repositories:\n\n"
message = message + get_repos_and_forks(True) + "\n\n"
message = message + "Private repositories:\n\n"
message = message + get_repos_and_forks(False) + "\n\n"

if skip_sending_email:
    print message
else:
    functions.send_mail(config.FromAddress, config.Receivers, "Repository information for organization " + config.Organisation,
                        message, type="plain")