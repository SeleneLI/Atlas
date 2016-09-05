import csv
import os
import sys
import time
from config.config import *

# AUTH = "%s/auth" % os.environ['PWD'] # put the KEY in file named 'auth' under current folder
big_csv = os.path.join(os.path.dirname(__file__), "auth")