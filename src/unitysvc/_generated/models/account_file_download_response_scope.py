from typing import Literal, cast

AccountFileDownloadResponseScope = Literal["personal", "shared"]

ACCOUNT_FILE_DOWNLOAD_RESPONSE_SCOPE_VALUES: set[AccountFileDownloadResponseScope] = {
    "personal",
    "shared",
}


def check_account_file_download_response_scope(value: str) -> AccountFileDownloadResponseScope:
    if value in ACCOUNT_FILE_DOWNLOAD_RESPONSE_SCOPE_VALUES:
        return cast(AccountFileDownloadResponseScope, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ACCOUNT_FILE_DOWNLOAD_RESPONSE_SCOPE_VALUES!r}")
