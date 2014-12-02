import config
import functions

teams = functions.do_github_api_request('https://api.github.com/orgs/' + config.Organisation + '/teams')
for team in teams:
    print("id: "+ str(team['id']) + " - " + team['name'] + " - " + team['url'])
