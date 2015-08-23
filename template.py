import re

VAR_TOKEN_START = '{{'
VAR_TOKEN_END = '}}'
BLOCK_TOKEN_START = '{%'
BLOCK_TOKEN_END = '%}'
REGEX_TOKEN = re.compile(r'(%s.*?%s|%s.*?%s)' %(VAR_TOKEN_START, VAR_TOKEN_END, 
                                                BLOCK_TOKEN_START, BLOCK_TOKEN_END))
VAR_SPLIT_TOKEN = re.compile(r'%s\s*(.+?)\s*%s' %(VAR_TOKEN_START, VAR_TOKEN_END))
FOR_SPLIT_TOKEN = re.compile(r'%s\s*for\s+(.*\S+)\s+in\s+(.+?)\s*%s' %(BLOCK_TOKEN_START, BLOCK_TOKEN_END))
COND_SPLIT_TOKEN = re.compile(r'%s\s*(if|elif|else)(?:\s+(.+))?\s*%s' %(BLOCK_TOKEN_START, BLOCK_TOKEN_END))
END_TOKEN = re.compile(r'%s\s*end(if|for)\s*%s' %(BLOCK_TOKEN_START, BLOCK_TOKEN_END))

# {% if a == "%}" %}
# {{ foo + "}}" }}

class TemplateError(Exception):
    pass


class ParseError(TemplateError):
    pass 


class Node:
    def __init__(self, val=None):
        self.val = val
    

class TextNode(Node):
    def render(self, scope):
        return self.val


class VarNode(Node):
    def __init__(self, val):
        Node.__init__(self, val) 

    def render(self, scope):
        val = scope.get(self.val, None)
        if val:
            return str(val)
        else:
            raise TemplateError


class LstNode(Node):
    def __init__(self):
        Node.__init__(self)
        self.children = []
    
    def add_child(self, node):
        self.children.append(node)

    def render(self, scope):
        text = ""
        for node in self.children:
            text += node.render(scope)
        return text


class ForNode(LstNode):
    def __init__(self, variables, iterable):
        LstNode.__init__(self)
        self.variables = variables
        self.iterable = iterable

    def render(self, scope):
        iterable = eval(self.iterable, scope)
        variables = self.variables.split(',')
        variables = [v.strip() for v in variables]
        txt = ''
 
        for value in iterable:
            if len(variables) == 1:
                scope[variables[0]] = value
            else:
                for i, var in enumerate(variables):
                    scope[var] = value[i]

            for child in self.children:
                txt += child.render(scope)
        return txt



class IfNode(Node):
    def __init__(self, condition):
        self.condition = condition
        self.if_children = []
        self.else_children = []
        self.curr_child = self.if_children

    def start_else(self):
        self.curr_child = self.else_children

    def add_child(self, item):
        self.curr_child.append(item)

    def is_in_else(self):
        return self.curr_child == self.else_children

    def render(self, scope):
        txt = ''
        if eval(self.condition, scope):
            for child in self.if_children:
                txt += child.render(scope)
        else:
            for child in self.else_children:
                txt += child.render(scope)
        return txt


class Stack:
    def __init__(self):
        self.stack = []

    def top(self):
        if self.stack:
            return self.stack[-1]
    
    def pop(self):
        if self.stack:
            return self.stack.pop()

    def push(self, val):
        self.stack.append(val)

    def __len__(self):
        return len(self.stack)


def process_template(template, scope):
    nodes_lst = REGEX_TOKEN.split(template)
    root_lst = LstNode()
    stk = Stack()
    stk.push(root_lst)
    for item in nodes_lst:
        if re.match(VAR_TOKEN_START, item):
            item = VAR_SPLIT_TOKEN.match(item).group(1) 
            node = VarNode(item)
            stk.top().add_child(node)
        elif re.match(BLOCK_TOKEN_START, item):
            for_token = FOR_SPLIT_TOKEN.match(item)
            if for_token:
                var, iterable = for_token.groups()
                node = ForNode(var, iterable)
                stk.top().add_child(node)
                stk.push(node)
                continue
            conditional_token = COND_SPLIT_TOKEN.match(item)
            if conditional_token: 
                exp, condition = conditional_token.groups()
                if exp == 'if':
                    node = IfNode(condition)
                    stk.top().add_child(node)
                    stk.push(node)
                elif exp == 'elif':
                    top = stk.top()
                    if not isinstance(top, IfNode):
                        raise ParseError('elif without corresponding if')
                    if top.is_in_else():
                        raise ParseError('elif after else')
                    top.start_else()
                    node = IfNode(condition)
                    stk.top().add_child(node)
                    stk.pop()
                    stk.push(node)
                elif exp == 'else':
                    stk.top().start_else()
            
            else:
                end_token = END_TOKEN.match(item)
                if end_token:
                        stk.pop()
                else:
                    raise ParseError("unexpected token %s" % item)
        else: 
            node = TextNode(item)
            stk.top().add_child(node)
       

    if len(stk) == 1:
        return root_lst
    elif isinstance (stk.top(), ForNode):
        raise TemplateError('for loop does not have matching endfor')
    elif isinstance (stk.top(), IfNode):
        raise TemplateError('conditional exp does not have matching endif')
    else:
        raise TemplateError('unknown template error')
