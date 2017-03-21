#!/usr/bin/python3

import json, requests, time

# this function will download tweets using the twitter API
# screen_name is user ID
# since_id is the most recent tweet that was downloaded. Twitter will serve the tweets that were created after since_id
def tweets(token, screen_name, since_id):
  url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
  params = {'screen_name':screen_name,'since_id':since_id,'trim_user':'true','exclude_replies':'false','include_rts':'true'}
  headers = {'Authorization': 'Bearer ' + token}
  try:
    while True:
      r = requests.get(url, params=params, headers=headers)
      if r.status_code == 429:
        time.sleep(120)
        continue
      if r.status_code != 200:
        print(r.text)
        return None
      return json.loads(r.text)
  except Exception as e:
    print('[ERR] {0}'.format(e))
    return None

# load token
with open('../config/token.json', 'r') as file:
  token = json.load(file)
token = token['token']

# load list of users information (sceen_name and since_id)
# since_id is the most recent tweet that was downloaded for the user under consideration
# when we provide since_id to twitter API, we're only served tweets that came after
with open('../config/users.json', 'r') as file:
  users = json.load(file)

for user in users:
  # use the function defined above to download tweets
  remote_tweets = tweets(token, user['screen_name'], user['since_id'])

  if remote_tweets is not None:
    print('downloaded {} tweet(s)'.format(len(remote_tweets)))

  # retrieve new since_id
  since_id = user['since_id']
  for remote_tweet in remote_tweets:
    if remote_tweet['id_str'] > since_id:
      since_id = remote_tweet['id_str']

  # update since_id
  user['since_id'] = since_id

  # load, for the user in this loop, the tweets that were downloaded before
  with open('../data/{}.json'.format(user['screen_name']), 'r') as file:
    local_tweets = json.load(file)

  # add downloaded tweets to list of existing tweets before persisting them back to file
  local_tweets.extend(remote_tweets)

  # persist to disk
  with open('../data/{}.json'.format(user['screen_name']), 'w') as file:
    json.dump(local_tweets, file, sort_keys=True)

# save all users (because we updated their since_id)
with open('../config/users.json', 'w') as file:
  json.dump(users, file, sort_keys=True)

