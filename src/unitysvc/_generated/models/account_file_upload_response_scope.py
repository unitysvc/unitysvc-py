from typing import Literal, cast

AccountFileUploadResponseScope = Literal["personal", "shared"]

ACCOUNT_FILE_UPLOAD_RESPONSE_SCOPE_VALUES: set[AccountFileUploadResponseScope] = {
    "personal",
    "shared",
}


def check_account_file_upload_response_scope(value: str) -> AccountFileUploadResponseScope:
    if value in ACCOUNT_FILE_UPLOAD_RESPONSE_SCOPE_VALUES:
        return cast(AccountFileUploadResponseScope, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ACCOUNT_FILE_UPLOAD_RESPONSE_SCOPE_VALUES!r}")
