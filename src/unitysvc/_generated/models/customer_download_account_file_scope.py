from typing import Literal, cast

CustomerDownloadAccountFileScope = Literal["personal", "shared"]

CUSTOMER_DOWNLOAD_ACCOUNT_FILE_SCOPE_VALUES: set[CustomerDownloadAccountFileScope] = {
    "personal",
    "shared",
}


def check_customer_download_account_file_scope(value: str) -> CustomerDownloadAccountFileScope:
    if value in CUSTOMER_DOWNLOAD_ACCOUNT_FILE_SCOPE_VALUES:
        return cast(CustomerDownloadAccountFileScope, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CUSTOMER_DOWNLOAD_ACCOUNT_FILE_SCOPE_VALUES!r}")
