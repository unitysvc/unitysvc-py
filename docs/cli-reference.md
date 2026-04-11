# CLI Reference

The `usvc` CLI is installed by `pip install unitysvc-py`. All commands
read credentials from `UNITYSVC_API_KEY` / `UNITYSVC_API_URL` by
default and accept `--api-key` / `--base-url` overrides.

## `usvc env`

Show which environment variables the SDK and CLI will use. Secrets
are redacted.

## `usvc secrets`

Customer secret management.

```
usvc secrets list [--skip N] [--limit N] [--format table|json]
usvc secrets set NAME [--value V | --from-file PATH]
usvc secrets delete NAME [--yes]
```

- `list` — list all secrets owned by the authenticated customer.
- `set` — upsert a secret by name. Looks it up first; updates if
  present, otherwise creates. If neither `--value` nor `--from-file`
  is passed, prompts interactively with hidden input.
- `delete` — remove a secret by name.

## `usvc aliases`

Customer service-alias operations.

```
usvc aliases list [--name NAME] [--include-deactivated]
                  [--skip N] [--limit N] [--format table|json]
usvc aliases show ALIAS_ID
usvc aliases delete ALIAS_ID [--yes]
```

## `usvc recurrent-requests`

Customer recurrent-request operations.

```
usvc recurrent-requests list [--service-id ID] [--enrollment-id ID]
                             [--status STATUS]
                             [--skip N] [--limit N]
                             [--format table|json]
usvc recurrent-requests show REQUEST_ID
usvc recurrent-requests trigger REQUEST_ID
usvc recurrent-requests delete REQUEST_ID [--yes]
```
