from typing import Literal, cast

AccountFileUploadRequestScope = Literal["personal", "shared"]

ACCOUNT_FILE_UPLOAD_REQUEST_SCOPE_VALUES: set[AccountFileUploadRequestScope] = {
    "personal",
    "shared",
}


def check_account_file_upload_request_scope(value: str) -> AccountFileUploadRequestScope:
    if value in ACCOUNT_FILE_UPLOAD_REQUEST_SCOPE_VALUES:
        return cast(AccountFileUploadRequestScope, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ACCOUNT_FILE_UPLOAD_REQUEST_SCOPE_VALUES!r}")
