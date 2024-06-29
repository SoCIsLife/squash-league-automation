import pandas as pd
from databases.Players import Players
from gamelogic.Group import Group
from difflib import SequenceMatcher as sm

class Results(Players):
  '''
  TODO: Documentation
  '''

  def __init__(self, db_path, db_players):
    if ".ods" in db_path:
      self._parse_db_ods(db_path, db_players)
    else:
      raise Exception('Unrecognized database type')


  def _parse_db_ods(self, db_path, db_players):
    # read and convert database to dictationary
    db = pd.read_excel(db_path, engine="odf")
    super().__init__(db.to_dict('records'))

    # construct player full names
    for player in self:
      player['fullname'] = player['name'] + ' ' + player['surname']

    # update player info using player database
    for idx, player in enumerate(self):
      player_updated = db_players.get_player(player['fullname'])
      if not player_updated:
        raise Exception(player['fullname'] + ' player not in the player database, please update it')
      else:
        group     = player['group']
        points    = player['points']
        self[idx] = player_updated
        self[idx]['group']     = group
        self[idx]['old_group'] = group
        self[idx]['points']    = points


  def construct_group(self, group_idx):
    group = Group()
    for p in self:
      if p['group'] == group_idx:
        group.add_player(p)

    return group


  def construct_groups(self):
    # collect unique 'group' values
    groups = []
    unique_groups = {player['group'] for player in self}

    # for each 'group' value construct a group
    for g in unique_groups:
      group = self.construct_group(g)
      groups.append(group)

    return groups
