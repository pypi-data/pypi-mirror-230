"""
Generic Views
"""
from flask.views import MethodView
from ms_utils import ViewGeneralMethods


class ApiView(MethodView, ViewGeneralMethods):
    """
    Api Class
    """
    init_every_request = False
    post_validator = None
    path_validator = None

    def get_post_validator(self):
        """
        Get validator
        """
        if self.post_validator is None:
            raise ValueError("'Validator' is not defined.")

    def get_path_validator(self):
        """
        Get validator
        """
        if self.path_validator is None:
            raise ValueError("'Validator' is not defined.")


class GenericItemCrud(ApiView):
    def get(self, object_id):
        return self.details(object_id)

    def patch(self, object_id):
        return self.update_or_create(self.path_validator(), object_id)

    def delete(self, object_id):
        return self.delete(object_id)


class GenericGroupCrud(ApiView):
    def get(self):
        return self.list()

    def post(self):
        return self.update_or_create(self.get_post_validator())


class UrlsApi:
    blueprint = None
    url_name = 'generic-api'
    item_crud_class = GenericItemCrud
    group_crud_class = GenericGroupCrud

    def __init__(self):
        self.register_api()

    def get_blueprint(self):
        """
        Get validator
        """
        if self.blueprint is None:
            raise ValueError("'Blueprint' is not defined.")

    def register_api(self):
        item = self.item_crud_class.as_view(f"{self.url_name}-item")
        group = self.group_crud_class.as_view(f"{self.url_name}-group")
        self.get_blueprint().add_url_rule(f"/{self.url_name}/<int:object_id>", view_func=item)
        self.get_blueprint().add_url_rule(f"/{self.url_name}/", view_func=group)
