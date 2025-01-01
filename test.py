import re

invalid_chars = r'[\\/*?"<>|,#:;[\]{}!@#$%^&()]'
name = "\\ <>> asdfas test"
if re.search(invalid_chars, name):
   print("Invalid characters in name")
else:
   print("Valid name")

