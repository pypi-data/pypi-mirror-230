from typing import Optional

from pyticketfood import Transaction as TicketTransaction
from .models import SyncedTransaction, NewTransactionMsg

import time
import ynab_api
from ynab_api.api import transactions_api
from ynab_api.model.error_response import ErrorResponse
from ynab_api.model.save_transactions_response import SaveTransactionsResponse
from ynab_api.model.save_transactions_wrapper import SaveTransactionsWrapper

from ynab_api.model.save_transaction import SaveTransaction

import warnings
import datetime


def create_transaction(new_transaction: NewTransactionMsg, api_key: str) \
    -> Optional[str]:
    '''
        Returns a SyncedTransaction if successfull or None if not
    '''

    nt = new_transaction

    # Defining the host is optional and defaults to https://api.youneedabudget.com/v1
    # See configuration.py for a list of all supported configuration parameters.
    configuration = ynab_api.Configuration(
        host = "https://api.youneedabudget.com/v1"
    )

    # The client must configure the authentication and authorization parameters
    # in accordance with the API server security policy.
    # Examples for each auth method are provided below, use the example that
    # satisfies your auth use case.

    # Configure API key authorization: bearer
    configuration.api_key['bearer'] = api_key
    configuration.api_key_prefix['bearer'] = 'Bearer'


    # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
    # configuration.api_key_prefix['bearer'] = 'Bearer'

    # Enter a context with an instance of the API client
    with ynab_api.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = transactions_api.TransactionsApi(api_client)
        # budget_id = budget_id # str, none_type | The id of the budget. \"last-used\" can be used to specify the last used budget and \"default\" can be used if default budget selection is enabled (see: https://api.youneedabudget.com/#oauth-default-budget).
        data = SaveTransactionsWrapper(
            transaction=SaveTransaction(
                account_id=nt.account_id,
                date=nt.ticket_transaction.date.date(),
                amount=int(nt.ticket_transaction.value*1000),  # 1000 = 1€
                payee_name=nt.ticket_transaction.description,
            )
        ) # SaveTransactionsWrapper | The transaction or transactions to create.  To create a single transaction you can specify a value for the `transaction` object and to create multiple transactions you can specify an array of `transactions`.  It is expected that you will only provide a value for one of these objects.

        # example passing only required values which don't have defaults set
        try:
            # Create a single transaction or multiple transactions
            api_response = api_instance.create_transaction(nt.budget_id, data)
            t_id = api_response.data.transaction.id
            return t_id
        except ynab_api.ApiAttributeError as e:
            warnings.warn(f"Not possible to extract transaction id from response: ")
        except ynab_api.ApiException as e:
            warnings.warn("Exception when calling TransactionsApi->create_transaction: %s\n" % e)

        return None


def main():
    import os
    BUDGET_ID = os.environ['BUDGET_ID']
    ACCOUNT_ID = os.environ['ACCOUNT_ID']
    API_KEY = os.environ['API_KEY']
    t = create_transaction(
        NewTransactionMsg(
            TicketTransaction(
                date=datetime.datetime.now(),
                description="Test",
                value=1.27,
            ),
            account_id=ACCOUNT_ID,
            budget_id=BUDGET_ID),
        API_KEY
    )

    if t is None:
        print("not possible to create message")
    else:
        print(t)



if __name__ == "__main__":
    main()