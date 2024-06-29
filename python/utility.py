#!/usr/bin/python3
import argparse
import locale
import config as cfg
import pandas as pd
from databases.Players    import Players
from databases.Results    import Results
from databases.Applicants import Applicants
from gamelogic.Group      import Group
from documents.ResultsTable import ResultsTable

# set locale to latvian
locale.setlocale(locale.LC_ALL, 'lv_LV.UTF-8')


# argument parser
parser = argparse.ArgumentParser(
  description='Tool for automating organizational tasks for small competitive leagues.',
  epilog='Newest version available at: https://github.com/SoCIsLife/squash-league-automation')

parser.add_argument('-p', '--player-db',        action='store', default='../db/players.ods')
parser.add_argument('-r', '--result-db',        action='store', default=None)
parser.add_argument('-a', '--applicant-db',     action='store', default=None)
parser.add_argument('-t', '--template-results', action='store', default=None)


# TODO: use/generate default arguments
args = parser.parse_args()


# generate default arguments depending on date
this_month = pd.to_datetime('today')
next_month = this_month + pd.offsets.MonthBegin(1)

if not args.result_db:
  args.result_db = '../db/' +  f"{this_month.year:04}" + '/'  + f"{this_month.month:02}" + '/results.ods'
if not args.applicant_db:
  args.applicant_db = '../db/' +  f"{next_month.year:04}" + '/'  + f"{next_month.month:02}" + '/applicants.ods'
if not args.template_results:
  args.template_results = '../db/' +  f"{next_month.year:04}" + '/'  + f"{next_month.month:02}" + '/results.ods'


# construct database objects
player_db    = Players(args.player_db)
result_db    = Results(args.result_db,       player_db)
applicant_db = Applicants(args.applicant_db, player_db)


# retreive initial groups from the results
groups = result_db.construct_groups()

players_added   = []
players_removed = []

# add another group for left-over players
group_leftover = Group()
for player in applicant_db:
  if not result_db.player_exists(player['fullname']):
    player['old_group']  = 999
    player['group']  = 999
    player['points'] = 0
    group_leftover.add_player(player)
    #print('New player added: ' + player['fullname'])
    players_added.append(player)

groups.append(group_leftover)


# remove players that have not applied
for group in groups:
  for player in group:
    if not applicant_db.player_exists(player['fullname']):
      group.remove(player['fullname'])
      players_removed.append(player)


# update groups given promotion/demotion info
for i in range(0, len(groups)):
  groups[i].sort_by_key('points', True)

  if i != 0:
    groups[i].set_group(
      i-1,                           # group to promote to
      0,                             # starting index
      0+cfg.PROMOTIONS-1)            # stop index

  if i != len(groups)-1:
    groups[i].set_group(
      i+1,                           # group to demote to
      max(cfg.GROUPS[i]['player_count'], len(groups[i]))-cfg.PROMOTIONS, # starting index
      max(cfg.GROUPS[i]['player_count'], len(groups[i]))-1)              # stop index

# create unified group for promotion/demotion logic
unified_group = Group()
for group in groups:
  for player in group:
    unified_group.add_player(player)


# check if there are forced conversions
for p in unified_group:
  if 'group_override' in p and not pd.isna(p['group_override']):
    p['group'] = p['group_override']

unified_group.sort_by_key('group')

# retreive group subset given the number of players
new_groups = []
idx_current = 0
for g_idx,g in enumerate(cfg.GROUPS):
  group = unified_group.subset_by_index(idx_current, idx_current+g['player_count']-1)

  # consistency check for group numbering
  for p in group:
    p['group'] = g_idx

  idx_current += g['player_count']
  new_groups.append(group)


# generate output for the chat
print('Saraksti nākošajam mēnesim: ' + next_month.month_name(locale='lv_LV.UTF-8'))

for idx,c in enumerate(cfg.GROUPS):
  group = new_groups[idx]
  print("===== %s (%d) =====" %(c['label'], len(group)))
  for player in group:
    if player['group'] == player['old_group']:
      print("%s" %(player['fullname']))
    elif player['old_group'] == 999:
      print("%-20s (%s -> %s)" %(
        player['fullname'],
        "Gaidās",
        cfg.GROUPS[player['group']]['label']))
    elif 'reasoning' in player and player['reasoning']:
      print("%-20s (%s -> %s, %s)" %(
        player['fullname'],
        "Gaidās",
        cfg.GROUPS[player['group']]['label'],
        player['reasoning']))
    else:
      print("%-20s (%s -> %s)" %(
        player['fullname'],
        cfg.GROUPS[player['old_group']]['label'],
        cfg.GROUPS[player['group']]['label']))
    
print('')
print('===== Izmaiņu kopsavilkums =====')
for idx,c in enumerate(cfg.GROUPS):
  group = new_groups[idx]
  for player in group:
    if player['old_group'] != player['group']:
      if player['old_group'] == 999:
        print("%-20s pārcelts no %-2s uz %-2s" % (
          player['fullname'],
          "Gaidās",
          cfg.GROUPS[player['group']]['label']))
      else:
        print("%-20s pārcelts no %-2s uz %-2s (Punkti iepriekš: %d)" % (
          player['fullname'],
          cfg.GROUPS[player['old_group']]['label'],
          cfg.GROUPS[player['group']]['label'],
          player['points']))

print('')
print('===== Izkrīt / Nepieteicās =====')
for player in players_removed:
    print("%-20s" % (player['fullname']))


# create results table template for the next month
doc_results = ResultsTable()
doc_results.fill_players(new_groups)
doc_results.save(args.template_results)
