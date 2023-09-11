from pathlib import Path
from .ticket_ynab_sync import Sync, load_sync
from .models import YnabConfig, TicketConfig
from .utils import input_bounded_int, input_from_list
import datetime as dt

import click
from getpass import getpass

@click.group()
def ticket2ynab():
    pass

@ticket2ynab.command()
@click.argument('path', type=click.Path())
def init(path: Path):
    if path.exists():
        print(f"given path already exists")
        return

    # ask for ticket creds, TODO validation, TODO test credentials work with a real call
    ticket_conf = TicketConfig(
        input('enter ticket username'),
        getpass('enter ticket password')
    )

    # ask for YNAB creds, TODO validation, TODO test credentials work with a real call
    ynab_conf = YnabConfig(
        input("enter account id"),
        input("enter budget id"),
        input("enter api key"),
    )

    s = Sync(ticket_conf, ynab_conf)
    s.save_state(path)


@ticket2ynab.command()
@click.argument('path', type=click.Path(exists=True))
def info(path: str):
    path: Path = Path(path)
    s = load_sync(path)
    if s is None:
        return

    # print general statistics
    print(f"balance: {s.balance}")
    print(f"total transactions: {len(s.transactions)}")
    n_synced, n_unsynced, n_no_sync = 0, 0, 0
    for t in s.transactions:
        if isinstance(t.ynab_transaction_id, str):
            n_synced += 1
        elif t.ynab_transaction_id == True:
            n_unsynced += 1
        elif t.ynab_transaction_id == False:
            n_no_sync += 1

    
    print(f"synced transactions: {n_synced}")
    print(f"unsynced transactions: {n_unsynced}")
    print(f"no sync transactions: {n_no_sync}")

    # print transctions from last N days
    N = 7
    ref_date = dt.datetime.now() - dt.timedelta(days=N)
    print(f"transactions from last {N} days:")
    print("date\tvalue\tdesc")
    for t in filter(lambda t: t.ticket_transaction.date >= ref_date, s.transactions):
        print(str(t.ticket_transaction.date), t.ticket_transaction.value, '\t', t.ticket_transaction.description)

@ticket2ynab.command()
@click.argument('path', type=click.Path(exists=True))
def update(path: str):
    path: Path = Path(path)
    s = load_sync(path)
    if s is None:
        return
    
    # check 
    # get new transactions from ticket
    balance, new_transactions = s.update()
    s.save_state(path)
    
    # print new transactions
    print(f"new balance: {balance}")
    print(f"new transactions: {len(new_transactions)}")
    for t in new_transactions:
        print(t)
    

@ticket2ynab.command()
@click.argument('path', type=click.Path(exists=True))
def sync(path: str):
    path: Path = Path(path)
    s = load_sync(path)
    if s is None:
        return
    
    # if this is the first sync, there might be old transactions that the user doesn't want to sync
    if s.last_sync_ts is None:
        T_unsynced = [t for t in s.transactions if isinstance(t.ynab_transaction_id, bool)]

        print(f"it seems this is the first sync\n"
              f"there are {len(T_unsynced)} transactions that can be synced\n")
        
        choice = input_from_list(f"do you wish to sync them all (y/n)?", ['y', 'n'])

        # list unsynced transaction and choose where to start syncing
        if choice == 'n':
            print("list of unsynced transactions:")
            for i, t in enumerate(T_unsynced):
                print(f"{i}\t{str(t.ticket_transaction.date)}\t{t.ticket_transaction.value}\t{t.ticket_transaction.description}")

            start_idx = input_bounded_int("enter the index of the first transactions to start syncing", 0, len(T_unsynced)-1)

            # mark transactions so they will not be synced
            for i,t in enumerate(T_unsynced):
                if i < start_idx:
                    t.ynab_transaction_id = False


    # try to sync all transactions that are marked to sync
    s.sync()
    s.save_state(path)