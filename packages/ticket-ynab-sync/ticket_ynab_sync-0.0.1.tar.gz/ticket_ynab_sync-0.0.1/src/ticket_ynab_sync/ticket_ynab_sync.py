"""Main module."""
from pyticketfood.ticket import Transaction as TicketTransaction, get_transactions as ticket_get_transactions


from .models import YnabConfig, TicketConfig, NewTransactionMsg, SyncedTransaction
import datetime as dt
from typing import List, Optional
from pathlib import Path
from .ynab import create_transaction
import pickle
import warnings

# get budget id
# get api key
# get account_id

# get ticket creds
# get start date from ticket
# init Ticket

# get new transactions from Ticket
# push new transactions to YNAB, store YNAB ID in local database

class Sync:
    def __init__(self, ticket_conf: TicketConfig, ynab_conf: YnabConfig):
        self.ticket_conf = ticket_conf
        self.ynab_conf = ynab_conf
        self.balance = None
        self.transactions: List[SyncedTransaction] = []
        self.last_update_ts = dt.datetime(2000,1,1)
        self.last_sync_ts = None

    def save_state(self, path: Path):
        with path.open('wb') as f:
            pickle.dump(self, f)

    def update(self) -> List[TicketTransaction]:
        if self.transactions:
            last_t_date = self.transactions[-1].ticket_transaction.date
        else:
            last_t_date = self.last_update_ts
        # get new ticket transactions
        newB, new_T = ticket_get_transactions(self.ticket_conf.username, self.ticket_conf.password, start_date=last_t_date, end_date=dt.datetime.now())

        self.balance = newB

        # list of database ticket transactions
        dbT = [t.ticket_transaction for t in self.transactions]

        # unique new transacitons
        uniqueNewT = [t for t in new_T if t not in dbT]


        # add new transactions (sorted by date) to database
        self.transactions += sorted([SyncedTransaction(t, True) for t in uniqueNewT],
                                    key=lambda t: t.ticket_transaction.date)
        self.last_update_ts = dt.datetime.now()

        return newB, uniqueNewT


    def sync(self) -> List[str]:
        T_ids = []
        for t in self.transactions:
            # ignore transactions that should not be synced or that are already synced
            if t.ynab_transaction_id != True:
                continue

            t_id = create_transaction(
                new_transaction=NewTransactionMsg(
                    t.ticket_transaction,
                    self.ynab_conf.account_id,
                    self.ynab_conf.budget_id
                ),
                api_key=self.ynab_conf.api_key
            )

            if t_id != '':
                t.ynab_transaction_id = t_id
                T_ids.append(t_id)
            else:
                warnings.warn(f'a transaction was not synced: {t}')
        self.last_sync_ts = dt.datetime.now()
        return T_ids
    


def load_sync(path: Path) -> Optional[Sync]:
    # TODO add validation
    if not path.exists():
        print("path does not exist")
        return None
    if not path.is_file():
        print("path is not a file")
        return None

    with path.open('rb') as f:
        return pickle.load(f)