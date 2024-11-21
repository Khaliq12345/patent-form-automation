import sys, os, pathlib
sys.path.append(
    pathlib.Path(os.getcwd()).parent.as_posix()
)
from nicegui import ui, app, events
from nicegui.ui import select
import constants
from constants import constants
from backend import state_service
import asyncio, json
from model import model
from bot import bot
from config import ADMIN_PASSWORD
from dateparser import parse


def is_logged_in(loginfo: dict):
    print(loginfo)
    if (loginfo.get('password') == ADMIN_PASSWORD):
        if parse(loginfo.get('exp')) > parse('now'):
            return True     
                

class PatentForm:
    def __init__(self, form_model: model.ApplicantModel | model.CompanyModel, is_admin: bool = False):
        self.state = {}
        self.form_model = form_model
        self.password = ''
        self.is_admin = is_admin
        self.log = {'log': 'Not started'}
        self.pdf_bytes = None
        
    
    def verify_password(self):
        if self.password == ADMIN_PASSWORD:
            app.storage.user['password'] = self.password
            app.storage.user['exp'] = parse('in 3 minutes').ctime()
            ui.navigate.reload()
        else:
            ui.notification(
                message='Incorrect password',
                type='negative',
                position='top',
                close_button=True,
            )
  
        
    def change_card_state(self):
        print('Refreshed!')
        self.custom_card_state.refresh()

            
    def model_validation(self, model: model.CompanyModel | model.ApplicantModel):
        model_json = model.model_dump()
        print(model_json)
        for x in model.model_fields:
            if x == 'state':
                print(f'State: {self.state}')
                if self.state:
                    model.model_fields[x].description = 'required'
                else:
                    model.model_fields[x].description = ''
            if model.model_fields[x].description == 'required':
                if (model_json[x] == '') or (not model_json[x]):
                    ui.notify(
                        f'Field: {x} is empty', 
                        position='top', 
                        type='negative',
                        close_button=True
                    )
                    raise ValueError(f'Field: {x} is empty')
      
      
    async def start_bot(self, model: model.ApplicantModel):
        self.spinner.visible = True
        try:
            self.model_validation(model)
            await bot.start_bot(model, self.log, self.pdf_bytes)
        except Exception as e:
            print(f'Error: {e}')
        finally:
            self.spinner.visible = False
        
        
    def save_to_local(self, model: model.CompanyModel):
        self.model_validation(model)
        with open('../companyInfo.json', 'w') as f:
            f.write(model.model_dump_json())
        ui.notify(
            message='Company Info updated',
            type='positive',
            position='top'
        )
    

    async def update_states(self, country_code, state_province: select):
        state_province.disable()
        self.spinner.visible = True
        self.state = await state_service.get_states(country_code)
        self.spinner.visible = False
        state_province.enable()
        state_province.set_options(self.state)

            
    @ui.refreshable
    def custom_card_state(self):
        if self.form_model.card_country == 'United States':
            print('Changed!')
            self.custom_select('State', options=constants.CARD_US_STATE, binder='card_state')
        else:
            self.custom_input('State', binder='card_state')
    

    def custom_input(
        self, 
        label: str, 
        binder: str, 
        hint: str = ''):
        return ui.input(
            label, 
            value=''
        ).classes("w-full").props(
            f'stack-label outlined hint="{hint}"'
        ).bind_value(self.form_model, binder)


    def custom_select(
        self, 
        label: str, 
        options: list[str], 
        binder: str, 
        hint: str = ''
        ) -> select:
        return (
            ui.select(options=options, label=label)
            .props(
                f'stack-label outlined hint="{hint}"',
            )
            .classes("w-full")
        ).bind_value(self.form_model, binder)


    def legal_form(self, text_class: str):
        ui.label("Legal Name").classes(text_class)
        self.custom_select(label='Prefix', 
            options=constants.PREFIXES, 
            hint='Optional',
            binder='prefix'
        )
        self.custom_input("Given name", binder='given_name')
        self.custom_input("Middle name", hint='Optional', binder='middle_name')
        self.custom_input("Family name", binder='family_name')
        self.custom_select(label='Suffix', 
            options=constants.SUFFIXES, 
            hint='Optional',
            binder='suffix'
        )
        
    
    def update_residency_state(self):
        self.set_residency_form.refresh()
    
    @ui.refreshable
    def set_residency_form(self):
        if self.form_model.residency_type == '1':
            self.form_model.residency_country = None
            self.custom_input('City', binder='residency_city')
            self.custom_select('State / province', 
                options=constants.US_STATES,
                binder='residency_state'
            )
            self.form_model.model_fields['residency_state'].description = 'required'
            self.form_model.model_fields['residency_city'].description = 'required'
            self.form_model.model_fields['residency_country'].description = ''
        elif self.form_model.residency_type == '2':
            self.form_model.residency_state = None
            self.custom_input('City', binder='residency_city')
            self.custom_select(
                'Country of residence', 
                constants.COUNTRIES, 
                binder='residency_country'
            )
            self.form_model.model_fields['residency_state'].description = ''
            self.form_model.model_fields['residency_city'].description = 'required'
            self.form_model.model_fields['residency_country'].description = 'required'
        else:
            self.form_model.residency_city = None
            self.form_model.residency_country = None
            self.form_model.residency_state = None
            self.form_model.model_fields['residency_state'].description = ''
            self.form_model.model_fields['residency_city'].description = ''
            self.form_model.model_fields['residency_country'].description = ''
    
     
    def residence_form(self, text_class: str):
        ui.label("Residence Information").classes(text_class)
        self.custom_select(
            'Residency Type', 
            options=constants.RESIDENCY_TYPE, 
            binder='residency_type'
        ).on_value_change(lambda: self.update_residency_state())
        self.set_residency_form()
        

    def mail_form(self, text_class: str):
        ui.label("Mailing Address").classes(text_class)
        self.custom_select('Country', 
            options=constants.COUNTRIES,
            binder='country'
        ).on_value_change(
            lambda x: self.update_states(x.value, state_province)
        )
        self.custom_input('Address 1', binder='address1')
        self.custom_input('Address 2', hint='Optional', binder='address2')
        self.custom_input('City', binder='city')
        state_province = self.custom_select(
            label='State / province', 
            options=self.state,
            binder='state'
        )
        self.custom_input('Postal code', hint='Optional', binder='postal_code')
     
     
    def application_form(self, text_class: str):
        ui.label("Application information").classes(text_class)
        self.custom_input('Title of invention', binder='invention_title')
        self.custom_input('Attorney docket', hint='Optional', binder='attorney_docket')
        self.custom_input('Entity status', hint='Optional', binder='entity_status')
        self.custom_input(
            label='Total number of drawing sheets', 
            hint='Optional',
            binder='total_number_of_drawing_sheet'
        )
        self.custom_input(
            label='Suggested figure for publication', 
            hint='Optional',
            binder='suggested_figure_for_publication'
        )
       
      
    def contact_form(self, text_class: str):
        ui.label("Contact information").classes(text_class)
        self.custom_input('Telephone number', binder='telephone', hint='Optional')
        self.custom_input('Fax number', binder='fax_number', hint='Optional')
        self.custom_input('Email Address 1', binder='email_address1')
        self.custom_input('Email Address 2', binder='email_address2', hint='Optional')
        self.custom_input('Email Address 3', binder='email_address3', hint='Optional')
        self.custom_input('Registration Number', binder='registration_number', hint='Optional')

      
    def payment_form(self, text_class: str):
        ui.label("Payment information").classes(text_class)
        self.custom_input('Credit Card Number', binder='credit_card_number')
        self.custom_input('Card Name', binder='card_name')
        self.custom_input('Security Code', binder='security_code')
        self.custom_select('Expiration Month', options=constants.CARD_MONTH, binder='exp_month')
        self.custom_select('Expiration Year', options=constants.CARD_YEAR, binder='exp_year')
        
    
    def billing_address(self, text_class: str):
        ui.label("Billing Address").classes(text_class)
        self.custom_input('Address Line 1', binder='card_address1')
        self.custom_input('Address Line 2', binder='card_address2', hint='Optional')
        self.custom_select('Country', options=constants.CARD_COUNTRY, binder='card_country').on_value_change(
            lambda: self.change_card_state()
        )
        self.custom_input('City', binder='card_city')
        self.custom_card_state()
        self.custom_input('Postal Code', binder='card_postalcode')
    
    
    def handle_upload(self, e: events.UploadEventArguments):
        self.pdf_bytes = e.content.read()
                
      
    def large_screen(self):
        with ui.element('div').classes('w-full p-5 max-md:hidden'):
            with ui.row().classes("grid grid-cols-3"):
                text_class = 'text-h5'
                with ui.column():
                    self.legal_form(text_class)
                with ui.column():
                    self.residence_form(text_class)
                with ui.column():
                    self.mail_form(text_class)
                with ui.column():
                    self.application_form(text_class)
                with ui.column():
                    ui.label('Upload Documents').classes(text_class)
                    ui.upload(label='Upload File', auto_upload=True).on_upload(
                        self.handle_upload
                    ).props('accept=.pdf')
                
            ui.button("Submit").classes('full-width m-5').props(
                'unelevated'
            ).on_click(lambda: self.start_bot(self.form_model))
            ui.label('Logs').classes('font-mono text-h4 text-center').bind_text(self.log, 'log')
            
            
    def small_screen(self):
        with ui.row().classes("w-full grid grid-cols-1 p-5 md:hidden"):
            text_class = 'text-h5'
            with ui.column():
                self.legal_form(text_class)
            with ui.column():
                self.residence_form(text_class)
            with ui.column():
                self.mail_form(text_class)
            with ui.column():
                self.application_form(text_class)
            with ui.column():
                ui.label('Upload Documents').classes(text_class)
                ui.upload(label='Upload File', auto_upload=True).on_upload(
                    self.handle_upload
                ).props('accept=.pdf')
            ui.button("Submit").classes('w-full').props(
                'unelevated'
            ).on_click(lambda: self.start_bot(self.form_model))
            ui.label('Logs').classes('font-mono text-h5 text-center').bind_text(self.log, 'log')


    def admin_large_screen(self):
        with ui.element('div').classes('w-full p-5 max-md:hidden'):
            with ui.row().classes("grid grid-cols-3"):
                text_class = 'text-h5'
                with ui.column():
                    self.legal_form(text_class)
                with ui.column():
                    self.residence_form(text_class)
                with ui.column():
                    self.mail_form(text_class)
                with ui.column():
                    self.contact_form(text_class)
                with ui.column():
                    self.payment_form(text_class)
                with ui.column():
                    self.billing_address(text_class)
        
            ui.button("Submit").classes('full-width m-5').props(
                'unelevated'
            ).on_click(lambda: self.save_to_local(self.form_model))
    
    
    def admin_small_screen(self):
        with ui.row().classes("w-full grid grid-cols-1 p-5 md:hidden"):
            text_class = 'text-h5'
            with ui.column():
                self.legal_form(text_class)
            with ui.column():
                self.residence_form(text_class)
            with ui.column():
                self.mail_form(text_class)
            with ui.column():
                self.contact_form(text_class)
            with ui.column():
                self.payment_form(text_class)
            with ui.column():
                self.billing_address(text_class)
            ui.button("Submit").classes('w-full').props(
                'unelevated'
            ).on_click(lambda: self.save_to_local(self.form_model))
    
    
    def main(self):
        if not self.is_admin:
            with ui.header().classes('justify-center'):
                ui.label("PATENT CENTER FORM").classes('text-h4')
                self.spinner = ui.spinner(type='cube', color='white', size='lg')
                self.spinner.visible = False
            self.large_screen()
            self.small_screen()
        else:
            with ui.header().classes('justify-center'):
                ui.label("ADMIN PATENT CENTER FORM").classes('text-h4')
                self.spinner = ui.spinner(type='cube', color='white', size='lg')
                self.spinner.visible = False
            if is_logged_in(app.storage.user):
                self.admin_large_screen()
                self.admin_small_screen()
            else:    
                with ui.row().classes('w-full') as login_page:
                    ui.input('Password', password=True).bind_value_to(self, 'password')
                    ui.button('Login').on_click(
                        lambda: self.verify_password()
                    )
            

@ui.page('/application/form', title='Form')
def user_page():
    ui.colors(primary="black")
    form = PatentForm(form_model=model.ApplicantModel())
    form.main()
    
@ui.page('/admin', title='Admin Form')
def admin_page():
    with open('../companyInfo.json', 'r') as f:
        json_string = f.read()
    json_data = json.loads(json_string)
    company_model = model.CompanyModel(**json_data)
    print(company_model)
    ui.colors(primary="black")
    form = PatentForm(form_model=company_model, is_admin=True)
    form.main()
    
    
ui.run(port=8080, storage_secret='Tester', title='Patent Form', favicon='📝')
