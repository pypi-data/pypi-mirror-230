"""
View Utils
"""
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

from ms_utils import prepare_json_response, PaginationSchema
from flask import current_app, request

from .model_utils import generic_get_serialize_data
from .validation_utils import validate_generic_form


class ViewGeneralMethods:
    """
    View generic Methods
    """
    ma = None
    db = None
    model = None
    schema = None
    instance = None

    def get_db(self):
        """
        Get SQLAlchemy instance
        """
        if self.db is not None:
            return self.db
        if 'db' in current_app.config.keys() and isinstance(current_app.config.get('db'), SQLAlchemy):
            return current_app.config.get('db')
        raise ValueError("'SQLAlchemy' is not defined.")

    def get_ma(self):
        """
        Get Marshmallow instance
        """
        if self.ma is not None:
            return self.ma
        if 'ma' in current_app.config.keys() and isinstance(current_app.config.get('ma'), Marshmallow):
            self.ma = current_app.config.get('ma')
            return current_app.config.get('ma')
        raise ValueError("'Marshmallow' is not defined.")

    def get_queryset(self):
        """
        Get query
        """
        if self.model is None:
            raise ValueError("'Model' is not defined.")
        return self.model.query

    def get_item(self, pk):
        self.instance = self.get_queryset().get_or_404(pk)
        return self.instance

    def get_list_without_pagination(self):
        """
        List items without pagination
        :return: json
        """
        return generic_get_serialize_data(self.schema(many=True), self.get_queryset().all())

    def get_list_with_pagination(self, **kwargs):
        """
        List items with pagination
        :param: kwargs
        :return: json
        """
        # TODO:: Review the filter option and take it to a method
        page = int(request.args.get('page')) if request.args.get('page') else 1
        per_page = int(request.args.get('per_page')) if request.args.get('per_page') else 10
        query = self.get_queryset()
        if request.args.get('q'):
            query = query.filter_by(**kwargs)
        query = query.paginate(page=page, per_page=per_page)
        query.items = generic_get_serialize_data(self.schema(many=True), query.items)
        return generic_get_serialize_data(
            PaginationSchema(self.schema(many=True)).pagination_sub_class, query)

    def list(self, **kwargs):
        """
        Generic list
        :return: jsonify
        """
        if request.args.get('not_paginate'):
            data = self.get_list_without_pagination()
        else:
            data = self.get_list_with_pagination(**kwargs)

        return prepare_json_response(f'{self.model.__name__} get successfully', data=data)

    def update_or_create(self, validation_class, object_id=None):
        """
        Generic method for create or update provider
        :param validation_class:
        :param object_id:
        :return: jsonify
        """
        errors = validate_generic_form(validation_class)
        if errors is not None:
            return errors
        action_text = 'created'
        try:
            data = request.json
            if object_id is None:
                self.create(data)
            else:
                action_text = 'updated'
                self.get_item(object_id)
                self.update(data)
            self.get_db().session.commit()
        except ValueError:
            self.get_db().session.rollback()
            return prepare_json_response(f'{self.model.__name__} can not be {action_text} successfully', False,
                                         code=400)
        return prepare_json_response(f'{self.model.__name__} {action_text} successfully')

    def create(self, data):
        """
        Generic Create method
        :param data:
        :return:
        """
        if self.model is None:
            raise ValueError("'Model' is not defined.")
        self.instance = self.model(**data)
        self.get_db().session.add(self.instance)
        return self.instance

    def update(self, data):
        """
        Generic Update method
        :param data:
        :return:
        """
        for key, value in data.items():
            if hasattr(self.instance, key):
                attribute = getattr(self.instance, key)
                if not hasattr(attribute, '__tablename__'):
                    # If the attribute is not a relationship
                    setattr(self.instance, key, value)

    def details(self, object_id):
        """
        Generic details method
        :param object_id:
        :return:
        """
        self.get_item(object_id)
        return prepare_json_response(f'{self.model.__name__} get successfully',
                                     data=generic_get_serialize_data(self.schema(), self.instance))

    def delete(self, object_id):
        """
        Generic delete method
        :param object_id:
        :return:
        """
        self.get_queryset().filter_by(id=object_id).delete()
        self.get_db().session.commit()
        return prepare_json_response(f'{self.model.__name__} deleted successfully!')

    def generic_change_boolean(self, object_id, field):
        """
        Generic change boolean method
        :param object_id:
        :param field:
        :return:
        """
        model_object = self.get_db().get_or_404(self.model, object_id)
        self.model.query.filter_by(id=object_id).update({field: not getattr(model_object, field)})
        self.get_db().session.commit()
        return prepare_json_response(
            f'{self.model.__name__} field {field} updated to {getattr(model_object, field)} successfully!')
