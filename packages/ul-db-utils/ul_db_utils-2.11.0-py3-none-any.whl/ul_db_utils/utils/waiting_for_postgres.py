import logging
import time
from urllib.parse import urlparse

from sqlalchemy_utils.types.pg_composite import psycopg2

logger = logging.getLogger(__name__)


def waiting_for_postgres(uri: str, *, retry_max_count: int = 100, retry_delay_s: float = 0.4) -> bool:
    parsed_db_uri = urlparse(uri)

    for i in range(0, retry_max_count):
        try:
            with psycopg2.connect(
                dbname=parsed_db_uri.path.strip('/'),
                user=parsed_db_uri.username,
                password=parsed_db_uri.password,
                host=parsed_db_uri.hostname,
                port=parsed_db_uri.port,
            ):
                logger.info("PostgreSQL is available")
            return True
        except Exception:  # noqa: B902
            logger.warning(f'{i + 1:0>{len(str(retry_max_count))}}/{retry_max_count} retry connect to PostgreSQL. sleep delay is {retry_delay_s} seconds')
            time.sleep(retry_delay_s)
            continue
    logger.error('PostgreSQL is NOT available')
    return False
