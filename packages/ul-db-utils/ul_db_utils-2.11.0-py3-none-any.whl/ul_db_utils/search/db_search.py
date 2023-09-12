"""
    Datebase filtering + sorting util from Flask-Restless
"""
import inspect
from typing import List, Dict, Optional, Tuple, Any, TypeVar, Type, Generator, Callable, Union, Iterator

from flask_sqlalchemy import Model
from sqlalchemy import and_, or_, not_
from sqlalchemy.ext.associationproxy import AssociationProxy
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm import Query
from sqlalchemy.sql.operators import ColumnOperators

from ul_db_utils.search.helpers import is_like_list
from ul_db_utils.search.helpers import get_relations
from ul_db_utils.search.helpers import get_related_model
from ul_db_utils.search.helpers import get_related_association_proxy_model
from ul_db_utils.search.helpers import session_query
from ul_db_utils.search.helpers import string_to_datetime
from ul_db_utils.search.helpers import ensure_attribute
from ul_db_utils.errors.compare_null_error import ComparisonToNullError
from ul_db_utils.errors.unknow_field_error import UnknownFieldError
from ul_db_utils.errors.db_filter_error import DBFiltersError
from ul_db_utils.errors.db_sort_error import DBSortError


OPERATORS: Dict[str, Union[Callable[[ColumnOperators, Any, str], bool], Callable[[ColumnOperators, Any], bool], Callable[[ColumnOperators], bool]]] = {  # type: ignore
    # Operators which accept a single argument.
    'is_null': lambda f: f == None,         # noqa: E711
    'is_not_null': lambda f: f != None,     # noqa: E711
    # 'desc': lambda f: f.desc,
    # 'asc': lambda f: f.asc,
    # Operators which accept two arguments.
    '==': lambda f, a: f == a,
    'eq': lambda f, a: f == a,
    'equals': lambda f, a: f == a,
    'equal_to': lambda f, a: f == a,
    '!=': lambda f, a: f != a,
    'ne': lambda f, a: f != a,
    'neq': lambda f, a: f != a,
    'not_equal_to': lambda f, a: f != a,
    'does_not_equal': lambda f, a: f != a,
    '>': lambda f, a: f > a,
    'gt': lambda f, a: f > a,
    '<': lambda f, a: f < a,
    'lt': lambda f, a: f < a,
    '>=': lambda f, a: f >= a,
    'ge': lambda f, a: f >= a,
    'gte': lambda f, a: f >= a,
    'geq': lambda f, a: f >= a,
    '<=': lambda f, a: f <= a,
    'le': lambda f, a: f <= a,
    'lte': lambda f, a: f <= a,
    'leq': lambda f, a: f <= a,
    '<<': lambda f, a: f.op('<<')(a),
    '<<=': lambda f, a: f.op('<<=')(a),
    '>>': lambda f, a: f.op('>>')(a),
    '>>=': lambda f, a: f.op('>>=')(a),
    '<>': lambda f, a: f.op('<>')(a),
    '&&': lambda f, a: f.op('&&')(a),
    'ilike': lambda f, a: f.ilike(a),
    'like': lambda f, a: f.like(a),
    'not_like': lambda f, a: ~f.like(a),
    'in': lambda f, a: f.in_(a),
    'not_in': lambda f, a: ~f.in_(a),
    # Operators which accept three arguments.
    'has': lambda f, a, fn: f.has(_sub_operator(f, a, fn)),
    'any': lambda f, a, fn: f.any(_sub_operator(f, a, fn)),
}


class Filter(object):

    def __init__(self, fieldname: str, operator: str, argument: Optional[Dict[str, Any]] = None, otherfield: Optional[str] = None) -> None:
        self.fieldname = fieldname
        self.operator = operator
        self.argument = argument
        self.otherfield = otherfield

    @staticmethod
    def from_dictionary(model: Type[Model], dictionary: Dict[str, Any]) -> 'Filter':
        # If there are no ANDs or ORs, we are in the base case of the
        # recursion.
        if 'or' not in dictionary and 'and' not in dictionary:
            fieldname = dictionary.get('name')
            if not hasattr(model, fieldname.split('.')[0]):  # type: ignore
                raise UnknownFieldError(fieldname)  # type: ignore
            operator = dictionary.get('op')
            otherfield = dictionary.get('field')
            argument = dictionary.get('val')
            # Need to deal with the special case of converting dates.
            argument = string_to_datetime(model, fieldname, argument)  # type: ignore
            return Filter(fieldname, operator, argument, otherfield)  # type: ignore
        # For the sake of brevity, rename this method.
        from_dict = Filter.from_dictionary
        # If there is an OR or an AND in the dictionary, recurse on the
        # provided list of filters.
        if 'or' in dictionary:
            subfilters = dictionary.get('or')
            return DisjunctionFilter(*[from_dict(model, filter_)
                                       for filter_ in subfilters])  # type: ignore
        else:
            subfilters = dictionary.get('and')
            return ConjunctionFilter(*[from_dict(model, filter_)
                                       for filter_ in subfilters])  # type: ignore


