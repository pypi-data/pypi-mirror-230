"""Utilities for reading from and writing to external files."""

import json
import os
from pathlib import Path

def get_path(fname):
  return os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)


def read_file(fname):
  """Read the contents of a given file as a string.
  
  Parameters
  ----------
  fname : str

  Returns
  -------
  str
  """
  fname = get_path(fname)
  if exists(fname):
    with open(fname, 'r') as f:
      return f.read()
  else:
    return ''
  

def read_lines(fname):
  """Read the lines of a file as a list, removing whitespace lines.
  
  Parameters
  ----------
  fname : str

  Returns
  -------
  list[str]
  """
  fname = get_path(fname)
  if exists(fname):
    return [l.strip() for l in read_file(fname).split('\n') if l.strip()]
  else:
    return []
  

def write_file(fname, data):
  """Write a string to a given file.
  
  Parameters
  ----------
  fname : str
  data : str
  """
  fname = get_path(fname)
  with open(fname, 'w+') as f:
    f.write(data)


def append_file(fname, data):
  """Append a string to a given file.

  Parameters
  ----------
  fname : str
  data : str
  """
  fname = get_path(fname)
  with open(fname, 'a+') as f:
    f.write(data)
  

def load_json(fname):
  """Load data from a JSON file.
  
  Parameters
  ----------
  fname : str

  Returns
  -------
  dict
  """
  fname = get_path(fname)
  if exists(fname):
    with open(fname, 'r') as f:
      return json.load(f)
  else:
    return {}
  

def write_json(fname, data, pretty=False):
  """Write data to a JSON file.
  
  Parameters
  ----------
  fname : str
  data : dict
  pretty : bool, default=False
    Whether to pretty-print the JSON by indenting new lines.
  """
  fname = get_path(fname)
  with open(fname, 'w+') as f:
    if pretty:
      json.dump(data, f, indent=2)
    else:
      json.dump(data, f)


def clear(fname):
  """Clear the contents of a file.
  
  Parameters
  ----------
  fname : str
  """
  fname = get_path(fname)
  with open(fname, 'w+') as f:
    f.write('')


def exists(fname):
  """Check if a file exists.
  
  Parameters
  ----------
  fname : str

  Returns
  -------
  bool
  """
  fname = get_path(fname)
  return os.path.isfile(fname)


def remove(fname):
  """Remove a file if it exists.

  Parameters
  ----------
  fname : str
  """
  fname = get_path(fname)
  if exists(fname):
    os.remove(fname)


def ensure_dir_exists(dirname):
  """Ensure that a directory exists, creating it if it doesn't.
  
  Parameters
  ----------
  dirname : str
  """
  fname = get_path(fname)
  Path(dirname).mkdir(parents=True, exist_ok=True)


def ensure_file_exists(fname):
  """Ensure that a file exists, creating an empty file if it doesn't.
  
  Parameters
  ----------
  fname : str
  """
  fname = get_path(fname)
  ensure_dir_exists('/'.join(fname.split('/')[:-1]))
  clear(fname)
