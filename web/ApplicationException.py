class ApplicationException(Exception):
    """
    Custom application exception
    Can be used to return more meaningfull errors than 404 page not found
    useage: raise ApplicationException(message=aaaa, statuscode=111)
    """
    def __init__(self, message = None, statuscode = 500):
        """
        Custom exception handler
        Without a statuscode the code defaults to 500
        Without a message the message defaults to None
        """
        # Call the base class constructor with the parameters it needs
        Exception.__init__(self, message)
        if not statuscode:
            statuscode = 500
        self.statuscode = statuscode
        self.message = message


