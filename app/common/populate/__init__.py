"""
Usage:

Run Django shell:

        $ python manage.py shell

Import populate module:

        >>> from app.common.populate import populate_threads, populate_async, Settings

Create settings object:

            >>> settings = Settings(
            ...     categories_count=10,
            ...     products_per_category_count=10,
            ...     customers_count=10,
            ...     carts_per_customer_count=10,
            ...     cart_items_per_cart_count=10,
            ... )

Run populate_threads:

                >>> populate_threads(settings, threads_count=4)

Or run populate_async:

                >>> populate_async(settings, tasks_count=4)

You can also call the script with default settings:

                    >>> populate_threads()
                    >>> populate_async()

The script also creates a superuser with the following credentials:
    username: `admin` (env variable: DJANGO_SUPERUSER_USERNAME)
    password: `admin` (env variable: DJANGO_SUPERUSER_PASSWORD)
    email: `admin@mail.com` (env variable: DJANGO_SUPERUSER_EMAIL)

for more information about the settings object, see :package:`app.common.populate.utils`
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

sys.path.append(str(BASE_DIR))

from app.common.populate.script_async import populate_async  # noqa: E402
from app.common.populate.script_threads import populate_threads  # noqa: E402
from app.common.populate.utils import Settings  # noqa: E402

__all__ = [
    "populate_threads",
    "populate_async",
    "Settings",
]
