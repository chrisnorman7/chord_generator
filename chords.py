#!/usr/bin/python
from sys import argv
from string import split

config = {
"chord_name" : ",blank ,*ord ,template",
"neck_length" : 7,
"fingers" : ["#j", "#a", "#b", "#c", "#d"],
"strings" : [";e", ";b", ";g", ";d", ";a", ";e"],
"empty_fret" : "33",
"nonempty_fret" : "_",
"normal_fret" : "=",
"pre_nonempty_fret" : "l",
"empty_string" : ";x",
"silent_string" : "=="
}

help_msg = "Syntax: " + argv[0] + " [--option1=value[ --option2=value2[ ...]]] [string[:fret:finger][ string[:fret:finger][ ...]]]\n\nOptions must be provided as --option=value, and for a list of all possible configuration directives with their current values, use --config.\nAll arguments must be numbers. For example 5:2:4, would place the 4th finger on the 2nd fret of the 5th string."

neck = []
for string in config["strings"]:
  actual_string = []
  for r in range(0,config["neck_length"]):
    actual_string.append("")
  actual_string[0] = config["empty_string"]
  neck.append(actual_string)

def convert_number(n):
  numbers = ["j", "a", "b", "c", "d", "e", "f", "g", "h", "i"]
  new_string = ""
  for t in str(n):
    new_string += numbers[int(t)]
  return new_string

for a in argv[1:]:
  if a == "-H" or a == "--help":
    quit(help_msg)
  elif a == "--config":
    for k in config.keys():
      if type(config[k]) == list:
        actual_string = ""
        for v in config[k]:
          actual_string += v + ", "
          actual_string = actual_string[0:-1]
      else:
        actual_string = str(config[k])
      print(k + "=" + actual_string)
    quit()
  elif a.startswith("--"):
    a = a.split("=")
    if len(a) != 2:
      quit("Configuration options must be passed with --option=value.")
    [option, value] = a
    option = option.strip("--")
    if not option in config.keys():
      quit("Invalid configuration directive: --" + option + ".")
    func = type(config[option])
    if func == list:
      config[option] = split(value, ",")
    else:
      config[option] = func(value)
    continue
  else:
    a = split(a, ":")
    for r in range(0,len(a)):
      try:
        a[r] = int(a[r])
      except ValueError:
        quit(help_msg)
    if len(a) == 3:
      [arg_string, arg_fret, arg_finger] = a
    elif len(a) == 1:
      [arg_string, arg_fret, arg_finger] = [a[0], 0, 0]
    else:
      quit(help_msg)
    arg_string -= 1
    if not (arg_string in range(0,len(config["strings"]))):
      arg_string += 1
      quit("This instrument is only configured for " + str(len(config["strings"])) + " strings. Thus " + str(arg_string) + " is out of range.")
    elif not (arg_finger in range(0, len(config["fingers"]))):
      quit("Only " + str(len(config["fingers"])) + " fingers are named. These are numbered from 0 to " + str(len(config["fingers"]) - 1) + ". " + str(arg_finger) + " is invalid.")
    elif not (arg_fret in range(0,config["neck_length"] + 1)):
      quit("This instrument only has " + str(config["neck_length"]) + " frets. " + str(arg_fret) + " is out of range.")
    if not arg_fret:
      neck[arg_string][1] = config["silent_string"]
    else:
      arg_finger = config["fingers"][arg_finger]
      if len(arg_finger) == 1:
        arg_finger = "#" + arg_finger
      neck[arg_string][arg_fret - 1] = arg_finger
      if neck[arg_string][0] == config["empty_string"]:
        neck[arg_string][0] = ""

print (config["chord_name"] + "\n")

line = "  "
for r in range(1,config["neck_length"] + 1):
  number = convert_number(r)
  if len(number) == 1:
    number = "#" + number
  line += " " + number
print(line)

counter = 0
for n in neck:
  line = config["strings"][counter] + " "
  counter += 1
  for r in range(0, len(n)):
    fret = n[r]
    if not fret:
      line += config["empty_fret"]
      if r < len(n) - 1 and n[r + 1]:
        line += config["pre_nonempty_fret"]
      else:
        line += config["normal_fret"]
    else:
      line += fret
      if fret == config["silent_string"]:
        line += config["normal_fret"]
      else:
        line += config["nonempty_fret"]
  print(line)
