#!/usr/bin/python3
import base64
import datetime
import json
import sys
import uuid

from random import choice, randint

TEAM_COUNT = 1
CHANNELS_PER_TEAM = 1
USER_COUNT = 5
TEAMS_PER_USER = 1
CHANNELS_PER_USER_PER_TEAM = 1
POSTS = 10000

RESERVED_TEAM_NAMES = [
    "signup",
    "login",
    "admin",
    "channel",
    "post",
    "api",
    "oauth",
]

def generate_identifier():
    return base64.b32encode(uuid.uuid4().bytes).decode('ascii').strip('=').lower()

def get_millis():
    return int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)

word_file = "/usr/share/dict/words"
WORDS = open(word_file).read().splitlines()

def random_message():
    return " ".join([choice(WORDS) for i in range(0, 10)])


output_file = sys.argv[1]
f = open(output_file, 'w')


# Write the data schema version header.
f.write('{"type": "version", "version": 1}\n')

# Generate some teams.
teams = []
for i in range(0,TEAM_COUNT):
    team = {}
    
    while True:
        team['name'] = generate_identifier()
        reserved = False
        for res in RESERVED_TEAM_NAMES:
            if team['name'].startswith(res):
                reserved = True
                break
        if not reserved:
            break

    print("Generating Team: {}".format(team['name']))
    team['display_name'] = generate_identifier()
    team['type'] = 'O'
    team['allow_open_invite'] = True
    teams.append(team)

# Write teams.
for team in teams:
    data = {
            'type': 'team',
            'team': team,
    }
    f.write(json.dumps(data)+"\n")

# Generate channels.
channels = []
channels_by_team = {}
for team in teams:
    for i in range(0, CHANNELS_PER_TEAM):
        channel = {}

        channel['team'] = team['name']
        channel['name'] = generate_identifier()
        channel['display_name'] = generate_identifier()
        channel['type'] = 'P' if randint(0,9) == 1 else 'O'
        print("Generating Channel: {}".format(channel['name']))

        channels.append(channel)
        if team["name"] not in channels_by_team:
            channels_by_team[team["name"]] = []
        channels_by_team[team["name"]].append(channel)

# Write channels.
for channel in channels:
    data = {
            'type': 'channel',
            'channel': channel,
    }
    f.write(json.dumps(data)+"\n")

# Generate Users.
users = []
for i in range(0, USER_COUNT):
    user = {}

    user['username'] = generate_identifier()
    user['email'] = generate_identifier() + "@example.com"
    user['teams'] = []
    print("Generating User: {}".format(user['username']))

    already_done_teams = []
    for i in range(0, TEAMS_PER_USER):
        while True:
            team = teams[randint(0, TEAM_COUNT-1)]
            if team["name"] not in already_done_teams:
                already_done_teams.append(team["name"])
                break

        team_membership = {
            "name": team["name"],
            "channels": [],
        }

        already_done_channels = []
        for j in range(0, CHANNELS_PER_USER_PER_TEAM):
            while True:
                channel = channels_by_team[team["name"]][randint(0, CHANNELS_PER_TEAM-1)]
                if channel["name"] not in already_done_channels:
                    already_done_channels.append(channel["name"])
                    break

            team_membership["channels"].append({
                "name": channel["name"],
            })

        user['teams'].append(team_membership)

    users.append(user)

# Write Users.
for user in users:
    data = {
            'type': 'user',
            'user': user,
    }
    f.write(json.dumps(data)+"\n")

posts = []
for i in range(0, POSTS):
    post = {}

    post['team'] = teams[randint(0, TEAM_COUNT-1)]["name"]
    post['channel'] = channels_by_team[post['team']][randint(0, len(channels_by_team[post['team']])-1)]["name"]
    post['user'] = users[randint(0, USER_COUNT-1)]["username"]

    START_WINDOW = get_millis() - 10000 * 3 * POSTS
    END_WINDOW = get_millis()

    post['create_at'] = randint(START_WINDOW, END_WINDOW)
    post['message'] = random_message()

    posts.append(post)

# Write posts.
for post in posts:
    data = {
            'type': 'post',
            'post': post,
    }
    f.write(json.dumps(data)+"\n")

f.close()


