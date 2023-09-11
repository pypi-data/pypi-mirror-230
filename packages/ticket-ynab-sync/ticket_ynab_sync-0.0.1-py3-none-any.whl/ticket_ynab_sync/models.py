from dataclasses import dataclass
from pyticketfood import Transaction as TicketTransaction
from enum import Enum


@dataclass
class SyncedTransaction:
    ticket_transaction: TicketTransaction
    ynab_transaction_id: bool | str  # False = don't sync, True = should sync, but not synced, str = ynab_id of synced transaction

@dataclass
class YnabConfig:
    account_id: str
    budget_id: str
    api_key: str

@dataclass
class TicketConfig:
    username: str
    password: str


@dataclass
class NewTransactionMsg:
    ticket_transaction: TicketTransaction
    account_id: str
    budget_id: str