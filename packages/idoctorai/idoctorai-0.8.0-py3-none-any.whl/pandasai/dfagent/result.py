class Result:

    def __init__(self, status=None, error=None, content=None, picpath=None):
        self.status = status
        self.error = error
        self.content = content
        self.picpath = picpath