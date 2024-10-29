from collector import Collector
from scanner import Scanner

s = Scanner()
s.read_config('config.yml')
print(s.pattern)
for i in s.pattern:
    print(i)
