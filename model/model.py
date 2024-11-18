from pydantic import BaseModel, Field, field_validator
from typing import Any
from typing_extensions import Self
    

class CustomerModel(BaseModel):
    prefix: str | None = ''
    given_name: str = Field(default='', description='required')
    middle_name: str = ''
    family_name: str = Field(default='', description='required')
    suffix: str | None = ''
    residency_type: str = '1'
    residency_city: str = Field(default='', description='required')
    residency_state: str = Field(default='', description='required')
    country: str = Field(default='', description='required')
    address1: str = Field(default='', description='required')
    address2: str = ''
    city: str = Field(default='', description='required')
    state: str | None = ''
    postal_code: str = ''
    
    
class ApplicantModel(CustomerModel):
    invention_title: str = Field(default='', description='required')
    attorney_docket: str = ''
    entity_status: str = ''
    total_number_of_drawing_sheet: str = ''
    suggested_figure_for_publication: str = ''
    
    
class CompanyModel(CustomerModel):
    telephone: str = ''
    fax_number: str = ''
    email_address1: str = ''
    email_address2: str = ''
    email_address3: str = ''
    registration_number: str = Field(default='', description='required')
    credit_card_number: str = Field(default='', description='required')
    security_code: str = Field(default='', description='required')
    card_name: str = Field(default='', description='required')
    exp_month: str = Field(default='', description='required')
    exp_year: str = Field(default='', description='required')
    card_address1: str = Field(default='', description='required')
    card_address2: str = ''
    card_country: str = Field(default='', description='required')
    card_city: str = Field(default='', description='required')
    card_state: str = Field(default='', description='required')
    card_postalcode: str = Field(default='', description='required')
    
    
    
    