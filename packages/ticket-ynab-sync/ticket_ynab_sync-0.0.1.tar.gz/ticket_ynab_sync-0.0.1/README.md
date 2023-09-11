================
ticket_ynab_sync
================


Sync Ticket transactions with a YNAB account.


# CLI `tys``

Commands:

- `tys init /path/to/db`: initializes a new Sync database (asks for YNAB and Ticket credentials) at the provided path
- `tys info /path/to/db`: displays information about the current state of the provided Sync database
- `tys sync /path/to/db`: runs a sync iteration - 1) get new transactions from Ticket, 2) push them to YNAB
  - `tys sync --period X /path/to/db`: ryns a sync iteration every X minutes
  - `tys sync --hour X /path/to/db`: ryns a sync iteration every X minutes



# TODO

[ ] CLI for configuring Ticket, e..g creds, start sync date, sync period, default category, etc.
[ ] CLI config YNAB, creds, which account to save new transactions to
[ ] init database with Ticket transactions
  [ ] extra: check if Ticket transactions already exist in YNAB account, based on value, description and date; store YNAB transaction id on local database
[ ] push new Ticket transactions (without YNAB id) to YNAB, get YNAB ID, associate ID to Ticket transaction
[ ] create loop for syncing
[ ] OR add to cronjob
[ ] EXTRA: alternative web based GUI to CLI


# Ticket API

https://github.com/diogo-aos/TicketYnacSync