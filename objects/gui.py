# gui.py

import tkinter as tk
import pathlib as path

from tkinter import messagebox as msg
from tkinter import filedialog as fd
from time import sleep, perf_counter
from string import ascii_letters
from copy import deepcopy
from .read_from_file import *
from . import style
from . import helpers


class Sudoku:
  def __init__(self):
    self.window = tk.Tk()
    self.window.title("Sudoku Solver")
    self.window.protocol("WM_DELETE_WINDOW", self.kill_window)
    self.window.geometry("550x620")
    self.window.resizable(False, False)
    self.elapsed_time = 0
    self.is_operating = True
    self.initialdir = "/"
    self.raw_boards = None      # list of boards
    self.shapes = None          # list of dictionaries that hold shapes
    self.board = None           # regular board
    self.boards = []            # list of regular boards
    self.board_options = None   # list of board names
    self.text_ids = [[0]*9 for _ in range(9)]   # ids of canvas text that holds numbers
    self.shape_line_id = []     # list of line ids of shape edges
    self.unsolvable = set()     # set that holds unsolvable puzzles
    
    # sudoku icon
    # make the path accessible for all operation systems
    BASE_DIR = path.Path(__file__).resolve().parent.parent
    IMG_DIR = path.PurePath(BASE_DIR, "resources", "sudoku.ico")
    self.window.iconbitmap(IMG_DIR)
    
    # menubar
    menubar = tk.Menu(self.window)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Open file", command=self.open_file)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=self.kill_window)
    menubar.add_cascade(label="File", menu=filemenu)
    self.window.config(menu=menubar)

    # canvas
    self.canvas = tk.Canvas(self.window, **style.canvas)
    self.canvas.pack(side=tk.TOP, fill=tk.BOTH)
    self.canvas.update()
    self.width = self.canvas.winfo_width()
    self.height = self.canvas.winfo_height()
    self.step_x, self.step_y = self.width/9, self.height/9

    frame = tk.Frame(self.window, bg="#f4f4f4")
    frame.pack(side=tk.TOP)
    
    # reset button
    self.reset_button = tk.Button(frame, text="Reset", command=self.reset, **style.btn)
    self.reset_button.grid(ipadx=20, pady=6, row=0, column=0)
    self.button_hover(self.reset_button)
    
    # solve button
    self.solve_button = tk.Button(frame, text="Solve", command=self.solve, **style.btn)
    self.solve_button.grid(ipadx=20, padx=34, pady=6, row=0, column=1)
    self.button_hover(self.solve_button)
    
    # menubutton that holds the list of boards
    self.option_value = tk.StringVar()
    self.current_board = tk.Menubutton(frame, textvariable=self.option_value, **style.btn)
    self.current_board.menu = tk.Menu(self.current_board, tearoff=0)
    self.current_board["menu"] = self.current_board.menu
    self.current_board.grid(ipadx=20, ipady=2, pady=6, row=0, column=2)
    self.option_value.set("No Board")
    
    # scale bar for manipulating speed
    var = tk.DoubleVar()
    self.speed = tk.Scale(frame, variable=var, **style.scale)
    self.speed.grid(ipadx=80, row=1, column=0, columnspan=2)
    self.speed.set(50)

    # label that holds timing information
    tk.Label(frame, text="Runtime:", font="Arial 13").grid(row=1, column=2)
    self.runtime = tk.Label(frame, text='00:00', font="Arial 13")
    self.runtime.grid(row=1, column=3)

    self.draw_lines()

    self.window.mainloop()
    

  def kill_window(self):
    self.window.destroy()
    
    
  def on_enter(self, event, btn):
    btn['background'] = '#333333'


  def on_leave(self, event, btn):
    btn['background'] = '#444444'
  
  
  def button_hover(self, button):
    button.bind("<Enter>", lambda event, btn=button: self.on_enter(event, btn))
    button.bind("<Leave>", lambda event, btn=button: self.on_leave(event, btn))

  
  def draw_lines(self):
    """
    This method draws the x and y lines in the canvas
    """
    # draw x lines
    y = self.step_y
    while y <= self.height:
      x = 0
      while x <= self.width:
        self.canvas.create_line(x, y, x+3.5, y)
        self.canvas.update()
        x += 3.5
      y += self.step_y
    
    # draw y lines
    x = self.step_x
    while x <= self.width:
      y = 0
      while y <= self.height:
        self.canvas.create_line(x, y, x, y+3.5)
        self.canvas.update()
        y += 3.5
      x += self.step_x
    
    self.is_operating = False
    
  
  def open_file(self):
    if not self.is_operating:
      self.is_operating = True
      
      # delete previous menu commands if there is any
      if self.option_value.get() != "No Board":
        for board_name in self.board_options:
          self.current_board.menu.delete(board_name)
      
      # clear unsolvable set
      self.unsolvable.clear()
          
      filetypes = [
        ('Text files', '*.txt'),
        ('All types', '.')
      ]
      try:
        filename = fd.askopenfilename(initialdir=self.initialdir,
                                      filetypes=filetypes)
        # get the directory path of filename
        self.initialdir = filename.rstrip(ascii_letters+'.')
        
        self.raw_boards = raw_boards(filename)
        for raw_board in self.raw_boards:
          self.boards.append(regular_board(raw_board))
          
      except Exception as error:
        msg.showerror("Error", str(error))
        self.is_operating = False
        
      else:
        self.board_options = [f"Board {i+1}" for i in range(len(self.raw_boards))]
        self.option_value.set(self.board_options[0])
        for id in range(len(self.board_options)):
          self.current_board.menu.add_command(label=self.board_options[id],
                                              font="Arial 13",
                                              command=lambda id=id: self.change_board(id))
        self.is_operating = False
        self.draw_given_shapes(0)
    else:
      msg.showinfo("Wait", "Please wait until other operation is done")
    
  
  def draw_given_shapes(self, id):
    if id in self.unsolvable:
      msg.showerror("Unsolvable", "Given puzzle cannot be solved")
    
    elif helpers.is_solvable(deepcopy(self.raw_boards[id]), deepcopy(self.boards[id])):
      self.reset()
      self.shapes = self.raw_boards[id]
      self.board = self.boards[id]
      self.is_operating = True
      self.draw_shapes()
      self.write_given_numbers()
    
    else:
      msg.showerror("Unsolvable", "Given puzzle cannot be solved")
      self.unsolvable.add(id)
    self.is_operating = False
    
    
  def change_board(self, id):
    if not self.is_operating:
      if (not(self.shapes or self.board) or 
          self.option_value.get() != self.board_options[id]):

        self.option_value.set(self.board_options[id])
        self.draw_given_shapes(id)
      
      
  def draw_shapes(self):
    def _recursion(x0, y0, x1, y1):
      if not not_visited:
        return None
      not_visited.discard((x0, y0, x1, y1))
      
      # check neighbors and decide to which one we can move next
      neighbors_0 = [(x0, y0, x0-1, y0), (x0, y0, x0, y0-1),
                     (x0, y0, x0+1, y0), (x0, y0, x0, y0+1)]
      neighbors_1 = [(x1, y1, x1-1, y1), (x1, y1, x1, y1-1),
                     (x1, y1, x1+1, y1), (x1, y1, x1, y1+1)]
      for x2, y2, x3, y3 in neighbors_0+neighbors_1:
        if (x2, y2, x3, y3) in not_visited:
          id = self.canvas.create_line(x0*self.step_x, y0*self.step_y,
                                       x1*self.step_x, y1*self.step_y, width=3)
          self.shape_line_id.append(id)
          sleep(0.02)
          self.canvas.update()
          _recursion(x2, y2, x3, y3)
        
    # get the coordinates of the shapes edges path
    not_visited = self.box_line_coords()
    
    # pop random point and add it to keep the recurion consistent
    x0, y0, x1, y1 = not_visited.pop()
    not_visited.add((x0, y0, x1, y1))
    _recursion(x0, y0, x1, y1)
  
  
  def box_line_coords(self):
    """
    Get the coordinates of the lines that build shapes
    """
    not_visited = set()
    for shape in self.shapes:
      for r, c in shape:
        # get points next to the numbers in one shape
        # and check which of them are inside the same shape too
        neighbors = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
        for next_r, next_c in neighbors:
          if (0 <= next_r < 9 and 0 <= next_c < 9 and
              (next_r, next_c) not in shape):
            
            # maximum of the point and its neighbor will be
            # the beginning of the line part that builds shape 
            x0, y0 = max(next_c, c), max(next_r, r)
            x1 = (next_c == c) and c + 1 or x0
            y1 = (next_r == r) and r + 1 or y0
            not_visited.add((x0, y0, x1, y1))
            not_visited.add((x1, y1, x0, y0))
    return not_visited
  
  
  def write_given_numbers(self):
    """
    This method writes given numbers, to solve sudoku, to entries
    """
    y = self.step_y/2 
    while y < self.height:
      x = self.step_x/2
      while x < self.width:

        # find row and column of the board based on the step sizes
        r, c = round((y-self.step_y/2)/self.step_y), round((x-self.step_x/2)/self.step_x)
        number = self.board[r][c] or ''
        self.text_ids[r][c] = self.canvas.create_text(x, y, text=str(number), **style.numbers)
        sleep(0.05)
        self.canvas.update()
        x += self.step_x
      y += self.step_y


  def solve(self):
    # wait untill other functions finish operating,
    # check if the board is not empty
    if not self.is_operating and self.shapes and self.board:
      self.is_operating = True
      shapes = deepcopy(self.shapes)
      board = deepcopy(self.board)
      
      # start timing
      start = perf_counter()
      self.elapsed_time = 0
      
      # additional function to implement backtracking
      # and also to be able to time the solution
      def _recursive():
        self.elapsed_time = int(perf_counter() - start)
        self.runtime['text'] = f'{self.elapsed_time//60:02d}:{self.elapsed_time%60:02d}'
        shape, pos = helpers.find_empty(shapes)
        if not pos:
          return True
        else:
          row, col = pos
        
        for num in range(1, 10):
          shape[pos], board[row][col] = num, num
          self.canvas.itemconfigure(self.text_ids[row][col], text=str(num))
          sleep(6 / self.speed.get())
          if helpers.is_valid(board, shape, num, pos):

            # assign this number and check next entries
            self.canvas.update()

            if _recursive():
              return True
            
            # _recursive is False, then backtrack and try again
            shape[pos], board[row][col] = 0, 0
            self.canvas.itemconfigure(self.text_ids[row][col], text='')
            sleep(6 / self.speed.get())
            self.canvas.update()
            
        # all numbers checked, Sudoku can't be solved
        return False
      
      _recursive()
      self.is_operating = False
    elif not(self.shapes or self.board):
      msg.showerror("Empty Board", "Board is clear. Please select a board or open a new file")
    
    
  def reset(self):
    if not self.is_operating and self.board and self.shapes:
      self.is_operating = True
      
      self.elapsed_time = 0
      self.board = None
      self.shapes = None
      self.runtime['text'] = '00:00'
      for r in range(9):
        for c in range(9):
          self.canvas.itemconfigure(self.text_ids[r][c], text='')
          sleep(0.02)
          self.canvas.update()
      
      # clear the shape lines
      for id in self.shape_line_id:
        self.canvas.delete(id)
        # self.shape_line_id.remove(id)
        sleep(0.02)
        self.canvas.update()
      self.shape_line_id.clear()
        
      self.is_operating = False
