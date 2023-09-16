"""
Pagination Generic Class
"""
from flask_marshmallow.sqla import SQLAlchemyAutoSchema


class PaginationSchema:
    """
    Pagination Class
    """
    schema_object = None

    def __init__(self, schema_object):
        self.schema_object = schema_object
        self.pagination_sub_class = self.PaginationSchemaSubClass()

    class PaginationSchemaSubClass(SQLAlchemyAutoSchema):
        """
        Pagination Schema Data
        """
        class Meta:
            """
            Meta Class
            """
            fields = ('has_prev', 'has_next', 'next_num', 'page', 'pages', 'per_page', 'prev_num', 'total', 'items')
