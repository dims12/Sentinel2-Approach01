import mgrs
import re

latitude = 42.0
longitude = -93.0

m = mgrs.MGRS()
c = m.toMGRS(latitude, longitude).decode('cp1252')

s = re.search('(\d+)([^\d])([^\d]{2})(\d{5})(\d{5})', c)
print('group1 = ', s.group(1))

pass