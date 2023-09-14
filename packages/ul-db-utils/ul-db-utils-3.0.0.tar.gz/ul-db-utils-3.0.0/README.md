# Generic library db-utils

> Provides common database-related functionality that can be used across different services.

> Contains all database-related packages as dependencies.
If you need to use some package that is not available in your service, you should add it here.

## Common functionality
> This section describes some classes or methods that are awailable for use in all services that use db-utils.

### CustomQuery
> As a default this class inherit from *flask_sqlalchemy BaseQuery* and adds additional filters.
> 1. Filtering by only non-deleted (marked as *is_alive=True*) records.
> 2. Joining with/without deleted (marked as *is_alive=False*) records.

> If you want to add some additional by-default behavior to all services than you have to add it here.

### transaction_commit
> This context manager allows us to perform a database transaction at ORM level. You should use it like this:
> ```python
> with transaction_commit():
>   query.perform(something)

### Abstract models
> This section describes all available abstract models from which we can inherit in our services.

#### BaseModel
```python
class BaseModel(DbModel, SerializerMixin):

    __abstract__ = True

    query_class = CustomQuery

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow(), nullable=False)
    date_modified = db.Column(db.DateTime(), default=datetime.utcnow(), nullable=False)
    is_alive = db.Column(db.Boolean(), default=True, nullable=False)
```
> Provides UUID, record creation/modification datetime and is_alive field used for soft-deletion.

#### BaseUndeletableModel
```python
class BaseUndeletableModel(DbModel, SerializerMixin):

    __abstract__ = True

    query_class = BaseQuery

    id = db.Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow(), nullable=False)
    date_modified = db.Column(db.DateTime(), default=datetime.utcnow(), nullable=False)
```
> The same thing as BaseModel but models that will inherit from this model won't be able to soft-delete records.

#### BaseMaterializedPGViewModel
```python
class BaseMaterializedPGView(DbModel, SerializerMixin):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    last_refresh_date = db.Column(db.DateTime(), nullable=False)

    sql = ''
    refresh_by_tables: List[str] = []

    query_class = BaseQuery

    __table_args__ = {'info': {'skip_autogenerate': True}}

    _index_format = '{table}_{field}_index'
    _pkey_format = '{table}_pkey'

    __abstract__ = True
```
> Provides a way to create materialized views in PostgreSQL, add indexes, triggers, etc.

#### BaseImmutableModel
```python
class BaseImmutableModel(DbModel, SerializerMixin):
    __abstract__ = True

    query_class = BaseQuery

    id = db.Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow(), nullable=False)
    user_created_id = db.Column(PG_UUID(as_uuid=True), nullable=False)
```
> Models that are going to inherit from this one won't have update record functionality.

#### ApiUser
```python
class ApiUser(BaseModel):
    __tablename__ = 'api_user'

    date_expiration = db.Column(db.DateTime(), nullable=False)
    name = db.Column(db.String(255), unique=True, nullable=False)
    note = db.Column(db.Text(), nullable=False)
    permissions = db.Column(ARRAY(db.Integer()), nullable=False)
```
> Every APIUser Model record has an array of permissions.


### Exceptions

| Exception                    | Desription                                                                                                                                    |
|------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| ComparisonToNullError        | Raised when a client attempts to use a filter object that compares a resource's attribute to NULL using == operator instead of using is_null. |
| DBFiltersError               | Raised when a client attempts to filter with invalid query params.                                                                            |
| DBSortError                  | Raised when a client attempts to sort with invalid query params.                                                                              |
| MultipleObjectsReturnedError | When only one object expected to be returned, but DB returned multiple objects.                                                               |
| UnknownFieldError            | When user tries to reference the non-existent model field.                                                                                    |
| DeletionNotAllowedError      | Raised when db obj deletion not allowed.                                                                                                      |
| UpdateColumnNotAllowedError  | Raised when db table column update not allowed.                                                                                               |
| UpdateNotAllowedError        | Raised when db table update not allowed.                                                                                                      |
| DbError                      | Generic DB error.                                                                                                                             |


## Adding new database-related package
> First, try to understand why do you need this library and what exactly can you do with it. Look at the list of
> already existing libraries and think if they can fulfill your needs. 

> Check this library for deprecation, does it have enough maintenance, library dependencies.
> If all above satisfies you, perform next steps:
> 1. Add the package name and version to **Pipfile** under ```[packages]``` section. Example: ```alembic = "==1.8.1"```.
> 2. Run ```pipenv install```.
> 3. Add the package name and version to **setup.py** to ```install-requires``` section.
> 4. Commit changes. ```git commit -m "Add dependency *library-name*"```.
> 5. Run version patch: ```pipenv run version_patch```.
> 6. Push changes directly to dev ```git push origin dev --tags``` or raise MR for your changes to be reviewed.
