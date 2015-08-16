import re

exp = [r'\w$',
       r'(\w+/)',
       r'(\w+/)*',
       r'^/(\w+/)',
       r'^/(\w+/)*',
       r'^/(\w+/)*\w*$'] 



def match(word):
    print word
    for item in exp:
        if re.match(item, word):
            print item
    print '---'

match('hi')
match('_')
match('h/')
match('/')
match('//')
match('/h')
match('/h/')
match('/hi')
match('/hi/')

if re.match(exp[0], 'h/'):
    print True
    print exp[0]
    print 'h/'

if re.match(r'/','//'):
    print True
