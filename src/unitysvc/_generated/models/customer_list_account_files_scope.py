from typing import Literal, cast

CustomerListAccountFilesScope = Literal["personal", "shared"]

CUSTOMER_LIST_ACCOUNT_FILES_SCOPE_VALUES: set[CustomerListAccountFilesScope] = {
    "personal",
    "shared",
}


def check_customer_list_account_files_scope(value: str) -> CustomerListAccountFilesScope:
    if value in CUSTOMER_LIST_ACCOUNT_FILES_SCOPE_VALUES:
        return cast(CustomerListAccountFilesScope, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CUSTOMER_LIST_ACCOUNT_FILES_SCOPE_VALUES!r}")
