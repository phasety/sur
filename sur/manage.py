#!/usr/bin/env python
import sys
import sur # NOQA

if __name__ == "__main__":
  # sur.setup_as_lib()
  from django.core.management import execute_from_command_line
  execute_from_command_line(sys.argv)