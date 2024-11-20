from pydantic import BaseModel, Field, field_validator
from typing import Any
from typing_extensions import Self
    

class CustomerModel(BaseModel):
    prefix: str | None = None
    given_name: str | None = Field(default=None, description='required')
    middle_name: str | None = None
    family_name: str | None = Field(default=None, description='required')
    suffix: str | None = None
    residency_type: str | None = '1'
    residency_city: str | None = Field(default=None)
    residency_state: str | None = Field(default=None)
    residency_country: str | None = Field(default=None)
    country: str | None = Field(default=None, description='required')
    address1: str | None = Field(default=None, description='required')
    address2: str | None = None
    city: str | None = Field(default=None, description='required')
    state: str | None = None
    postal_code: str | None = None
    
    
class ApplicantModel(CustomerModel):
    invention_title: str | None = Field(default=None, description='required')
    attorney_docket: str | None = None
    entity_status: str | None = None
    total_number_of_drawing_sheet: str | None = None
    suggested_figure_for_publication: str | None = None
    
    
class CompanyModel(CustomerModel):
    telephone: str | None = None
    fax_number: str | None = None
    email_address1: str | None = Field(default=None, description='required')
    email_address2: str | None = None
    email_address3: str | None = None
    registration_number: str | None = Field(default=None, description='required')
    credit_card_number: str | None = Field(default=None, description='required')
    security_code: str | None = Field(default=None, description='required')
    card_name: str | None = Field(default=None, description='required')
    exp_month: str | None = Field(default=None, description='required')
    exp_year: str | None = Field(default=None, description='required')
    card_address1: str | None = Field(default=None, description='required')
    card_address2: str | None = None
    card_country: str | None = Field(default=None, description='required')
    card_city: str | None = Field(default=None, description='required')
    card_state: str | None = Field(default=None, description='required')
    card_postalcode: str | None = Field(default=None, description='required')
    
    
    
    