class JunctionFilter(Filter):
    """A conjunction or disjunction of other filters.

    `subfilters` is a tuple of :class:`Filter` objects.

    """

    def __init__(self, *subfilters: Filter) -> None:
        self.subfilters = subfilters

    def __iter__(self) -> Iterator[Filter]:
        return iter(self.subfilters)


class ConjunctionFilter(JunctionFilter):
    """A conjunction of other filters."""


class DisjunctionFilter(JunctionFilter):
    """A disjunction of other filters."""


def _sub_operator(model: Type[Model], argument: Dict[str, Any], fieldname: str) -> bool:
    """Recursively calls :func:`create_operation` when argument is a dictionary
    of the form specified in :ref:`search`.

    This function is for use with the ``has`` and ``any`` search operations.

    """
    if isinstance(model, InstrumentedAttribute):
        submodel = model.property.mapper.class_
    elif isinstance(model, AssociationProxy):
        submodel = get_related_association_proxy_model(model)
    fieldname = argument['name']
    operator = argument['op']
    argument = argument.get('val')  # type: ignore
    return create_operation(submodel, fieldname, operator, argument)  # type: ignore


def create_operation(model: Type[Model], fieldname: str, operator: str, argument: Optional[Any]) -> bool:
    # raises KeyError if operator not in OPERATORS
    opfunc = OPERATORS[operator]
    # In Python 3.0 or later, this should be `inspect.getfullargspec`
    # because `inspect.getargspec` is deprecated.
    numargs = len(inspect.getargspec(opfunc).args)
    # raises AttributeError if `fieldname` does not exist
    field = getattr(model, fieldname)
    # each of these will raise a TypeError if the wrong number of argments
    # is supplied to `opfunc`.
    if numargs == 1:
        return opfunc(field)  # type: ignore
    if argument is None:
        msg = ('to compare a value to NULL, use the is_null/is_not_null '
               'operators.')
        raise ComparisonToNullError(msg)
    if numargs == 2:
        return opfunc(field, argument)  # type: ignore
    return opfunc(field, argument, fieldname)  # type: ignore


T = TypeVar('T', bound=Model)


def left_join_table(query: 'Query[T]', parent_model: Type[T], relationship_name: str) -> 'Query[T]':
    relationships = [relation for relation in get_relations(parent_model) if relation[0] == relationship_name]
    if relationships:
        relationship = relationships[0][1]
        if relationship.secondary is not None:
            query = query.outerjoin(relationship.secondary, relationship.secondaryjoin)
        query = query.outerjoin(relationship.target, relationship.primaryjoin)
    return query


def create_filter(model: Type[Model], filt: Filter) -> Union[Generator[bool, None, None], bool]:
    # If the filter is not a conjunction or a disjunction, simply proceed as normal.
    if not isinstance(filt, JunctionFilter):
        fname = filt.fieldname
        val = filt.argument
        # get the other field to which to compare, if it exists
        if filt.otherfield:
            val = getattr(model, filt.otherfield)
        # for the sake of brevity...
        return create_operation(model, fname, filt.operator, val)
    # Otherwise, if this filter is a conjunction or a disjunction, make
    # sure to apply the appropriate filter operation.
    if isinstance(filt, ConjunctionFilter):
        return and_(create_filter(model, f) for f in filt)
    return or_(create_filter(model, f) for f in filt)


def ensure_sort_attribute(model: Type[Model], field_name: str) -> Any:
    try:
        field = ensure_attribute(model, field_name)
    except UnknownFieldError as e:
        raise DBSortError(f"invalid value in query sort params: {e.field}")
    return field


