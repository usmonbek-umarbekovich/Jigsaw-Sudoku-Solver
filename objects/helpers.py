# helpers.py

def is_valid(board, shape, num, pos):
  # check the row
  for c in range(len(board[0])):
    if pos[1] != c and board[pos[0]][c] == num:
      return False

  # check the column
  for r in range(len(board)):
    if pos[0] != r and board[r][pos[1]] == num:
      return False
    
  # check inside the shape
  for k in shape:
    if k != pos and shape[k] == num:
      return False
  
  # If it come here without returning False
  # Then it is True
  return True


def find_empty(shapes):
  for shape in shapes:
    for pos in shape:
      if shape[pos] == 0:
        return shape, pos
  return None, None


def is_solvable(shapes, board):
  shape, pos = find_empty(shapes)
  if not pos:
    return True
  else:
    row, col = pos
  for num in range(1, 10):
    if is_valid(board, shape, num, pos):
      shape[pos], board[row][col] = num, num
      
      if is_solvable(shapes, board):
        return True
      
      shape[pos], board[row][col] = 0, 0
  return False