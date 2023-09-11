
class ApiException(Exception):
    def __init__(self, code, message):            
        super().__init__(code, message)

class BuildException(Exception):
    def __init__(self, message):            
        super().__init__(message)
