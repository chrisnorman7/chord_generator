#!/usr/bin/python
from sys import argv
from string import split

config = {
"chord_name" : ",blank ,*ord ,template",
"neck_length" : 7,
"auto_size" : 0,
"show_brief" : 1,
"brief_brief" : 1,
"brief_delimiter" : "4",
"brief_seperator" : "-",
"fingers" : ["#j", "#a", "#b", "#c", "#d"],
"strings" : [";e", ";b", ";g", ";d", ";a", ";e"],
"empty_fret" : "33",
"nonempty_fret" : "_",
"normal_fret" : "=",
"pre_nonempty_fret" : "l",
"empty_string" : ";x",
"silent_string" : "==",
"input_seperator" : ".",
"linebreak" : ""
}

help_msg = "Syntax: " + argv[0] + " [--option1=value[ --option2=value2[ ...]]] [string[:fret:finger][ string[:fret:finger][ ...]]]\n\nOptions must be provided as --option=value, and for a list of all possible configuration directives with their current values, use --config.\nAll arguments must be numbers. For example 5:2:4, would place the 4th finger on the 2nd fret of the 5th string."

neck = {}

def convert_number(n):
  numbers = ["j", "a", "b", "c", "d", "e", "f", "g", "h", "i"]
  new_string = ""
  for t in str(n):
    new_string += numbers[int(t)]
  return new_string.rjust(2, "#")

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
    option = option[2:]
    if not config.has_key(option):
      quit("Invalid configuration directive: --" + option + ". See --config for a list.")
    func = type(config[option])
    if func == list:
      config[option] = split(value, ",")
    else:
      try:
        config[option] = func(value)
      except ValueError:
        quit("Invalid value for --" + option + ": " + value + ". Option expects value of " + str(type(config[option])) + ".")
    continue
  else:
    a = split(a, config["input_seperator"])
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
      quit("This instrument is only configured for " + str(len(config["strings"])) + " strings. Thus " + str(arg_string + 1) + " is out of range.")
    elif not (arg_finger in range(0, len(config["fingers"]))):
      quit("Only " + str(len(config["fingers"])) + " fingers are named. These are numbered from 0 to " + str(len(config["fingers"]) - 1) + ". " + str(arg_finger) + " is invalid.")
    elif not (arg_fret in range(0,config["neck_length"] + 1)) and not config["auto_size"]:
      quit("This instrument only has " + str(config["neck_length"]) + " frets. " + str(arg_fret) + " is out of range.")
    if not neck.has_key(arg_string):
      neck[arg_string] = {}
    if not arg_fret:
      neck[arg_string][0] = config["silent_string"]
    else:
      arg_finger = config["fingers"][arg_finger].rjust(2, "#")
      neck[arg_string][arg_fret - 1] = arg_finger
      try:
        if neck[arg_string][0] == config["empty_string"]:
          del neck[arg_string][0]
      except:
        pass

print(config["chord_name"])

if config["auto_size"]:
  config["neck_length"] = 0
  for n in neck:
    for f in neck[n].keys():
      config["neck_length"] = max(config["neck_length"], f + 1)

line = ""
if config["show_brief"]:
  for counter in range(0, len(config["strings"])):
    if not neck.has_key(counter):
      line += config["empty_string"]
    else:
      for k in neck[counter].keys():
        if neck[counter][k] == config["silent_string"]:
          line += config["silent_string"]
        else:
          line += convert_number(k + 1)
          if not config["brief_brief"]:
            line += config["brief_delimiter"] + neck[counter][k]
    line += config["brief_seperator"]
  line = line[0:-1]
print(line + config["linebreak"])

line = "  "
for r in range(1,config["neck_length"] + 1):
  line += " " + convert_number(r)
print(line)

for counter in range(0,len(config["strings"])):
  line = config["strings"][counter].rjust(2, ";").ljust(3, " ")
  for n in range(0,config["neck_length"]):
    if n == 0 and not neck.has_key(counter):
      fret = config["empty_string"]
    else:
      try:
        fret = neck[counter][n]
      except:
        fret = config["empty_fret"]
    line += fret
    if not fret in [config["empty_fret"], config["silent_string"]]:
      line += config["nonempty_fret"]
      continue
    try:
      if neck[counter][n + 1]:
        line += config["pre_nonempty_fret"]
    except:
      line += config["normal_fret"]
  print(line + config["linebreak"])
