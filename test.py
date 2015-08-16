from watermelon import App, render_template
from server import *

app = App()

## TEST 1: Return Hello World ##
@app.route('/hello')
def hello():
    return 'Hello World'

@app.route('/')
def welcome():
    return 'Welcome'

@app.route('/reading')
def reading():
    template = render_template('test.txt')
    print template
    return template

#render css file
@app.route('/html')
def show_html():
    html = render_template('test.html',title="Hello!",message="Watermelon is successfully rendering!")
    return html

#take in dynamic stuff
@app.route('/dynamic/<name>')
def say_name(name):
    print 'hello!'
    return "Hi there "+name+"!"

@app.route('/form')
def create_form():
    resp = render_template('test.html')
    return resp


@app.route('/submitted', method='POST')
def submitted():
    return "Form Submitted! %d%d%d%d" %(row, col, to_row, tocol)

@app.route('/simple_html')
def simple_html():
    return "<html>Hello</html>"

#app.run()
app.run(server=WSGIRefServer)