TModel = TypeVar('TModel', bound=Model)


def db_search(
    model: Type[TModel],
    initial_query: 'Optional[Query[TModel]]' = None,
    filters: Optional[List[Dict[str, Any]]] = None,
    sorts: Optional[List[Tuple[str, str]]] = None,
    limit: Optional[int] = 1000,
    offset: int = 0,
) -> 'Query[TModel]':
    """ Applies filters, sortings, limit, offset to SqlAlchemy Query

        :filter example: [{"name": "is_alive", "op": "==", "val": "True"}]

        :sort example: [("+", "id"), ("-", "date_modifed")]
    """
    if initial_query is not None:
        query = initial_query
    else:
        query = session_query(model)
    # Filter the query.
    if filters:
        try:
            q_filters = [Filter.from_dictionary(model, f) for f in filters]
            # This function call may raise an exception.
            q_filters = [create_filter(model, f) for f in q_filters]  # type: ignore
        except UnknownFieldError as e:
            raise DBFiltersError(f"invalid attribute in query filter params: {model.__name__.lower()} has no attribute '{e.field}'")
        except KeyError:
            raise DBFiltersError("invalid operation in query filter params")
        except ComparisonToNullError as e:
            raise DBFiltersError(f"invalid value in query filter params: {e}")
        # not best practices, but ensure exception for all remaining exceptions
        except (Exception):     # noqa: E722
            raise DBFiltersError("invalid query filter params")
        query = query.filter(*q_filters)

    if sorts:
        for (symbol, field_name) in sorts:
            direction_name = 'asc' if symbol == '+' else 'desc'
            if '.' in field_name:
                sort_list = field_name.split('.')
                related_models: List[Type[Model]] = [model]
                if len(sort_list) > 2:
                    for model_name in sort_list[0:-1]:
                        relation_model = get_related_model(related_models[-1], model_name)
                        query = left_join_table(
                            query=query,
                            parent_model=related_models[-1],  # type: ignore
                            relationship_name=model_name,
                        )
                        related_models.append(relation_model)  # type: ignore
                    last_field = ensure_sort_attribute(related_models[-1], sort_list[-1])
                    direction = getattr(last_field, direction_name)
                    query = query.order_by(direction())
                else:
                    model_name, field_name = sort_list
                    relation_model = get_related_model(related_models[-1], model_name)
                    query = left_join_table(
                        query=query,
                        parent_model=related_models[-1],  # type: ignore
                        relationship_name=model_name,
                    )
                    related_models.append(relation_model)  # type: ignore
                    field = ensure_sort_attribute(related_models[-1], field_name)
                    # Check filed belongs to last model
                    # else - it's relationship, need to left join and different sort
                    if relation_model.__table__ == field._from_objects[0]:  # type: ignore
                        direction = getattr(field, direction_name)
                        query = query.order_by(direction())
                    else:
                        relation_model = get_related_model(related_models[-1], field_name)
                        query = left_join_table(
                            query=query,
                            parent_model=related_models[-1],  # type: ignore
                            relationship_name=field_name,
                        )
                        related_models.append(relation_model)  # type: ignore
                        try:
                            direction = getattr(field, direction_name)
                            query = query.order_by(direction())
                        except NotImplementedError:
                            if is_like_list(model, field_name):
                                any_op = getattr(field, 'any')      # noqa: B009
                                query = query.order_by(any_op() if direction_name == 'desc' else not_(any_op()))
                            else:
                                has_op = getattr(field, 'has')      # noqa: B009
                                query = query.order_by(has_op() if direction_name == 'desc' else not_(has_op()))
            else:
                field = ensure_sort_attribute(model, field_name)
                try:
                    direction = getattr(field, direction_name)
                    query = query.order_by(direction())
                except NotImplementedError:
                    if is_like_list(model, field_name):
                        any_op = getattr(field, 'any')      # noqa: B009
                        query = query.order_by(any_op() if direction_name == 'desc' else not_(any_op()))
                    else:
                        has_op = getattr(field, 'has')      # noqa: B009
                        query = query.order_by(has_op() if direction_name == 'desc' else not_(has_op()))

    if limit is not None:  # because sometimes you need NORMAL pagination with filtered items
        query = query.limit(limit).offset(offset)
    return query
