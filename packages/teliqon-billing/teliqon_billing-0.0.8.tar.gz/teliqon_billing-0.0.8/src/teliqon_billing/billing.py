import requests
import json
from . import core
from . import types
from typing import List


class BillingAPI:
    def __init__(self, api_token: str, environment_id: int, api_url: str = None) -> None:
        assert isinstance(environment_id, int)
        self.api_token = api_token
        self.environment_id = environment_id
        self._requests_params = {
            "verify": False
        }
        if api_url is not None:
            assert api_token.endswith('/')

        self.api_url = api_url or core.API_URL
        self.__load_api_urls()
        self.ping()

    def __load_api_urls(self):
        self.__user_api_url = self.api_url + 'user/'
        self.__deposit_api_url = self.api_url + 'deposit/'
        self.__ping_api_url = self.api_url + 'ping/'
        self.__withdrawal_api_url = self.api_url + 'withdrawal/'
        self.__in_system_transfer_api_url = self.api_url + 'transfer/in/'
        self.__out_system_transfer_api_url = self.api_url + 'transfer/out/'
        self.__transactions_api_url = self.api_url + 'transactions/'
        self.__subscriptions_api_url = self.api_url + 'subscriptions/'

    @property
    def headers(self):
        return {
            "Authorization": f"Token {self.api_token}"
        } 

    def ping(self):
        params = {
            "environment": self.environment_id,
        }
        response = requests.get(
            url=self.__ping_api_url,
            headers=self.headers,
            params=params,
            **self._requests_params,
        )
        response.raise_for_status()
        assert json.loads(response.text)['status'] == 'ok'


    def create_user(self, unique_id: str, **kwars) -> types.BillingUser:
        body = {
            "environment": self.environment_id,
            "unique_id": unique_id,
            **kwars
        }

        response = requests.post(
            url=self.__user_api_url,
            headers=self.headers,
            json=body,
            **self._requests_params,
        )
        response.raise_for_status()

        data = json.loads(response.text)
        data.pop('environment')
        return types.BillingUser.from_dict(balance=0, **data)

    def update_user(self, unique_id: str, **kwars) -> types.BillingUser:
        body = {
            "environment": self.environment_id,
            "unique_id": unique_id,
            **kwars
        }
        response = requests.patch(
            url=self.__user_api_url,
            headers=self.headers,
            json=body,
            **self._requests_params,
        )
        response.raise_for_status()

        data = json.loads(response.text)
        data.pop('environment')
        return types.BillingUser.from_dict(**data)
    
    def get_user(self, unique_id: str) -> types.BillingUser:
        params = {
            "environment": self.environment_id,
            "unique_id": unique_id,
        }
        
        response = requests.get(
            url=self.__user_api_url,
            headers=self.headers,
            params=params,
            **self._requests_params,
        )
        response.raise_for_status()

        data = json.loads(response.text)
        data.pop('environment')
        return types.BillingUser.from_dict(**data)

    def get_users(self) -> List[types.BillingUser]:
        params = {
            "environment": self.environment_id,
        }
        
        response = requests.get(
            url=self.__user_api_url,
            headers=self.headers,
            params=params,
            **self._requests_params,
        )
        response.raise_for_status()

        data = json.loads(response.text)
        users = list()
        for user in data['users']:
            user.pop('environment')
            users.append(types.BillingUser.from_dict(**user))
        
        return users
        
    def deposit(self, unique_id: str, amount: float, comment: str = None) -> types.Transaction:
        body = {
            "environment": self.environment_id,
            "unique_id": unique_id,
            "amount": amount,
            "comment": comment or ''
        }

        response = requests.post(
            url=self.__deposit_api_url,
            headers=self.headers,
            json=body,
            **self._requests_params,
        )
        response.raise_for_status()

        data = json.loads(response.text)

        return types.Transaction.from_dict(**data)
    

    def withdrawal(self, unique_id: str, amount: float, comment: str = None, fee_on_sender: bool = False) -> types.Transaction:
        body = {
            "environment": self.environment_id,
            "unique_id": unique_id,
            "amount": amount,
            "comment": comment or '',
            "fee_on_sender": fee_on_sender
        }

        response = requests.post(
            url=self.__withdrawal_api_url,
            headers=self.headers,
            json=body,
            **self._requests_params,
        )
        response.raise_for_status()

        data = json.loads(response.text)

        return types.Transaction.from_dict(**data)
    
    def process_withdrawal(self, unique_id: str, transaction_id: int, status: bool = True) -> types.Transaction:
        body = {
            "environment": self.environment_id,
            "unique_id": unique_id,
            "transaction_id": transaction_id,
            "status": status
        }

        response = requests.patch(
            url=self.__withdrawal_api_url,
            headers=self.headers,
            json=body,
            **self._requests_params,
        )
        response.raise_for_status()

        data = json.loads(response.text)

        return types.Transaction.from_dict(**data)

    def in_system_transfer(self, from_unique_id: str, to_unique_id: str, amount: float, comment: str = None, fee_on_sender: bool = True) -> types.Transaction:
        body = {
            "environment": self.environment_id,
            "from_unique_id": from_unique_id,
            "to_unique_id": to_unique_id,
            "amount": amount,
            "comment": comment or '',
            "fee_on_sender": fee_on_sender
        }

        response = requests.post(
            url=self.__in_system_transfer_api_url,
            headers=self.headers,
            json=body,
            **self._requests_params,
        )
        response.raise_for_status()

        data = json.loads(response.text)

        return types.Transaction.from_dict(**data)

    def out_system_transfer(self, unique_id: str, amount: float, comment: str = None, fee_on_sender: bool = False, service_unique_id: str = None) -> types.Transaction:
        body = {
            "environment": self.environment_id,
            "unique_id": unique_id,
            "amount": amount,
            "comment": comment or '',
            "fee_on_sender": fee_on_sender,
            "service_unique_id": service_unique_id
        }

        response = requests.post(
            url=self.__out_system_transfer_api_url,
            headers=self.headers,
            json=body,
            **self._requests_params,
        )
        response.raise_for_status()

        data = json.loads(response.text)

        return types.Transaction.from_dict(**data)

    def get_user_transactions(self, unique_id: str) -> List[types.Transaction]:
        body = {
            "environment": self.environment_id,
            "unique_id": unique_id,
        }

        response = requests.get(
            url=self.__transactions_api_url,
            headers=self.headers,
            params=body,
            **self._requests_params
        )
        response.raise_for_status()

        data = json.loads(response.text)

        transactions = list()
        for transaction in data['transactions']:
            transactions.append(types.Transaction.from_dict(**transaction))
        
        return transactions

    
    def get_user_subscriptions(self, unique_id: str) -> List[types.Subscription]:
        body = {
            "environment": self.environment_id,
            "unique_id": unique_id,
        }

        response = requests.get(
            url=self.__subscriptions_api_url,
            headers=self.headers,
            params=body,
            **self._requests_params
        )
        response.raise_for_status()

        data = json.loads(response.text)

        subscriptions = list()
        for sub in data['subscriptions']:
            subscriptions.append(types.Subscription.from_dict(**sub))
        
        return subscriptions

    def new_user_subscription(self, unique_id: str, plan_unique_id: str) -> types.Subscription:
        body = {
            "environment": self.environment_id,
            "unique_id": unique_id,
            "plan_unique_id": plan_unique_id
        }

        response = requests.post(
            url=self.__subscriptions_api_url,
            headers=self.headers,
            json=body,
            **self._requests_params
        )
        response.raise_for_status()

        data = json.loads(response.text)

        return types.Subscription.from_dict(**data)


    def _patch_user_subscription(self, unique_id: str, plan_unique_id: str, **kwars) -> types.Subscription:
        body = {
            "environment": self.environment_id,
            "unique_id": unique_id,
            "plan_unique_id": plan_unique_id,
            **kwars
        }

        response = requests.patch(
            url=self.__subscriptions_api_url,
            headers=self.headers,
            json=body,
            **self._requests_params
        )
        response.raise_for_status()

        data = json.loads(response.text)

        return types.Subscription.from_dict(**data)

    def set_subscription_status(self, unique_id: str, plan_unique_id: str, is_disabled: bool) -> types.Subscription:
        return self._patch_user_subscription(unique_id, plan_unique_id, is_disabled=is_disabled)

    def set_subscription_count_value(self, unique_id: str, plan_unique_id: str, count: int) -> types.Subscription:
        return self._patch_user_subscription(unique_id, plan_unique_id, count=count)
    
    def increment_subscription_count_value(self, unique_id: str, plan_unique_id: str) -> types.Subscription:
        return self._patch_user_subscription(unique_id, plan_unique_id, count_event='inc')

    def decrement_subscription_count_value(self, unique_id: str, plan_unique_id: str) -> types.Subscription:
        return self._patch_user_subscription(unique_id, plan_unique_id, count_event='dec')
