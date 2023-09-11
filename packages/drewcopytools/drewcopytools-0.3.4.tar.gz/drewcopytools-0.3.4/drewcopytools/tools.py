# General tool type functions.
import subprocess
import logging
import logging

# -----------------------------------------------------------------------------
# Simple function to get the correct name of a program, depending on the current platform.
# this will pretty much add/remove the .exe extension of a program name as needed depending if
# you are on window/linux, etc.
def translate_exe_name(exeName:str):
  from sys import platform

  EXE_EXT = ".exe"
  res = exeName
  if platform == 'darwin' or platform == 'linux':
    if res.endswith(EXE_EXT):
      l = len(res)
      res = res[:l-len(EXE_EXT)]

  elif platform == 'win32':
    if not res.endswith(EXE_EXT):
      res = res + EXE_EXT

  else:
    raise Exception(f"unknown/unsupported platform: '{platform}'!")
  
  return res


# -----------------------------------------------------------------------------
# This function is meant to take a command line as a single string, and split it
# into an array so that it can be used in subprocess.call.
def split_cmdline_args(input:str):
  res = []
  parts = input.split(' ')

  buffer = ''
  inQuotes = False

  for p in parts:
    bufferComplete = False

    if inQuotes:
      buffer += " " + p
      if buffer.endswith("\""):
        buffer = buffer[:-1]
        inQuotes = False
        bufferComplete = True
    else:
      buffer += p
      if buffer.startswith("\""):
        if buffer.endswith("\""):
          buffer = buffer[1:-1]
          bufferComplete = True
        else:
          inQuotes = True
          buffer = buffer[1:]
      else:
        bufferComplete = True

    if bufferComplete:
      res.append(buffer)
      buffer = ''

  return res

# ------------------------------------------------------------------------------------------------------------------------
# Calls a subprocess from a string in a cross-platform way.
# No more guessing what the right approach is.
def subprocess_really(exe:str):
  logging.debug(f'CALL:{exe}')

  if isinstance(exe, str):
    exe = split_cmdline_args(exe)

  callres = subprocess.call(exe)
  if callres != 0:
    logging.debug("CALL FAILED!")
    return False
  return True

# ----------------------------------------------------------------------------------------------------------
def translate_url_to_filename(url):
    """ Translates a URL to a safe file name. """    
    import re
    res = re.sub(r'http(s)?://', '', url)
    res = res.replace('/', '_')
    res = res.replace('?', 'qs_')
    return res
