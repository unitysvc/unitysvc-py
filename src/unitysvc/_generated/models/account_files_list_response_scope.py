from typing import Literal, cast

AccountFilesListResponseScope = Literal["personal", "shared"]

ACCOUNT_FILES_LIST_RESPONSE_SCOPE_VALUES: set[AccountFilesListResponseScope] = {
    "personal",
    "shared",
}


def check_account_files_list_response_scope(value: str) -> AccountFilesListResponseScope:
    if value in ACCOUNT_FILES_LIST_RESPONSE_SCOPE_VALUES:
        return cast(AccountFilesListResponseScope, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ACCOUNT_FILES_LIST_RESPONSE_SCOPE_VALUES!r}")
