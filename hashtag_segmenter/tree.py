#----------------------------
# Copyright 2014 Ryan Tidwell
#----------------------------

class TreeNode(object):
    children = None
    token = None
    is_visited = False
    parent = None

    def __init__(self, token):
        self.token = token
        self.children = []
        self.is_visited = False
        self.parent = None

    def set_parent(self, tree_node):
        self.parent = tree_node

    def get_parent(self):
        return self.parent

    def add_child(self, tree_node):
        self.children.append(tree_node)

    def get_children(self):
        return self.children

    def get_token(self):
        return self.token

    def set_visited(self):
        self.is_visited = True

    def visited(self):
        return self.is_visited

    def __str__(self):
        return self.token

    def __repr__(self):
        return self.token
