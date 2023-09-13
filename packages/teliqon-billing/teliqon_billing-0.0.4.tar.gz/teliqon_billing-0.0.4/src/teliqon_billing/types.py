from dataclasses import dataclass
from datetime import datetime


@dataclass
class BillingUser:
    unique_id: str
    credit_limit: float
    balance: float
    first_name: str
    last_name: str
    mobile_number: str
    work_number: str
    email: str
    company_name: str
    country: str
    city: str
    address: str
    zip_code: str
    description: str 



@dataclass
class Transfer:
    income: bool
    user: BillingUser

    def __post_init__(self):
        if self.user is not None:
            self.user = BillingUser(**self.user)


@dataclass
class OutSystemService:
    unique_id: str
    title: str
    desciption: str


@dataclass
class Transaction:
    id: int
    type: str
    status: str
    comment: str
    created_at: datetime
    amount: float
    fee: float
    balance_before: float
    balance_after: float
    transfer: Transfer
    out_system_service: OutSystemService

    def __post_init__(self):
        if self.transfer is not None:
            self.transfer = Transfer(**self.transfer)
        if self.out_system_service is not None:
            self.out_system_service = OutSystemService(**self.out_system_service)

        self.created_at = datetime.fromisoformat(self.created_at.rsplit('.', maxsplit=1)[0])


@dataclass
class SubscriptionPlan:
    unique_id: str
    out_system_service: OutSystemService
    first_payment_amount: float
    amount: float
    days_frequency: float

    def __post_init__(self): 
        if self.out_system_service is not None:
            self.out_system_service = OutSystemService(**self.out_system_service)


@dataclass
class Subscription:
    plan: SubscriptionPlan
    count: int
    amount: float
    comment: str
    first_payment_at: datetime
    next_payment_at: datetime
    is_active: bool
    is_disabled: bool

    def __post_init__(self):
        self.plan = SubscriptionPlan(**self.plan)
        self.first_payment_at = datetime.fromisoformat(self.first_payment_at.rsplit('.', maxsplit=1)[0])
        self.next_payment_at = datetime.fromisoformat(self.next_payment_at.rsplit('.', maxsplit=1)[0])