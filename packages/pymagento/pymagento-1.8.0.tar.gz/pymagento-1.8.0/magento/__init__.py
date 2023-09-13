from datetime import datetime

from magento.attributes import (
    get_custom_attribute, get_boolean_custom_attribute, get_custom_attributes_dict,
    set_custom_attribute, set_custom_attributes, serialize_attribute_value
)
from magento.client import Magento
from magento.exceptions import MagentoException, MagentoAssertionError
from magento.order_helpers import is_order_on_hold, is_order_cash_on_delivery, get_order_shipping_address
from magento.queries import Query, make_field_value_query, make_search_query
from magento.version import __version__

# ids of the default categories in Magento
ROOT_CATEGORY_ID = 1
# Note this is the default root category, but it can be changed
DEFAULT_ROOT_CATEGORY_ID = 2

# Magento visibility options
# https://devdocs.magento.com/guides/v2.4/rest/tutorials/configurable-product/create-configurable-product.html
VISIBILITY_BOTH = 4
VISIBILITY_IN_CATALOG = 2
VISIBILITY_IN_SEARCH = 3
VISIBILITY_NOT_VISIBLE = 1

# Magento product statuses
# https://magento.stackexchange.com/q/10693/92968
ENABLED_PRODUCT = 1
DISABLED_PRODUCT = 2


def format_datetime(dt: datetime):
    """Format a datetime for Magento."""
    # "2021-07-02 13:19:18.300700" -> "2021-07-02 13:19:18"
    return dt.isoformat(sep=" ").split(".", 1)[0]
