import xlwt
import pandas as pd

class Centered(xlwt.Style.XFStyle):
  def __init__(self):
    super().__init__()
    self.alignment.horz = self.alignment.HORZ_CENTER


class ResultsTable(xlwt.Workbook):
  def __init__(self):
    super().__init__()

    # styles
    self.style_centered = Centered()

    self.sheet = self.add_sheet('Sheet1')
    self.sheet.set_portrait(False)
    self.sheet.fit_num_pages = 1
    self.sheet.set_header_margin(0)
    self.sheet.set_footer_margin(0)
    self.sheet.set_header_str(b"")
    self.sheet.set_footer_str(b"")
    self.sheet.set_top_margin(0.30)
    self.sheet.set_left_margin(0.30)

    self.sheet.write(0, 0, "results", style=self.style_centered)
    self.sheet.write(0, 1, "name",    style=self.style_centered)
    self.sheet.write(0, 2, "surname", style=self.style_centered)
    self.sheet.write(0, 3, "points",  style=self.style_centered)

    
  def fill_players(self, groups):
    current_row = 1
    for group in groups:
      for player in group:
        self.sheet.write(current_row, 0, player["group"], style=self.style_centered)
        self.sheet.write(current_row, 1, player["name"])
        self.sheet.write(current_row, 2, player["surname"])
        self.sheet.write(current_row, 3, "", style=self.style_centered)
        current_row += 1
