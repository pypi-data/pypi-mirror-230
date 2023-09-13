class HaiqvValueError(Exception):
    def __init__(self, error:dict):
        self.error = error
    
    def __str__(self):
        return str(self.error)

    def get_code(self):
        return self.error.get('error_code')

    def get_message(self):
        return self.error.get('message')