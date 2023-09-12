from sqlalchemy.dialects.postgresql import UUID

from ul_db_utils.model.base_immutable_model import BaseImmutableModel
from ul_db_utils.model.methods.make_immutable_column import make_immutable_column
from ul_db_utils.modules.custom_query import CustomQuery
from ul_db_utils.modules.db import db


class MediaFile(BaseImmutableModel):
    """
      Model for media-storage-service
      git: /unic-lab/libraries/common-services/media-storage

      basename: str, complete title of a file and file extension
      sha2_hashsum: str, sha2 hashsum of a file data
      content: content of a file, stored in binary format
      """
    __tablename__ = 'media_file'

    media_file_type_id = db.Column(UUID(as_uuid=True), db.ForeignKey('media_file_type.id'), nullable=False)

    basename = db.Column(db.String(1000), nullable=False)
    sha2_hashsum = db.Column(db.String(255), nullable=False)  # not updatable
    content = db.Column(db.LargeBinary, nullable=False)  # not updatable

    media_file_type = db.relationship(
        'MediaFileType',
        foreign_keys=[media_file_type_id],
        query_class=CustomQuery,
        uselist=False,
        lazy='joined',
    )


make_immutable_column(MediaFile.content)
make_immutable_column(MediaFile.sha2_hashsum)
