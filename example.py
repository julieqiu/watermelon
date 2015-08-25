from watermelon import App, render_template, request, Response
from server import *

app = App()

@app.route('/')
def welcome():
    return 'Welcome!!!'

@app.route('/dynamic/<name>')
def say_name(name):
    print 'hello!'
    return "Hi there "+name+"!"

@app.route('/text')
def reading():
    template = render_template('test.txt')
    return template

@app.route('/form')
def create_form():
    resp = render_template('test_form.html',
                           title='Hello!',
                           message='Enter Values')
    return resp

@app.route('/submitted', method='POST')
def submitted():
    row = request.args.get('row')
    col = request.args.get('col')
    to_row = request.args.get('to_row')
    to_col = request.args.get('to_col') 
    row = int(row)
    col = int(col)
    to_row = int(to_row)
    to_col = int(to_col)
    return "Form Submitted! %d%d%d%d" %(row, col, to_row, to_col)

@app.route('/make_response')
def make_response():
    response = Response()
    response.txt = 'Hello'
    response.add_header_item('Foo','Bar')
    return response

@app.route('/stack')
def render():
    title = 'This is the Title'
    another_title = ' This is another title'
    lst = [1,2,3,4]
    my_dict = {'k' : 'v', 'x' : 'y' }
    resp = render_template('test_stack.html', 
                           Title=title, 
                           another_title=another_title, 
                           lst=lst, 
                           my_dict=my_dict)
    return resp

if __name__ == '__main__':
    app.run()
