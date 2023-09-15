from flask_restful import Resource


class HealthResource(Resource):
    def __init__(self, representations=None):
        self.representations = representations
        super(HealthResource, self).__init__()


    def get(self):
        return 'Ok', 200
