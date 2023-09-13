class Redirect:


    def __init__(self, request, route, status_code=307):

        self.request = request
        self.route = route
        self.status_code = status_code
