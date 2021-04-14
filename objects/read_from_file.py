# read_from_file.py

__all__ = ('raw_boards', 'regular_board')


def raw_boards(filename):
  all_puzzles = []
  with open(filename) as file:
    while True:
      try:
        shapes = []
        while len(shapes) != 9:
          raw_shape = next(file).strip('\n;, ')
          if raw_shape:
            shapes.append(parse_line(raw_shape))
        if len(shapes) != 9:
          raise ValueError("""There is an incomplete board or document is empty""")
        all_puzzles.append(shapes)
      except StopIteration:
        break
  return all_puzzles


def parse_line(raw_shape):
  shape = {}
  for item in raw_shape.split():
    r, c = int(item[0])-1, int(item[1])-1
    shape[(r, c)] = int(item[3])
    
  if len(shape) != 9:
    raise ValueError("Incomplete row!")
  return shape


def regular_board(shapes):
  """
  Turn list of dictionaries into list of lists
  """
  board = [[0]*9 for _ in range(9)]
  for shape in shapes:
    for r, c in shape:
      board[r][c] = shape[(r, c)]
  return board
