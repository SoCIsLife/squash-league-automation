import pandas as pd
from databases.Players import Players
from difflib import SequenceMatcher as sm

class Applicants(Players):
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

    # update player info using player database
    for idx, applicant in enumerate(self):
      player_updated = db_players.get_player(applicant['fullname'])
      if not player_updated:
        raise Exception(applicant['fullname'] + ' player not in the player database, please update it')
      else:
        group_override = applicant['group_override']
        reasoning      = applicant['reasoning']
        self[idx] = player_updated
        if not pd.isna(group_override):
          self[idx]['group_override'] = int(group_override)
          self[idx]['reasoning']      = reasoning
