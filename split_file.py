import os
import sys


def split_file(fname):
  f_out = None
  with open(fname) as f_in:
    event_number_prev = None

    first_line = True
    legenda = ""
    for line in f_in:
      if first_line:
        legenda = line
        first_line = False
        continue

      line = line.replace(' ', '')
      event_number = int(line.split(',')[0])

      if event_number != event_number_prev:

        if f_out is not None:
          f_out.close()

        fname_out = f"event_{event_number}_track_candidates_params.txt"
        if (os.path.exists(fname_out)):
          print(f"Warning: {fname_out} already exists! Will bee rewritten.")
        f_out = open(fname_out, 'w')
        f_out.write(legenda)

        event_number_prev = event_number

      f_out.write(line)
  f_out.close()


if len(sys.argv) != 2:
  print("Usage: script_name <fname>")
  exit()
fname = sys.argv[1]
split_file(fname)
