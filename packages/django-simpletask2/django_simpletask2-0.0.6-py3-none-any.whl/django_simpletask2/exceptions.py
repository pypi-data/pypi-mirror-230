

class DjangoSimpleTask2Error(RuntimeError):

    def __init__(self, code, message):
        super().__init__(code, message)
    
    @property
    def code(self):
        return self.args[0]
    
    @property
    def message(self):
        return self.args[1]
