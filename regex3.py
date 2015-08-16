import re

x = r'<(\w+)>'
y = r'(?P<\1>[^/]+)'
z = re.sub(x, y, '/user/<name>/<hello>/<yo>')

a = '%s$' % z
#/user/(?P<name>[^/]+)$
print a

b = re.compile(a)
c = '/user/5/6/7' 

d = b.match(c)
e = d.groupdict()

print e


