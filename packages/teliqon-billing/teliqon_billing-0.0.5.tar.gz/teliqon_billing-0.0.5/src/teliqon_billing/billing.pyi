from .types import BillingUser

class BillingApi:
    def create_user(self, unique_id: str, credit_limit: float = None, 
        first_name: str = None, last_name: str = None,
        mobile_number: str = None, work_number: str = None,
        email: str = None, company_name: str = None,
        country: str = None, city: str = None,
        address: str = None, zip_code: str = None,
        description: str = None) -> BillingUser: ...
    
    def update_user(self, unique_id: str, credit_limit: float = None, 
        first_name: str = None, last_name: str = None,
        mobile_number: str = None, work_number: str = None,
        email: str = None, company_name: str = None,
        country: str = None, city: str = None,
        address: str = None, zip_code: str = None,
        description: str = None) -> BillingUser: ...