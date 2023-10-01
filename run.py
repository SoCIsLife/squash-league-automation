#!/usr/bin/python3
import csv
import argparse
import config as cfg


def process_csv(fname):
  '''
  Processes CSV file where first line encodes columns and returns array object
  where each row is encoded as a dict.
  '''
  records = []
  with open(fname, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
      records.append(row)

  return records


def get_group_label(group_number):
  '''
  Parses global group configuration to retreive group's label.
  '''
  return [g['label'] for g in cfg.GROUP_CONFIG if g['number'] == group_number][0]


def construct_next_player_list(player_list):
  '''
  Constructs the initial next month's player objects using the results from the
  previous month.
  '''
  new_player_list = []
  for player in player_list:
    new_player_list.append({
      'points'    : int(player['points']),
      'name'      : player['name'],
      'old_group' : int(player['group']),
      'new_group' : 999,
      'action'    : None})

  return new_player_list


def sort_by_key(player_list, key, reverse=False):
  return sorted(player_list, key=lambda d: d[key], reverse=reverse)


def display_players(players):
  '''
  A debug function to printout player list object.
  '''
  for player in players:
    print('Old group: ' + str(player['old_group']) + '; ' +
          'New group: ' + str(player['new_group']) + '; ' +
          'Player: '    + player['name']           + '; ' +
          'Points: '    + str(player['points'])    + '; ' +
          'Action: '    + str(player['action']))


# argument parser
parser = argparse.ArgumentParser(
  description='Software for automating organizational tasks for small squash leagues.',
  epilog='Newest version available at: https://github.com/SoCIsLife/squash-league-automation')

parser.add_argument('-r', '--results-file',    action='store', default=cfg.PATH_RESULTS)
parser.add_argument('-a', '--applicants-file', action='store', default=cfg.PATH_APPLICATIONS)
parser.add_argument('-o', '--output-file',     action='store', default='output.txt')

args = parser.parse_args()


print('[INFO] Reading input files...')
player_results      = process_csv(args.results_file)
player_applications = process_csv(args.applicants_file)
next_month_players  = construct_next_player_list(player_results)


print('[INFO] Removing the unregistered players...')
player_index=0
while player_index < len(next_month_players):
  player_applied = False

  # find player in applications
  for application in player_applications:
    if application['name'] == next_month_players[player_index]['name']:
      player_applied = True
      break

  # remove player if haven't applied
  if not player_applied:
    next_month_players.pop(player_index)
  else:
    player_index += 1



print('[INFO] Reordering players...')
next_month_players = sort_by_key(next_month_players, 'points', True)
next_month_players = sort_by_key(next_month_players, 'old_group')


print('[INFO] Identifying players for demotion...')
player_offset = 0  # govnokods (case when group substantially reduces in size)
for group in cfg.GROUP_CONFIG:
  player_index  = player_offset
  for player in next_month_players:
    # check if player can be demoted from the particular group
    if player['old_group'] == group['number']:

      # mark player for demotion
      if player_index >= group['player_count']-2:
        player['action'] = 'demote'

      player_index += 1
      player_offset = player_index - group['player_count']
    

print('[INFO] Adding new players...')
for application in player_applications:
  player_from_previous_month = False

  # check if registered player played in the previous month
  for player in next_month_players:
    if player['name'] == application['name']:
      player_from_previous_month = True

  # add new unique player with last possible group
  if not player_from_previous_month:
    next_month_players.append({'old_group': 999, 'name': application['name'], 'points':0, 'action':None})


print('[INFO] Assigning new groups...')
for group in cfg.GROUP_CONFIG:
  group_member_index = 0
  for player in next_month_players:
    # skip players whose group is already set
    if player['action'] == 'done':
      continue

    # skip players that should be demoted
    if player['old_group'] == group['number'] and player['action'] == 'demote':
      continue

    # current player eligible for the group, update player's group number
    player['new_group'] = group['number']
    player['action'] = 'done'
    group_member_index = group_member_index + 1

    # switch to the next group
    if group_member_index >= group['player_count']:
      break


print('[INFO] Reordering groups...')
next_month_players = sort_by_key(next_month_players, 'new_group')


print('[INFO] Checking for unfilled positions...')
player_index = 0
for group in cfg.GROUP_CONFIG:
  for i in range(0, group['player_count']):
    if player_index < len(next_month_players):
      if next_month_players[player_index]['new_group'] == 999:
        next_month_players[player_index]['new_group'] = group['number']

      player_index = player_index + 1


print('[INFO] Displaying results...')
for group in cfg.GROUP_CONFIG:
  print("===== %s =====" %(group['label']))
  for player in next_month_players:
    if player['new_group'] == group['number']:
      if player['old_group'] == player['new_group']:
        print("%s" %(player['name']))
      else:
        print("%-20s (%s -> %s)" %(
          player['name'],
          get_group_label(player['old_group']),
          get_group_label(player['new_group'])))

  print('')

print('===== Izmaiņu kopsavilkums =====')
for player in next_month_players:
  if player['old_group'] != player['new_group']:
    print("%-20s pārcelts no %-6s uz %-6s (Punkti iepriekš: %d)" % (
      player['name'],
      get_group_label(player['old_group']),
      get_group_label(player['new_group']),
      player['points']))
