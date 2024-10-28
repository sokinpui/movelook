from collector import Collector

c = Collector()
c.read_config('config.yml')
c.debug = True
c.process()



