class Symbol(object):

        # Constructor
        def __init__(self, name, data_type, description, data_indicator):
            self.label = name
            self.data_type = data_type
            self.description = description
            self.data_indicator = data_indicator

        # String representation of symbol object
        def __repr__(self):
            return self.label + ' ' + str(self.data_type) + ' ' + str(self.description)
