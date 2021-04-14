import tkinter as tk

canvas = {
  'bg': "#ffffff",
  'width': 520,
  'height': 520,
  'relief': tk.RIDGE,
  'bd': 2,
  'highlightthickness': 0
}

btn = {
  'bg': "#444444",
  'fg': "#ffffff",
  'font': "Arial 13",
  'activeforeground': "#f4f4f4",
  'activebackground': "#333333",
  'cursor': 'hand2'
}

scale = {
  'orient': 'horizontal',
  'cursor': "hand2",
  'from_': 1,
  'to': 100,
  'troughcolor': "#14fa0c",
  'showvalue': 0,
  'bg': "#0e05ad",
  'activebackground': "#0b048a",
  'borderwidth': 0,
  'sliderrelief': tk.RAISED
}

numbers = {
  'anchor': tk.CENTER,
  'font': "Arial 16"
}