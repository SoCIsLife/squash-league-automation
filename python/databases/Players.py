import pandas as pd
from difflib import SequenceMatcher as sm

class Players(list):
  '''
  TODO: Documentation
  '''

  def __init__(self, *args):
    if not args:
      super().__init__()
    elif isinstance(args[0], str):
      self.__init_str(args[0])
    elif isinstance(args[0], list):
      super().__init__(args[0])
    else:
      raise Exception('Unrecognized instance type')

  def __init_str(self, db_path):
    if ".ods" in db_path:
      # read and convert database to dictationary
      db = pd.read_excel(db_path, engine="odf")
      super().__init__(db.to_dict('records'))

      # construct player full names
      for player in self:
        player['fullname'] = player['name'] + ' ' + player['surname']
    else:
      raise Exception('Unrecognized database type')


  def get_player_index(self, token):
    for idx, player in enumerate(self):
      if token == player['id'] \
      or sm(None, token, player['fullname']).ratio() > 0.8 \
      or token == player['email'] \
      or token == player['phone'] \
      or sm(None, token, player['name']).ratio() > 0.8 \
      or sm(None, token, player['surname']).ratio() > 0.8:
        return idx

    return None


  def get_player(self, token):
    idx = self.get_player_index(token)
    if idx != None:
      return self[idx]

    return None


  def player_exists(self, token):
    if self.get_player(token):
      return True
    return False


  def get_fullname(self, token):
    return self.get_player(token)['fullname']


  def get_id(self, token):
    return self.get_player(token)['id']


  def get_group(self, token):
    return self.get_player(token)['group']


  def get_email(self, token):
    return self.get_player(token)['email']


  def get_phone(self, token):
    return self.get_player(token)['phone']
