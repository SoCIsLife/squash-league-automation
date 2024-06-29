import pandas as pd
from databases.Players import Players
from difflib import SequenceMatcher as sm

class Group(Players):
  '''
  TODO: Documentation
  '''

  def __init__(self, init_object=None):
    self.promotee_count = 0

    if init_object:
      super().__init__(init_object)
    else:
      super().__init__()


  def sort_by_key(self, key, reverse=False):
    self.sort(key=lambda d: d[key], reverse=reverse)


  def add_player(self, player, status='normal'):
    player['status'] = status
    self.append(player)


  def remove(self, token):
    idx = self.get_player_index(token)
    if idx != None:
      self.pop(idx)
    else:
      raise Exception('Could not remove player from the group')


  def set_group(self, group, start_idx=0, stop_idx=999):
    for idx in range(max(start_idx, 0), min(stop_idx+1, len(self))):
      self[idx]['group'] = group


  def subset_by_key(self, key, value, start_idx=0, stop_idx=999):
    subset_group = Group()
    for idx in range(max(start_idx, 0), min(stop_idx+1, len(self))):
      if self[idx][key] == value:
        subset_group.add_player(self[idx])

    return subset_group


  def subset_by_index(self, start_idx=0, stop_idx=999):
    subset_group = Group()
    for idx in range(max(start_idx, 0), min(stop_idx+1, len(self))):
      subset_group.add_player(self[idx])

    return subset_group
