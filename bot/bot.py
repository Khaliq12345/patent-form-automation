import os, sys, pathlib
sys.path.append(pathlib.Path(os.getcwd()).parent.as_posix())

from playwright.async_api import async_playwright, expect, Page
import asyncio
from model.model import CompanyModel, ApplicantModel
from typing import Union
import logging
import re, json
from pathlib import Path
from dateparser import parse


def load_company_model() -> CompanyModel:
    with open('../companyInfo.json', 'r') as f:
        json_string = f.read()
        json_data = json.loads(json_string)
        company_model = CompanyModel(**json_data)
    return company_model


async def add_new_inventor(page: Page, form_model: Union[ApplicantModel, CompanyModel]):
    await page.get_by_role('button', name='Add new inventor').click()
    await expect(page.locator('div[class="progress-loader"]').first).to_be_hidden()
    if form_model.prefix:
        await page.select_option('select[formcontrolname="prefixName"]', form_model.prefix)
    await page.fill('input[formcontrolname="firstName"]', form_model.given_name)
    if form_model.middle_name:
        await page.fill('input[formcontrolname="middleName"]', form_model.middle_name) #optional
    await page.fill('input[formcontrolname="lastName"]', form_model.family_name)
    if form_model.suffix:
        await page.select_option('select[formcontrolname="suffixName"]', form_model.suffix) #optional

    #Residence Information
    await page.select_option('select[formcontrolname="residencyTypeIdentifier"]', '1')
    await page.fill('input[formcontrolname="residencyCityName"]', form_model.residency_city)
    await page.select_option('select[formcontrolname="residencyRegionCode"]', form_model.residency_state)

    #Mailing Address
    await page.select_option('select[formcontrolname="countryCode"]', form_model.country)
    await page.fill('input[formcontrolname="addressLineOneText"]', form_model.address1)
    if form_model.address2:
        await page.fill('input[formcontrolname="addressLineTwoText"]', form_model.address2) #optional
    await page.fill('input[formcontrolname="cityName"]', form_model.city)
    await expect(page.locator('div[class="progress-loader"]').first).to_be_hidden()
    await page.select_option('select[formcontrolname="geographicRegionCode"]', form_model.state)
    await page.fill('input[formcontrolname="postalCode"]', form_model.postal_code)
    await page.locator('button[id="btn_add"]').first.click()
    await expect(page.locator('div[class="progress-loader"]').first).to_be_hidden()
    

async def add_correspondance(page: Page, form_model: CompanyModel):
    await page.select_option('select[formcontrolname="corrCountryCode"]', form_model.country)
    await page.fill('input[formcontrolname="nameLineOneText"]', form_model.given_name)
    await page.fill('input[formcontrolname="nameLineTwoText"]', form_model.family_name) #optional
    await page.fill('input[formcontrolname="addressLineOneText"]', form_model.address1)
    await page.fill('input[formcontrolname="addressLineTwoText"]', form_model.address2) #optional
    await page.fill('input[formcontrolname="cityName"]', form_model.city)
    await page.select_option('select[formcontrolname="regionCode"]', form_model.state)
    await page.fill('input[formcontrolname="postalCode"]', form_model.postal_code) #optional
    await page.fill('input[formcontrolname="correspondencePhoneNumber"]', form_model.telephone) #optional
    await page.fill('input[formcontrolname="correspondenceFaxNumber"]', form_model.fax_number) #optional
    await page.fill('input[formcontrolname="correspondenceEmailAddress0"]', form_model.email_address1) #optional
    await page.fill('input[formcontrolname="correspondenceEmailAddress1"]', form_model.email_address2) #optional
    await page.fill('input[formcontrolname="correspondenceEmailAddress2"]', form_model.email_address3) #optional


async def add_application(page: Page, form_model: ApplicantModel):
    await page.fill('textarea[formcontrolname="inventionTitle"]', form_model.invention_title) #optional
    await page.fill('input[formcontrolname="attorneyDocketNumber"]', form_model.attorney_docket) #optional
    await page.select_option('select[formcontrolname="entityStatus"]', form_model.entity_status)  #optional
    await page.fill('input[formcontrolname="drawingSheetTotalQuantity"]', form_model.total_number_of_drawing_sheet)
    await page.fill('input[formcontrolname="suggestedPublicationFigureText"]', form_model.suggested_figure_for_publication)


async def go_to_next_section(page: Page, click_continue: bool = False):
    if click_continue:
        await page.click('.continue-btn')
    else:
        await page.get_by_text('Next section').click()
    await expect(page.locator('div[class="progress-loader"]').first).to_be_hidden()


async def add_new_applicant_assignee(page: Page, form_model: CompanyModel, is_applicant: bool = True):
    await page.click('input[formcontrolname="organizationIndicator"]')
    if is_applicant:
        await page.select_option('select[formcontrolname="applicantType"]', '3')
    await page.fill('input[formcontrolname="organizationName"]', form_model.given_name)

    await page.select_option('select[formcontrolname="countryCode"]', form_model.country)
    await page.fill('input[formcontrolname="addressLineOneText"]', form_model.address1)
    await page.fill('input[formcontrolname="addressLineTwoText"]', form_model.address2) #optional
    await page.fill('input[formcontrolname="cityName"]', form_model.city)
    await page.select_option('select[formcontrolname="geographicRegionCode"]', form_model.state)
    await page.fill('input[formcontrolname="postalCode"]', form_model.postal_code)
    await page.fill('input[formcontrolname="phoneNumber"]', form_model.telephone) #optional
    await page.fill('input[formcontrolname="faxNumber"]', form_model.fax_number) #optional
    await page.fill('input[formcontrolname="emailAddressText"]', form_model.email_address1) #optional
    await page.locator('button[id="btn_add"]').first.click()
    await expect(page.locator('div[class="progress-loader"]').first).to_be_hidden()


async def add_signature(page: Page, form_model: CompanyModel):
    await page.fill('input[formcontrolname="signatureText"]', f'/{form_model.given_name}/')
    await page.fill('input[formcontrolname="firstName"]', form_model.given_name)
    await page.fill('input[formcontrolname="lastName"]', form_model.family_name)
    await page.fill('input[formcontrolname="registrationText"]', form_model.registration_number)
    

async def review_submit(page: Page, form_model: CompanyModel):
    await page.fill('input[formcontrolname="firstName"]', form_model.given_name)
    await page.fill('input[formcontrolname="lastName"]', form_model.family_name)
    await page.fill('input[formcontrolname="email"]', form_model.email_address1)
    await page.click('button[id="btnSubmit"]')
    await expect(page.locator('div[class="progress-loader"]').first).to_be_hidden()


async def payment_form(page: Page, form_model: CompanyModel, logger: dict):
    log_info(logger=logger, info=f'Filling the credit card information')
    await page.get_by_label("Credit Card Number Input Field").fill(form_model.credit_card_number)
    await page.get_by_label("Card Security Code *").fill(form_model.security_code)
    await page.get_by_label("Name on Card *").fill(form_model.card_name)
    await page.get_by_label("Expiration Month").select_option(label=form_model.exp_month)
    await page.get_by_label("Expiration Year").select_option(label=form_model.exp_year)
    log_info(logger=logger, info=f'Filling the Billing address information')
    await page.get_by_label("Address Line 1 *").fill(form_model.address1)
    await page.get_by_label("Address Line 2").fill(form_model.address2)
    await page.locator("div").filter(has_text=re.compile(r"^Country \*$")).locator("span").nth(1).click()
    await page.get_by_role("option", name=form_model.card_country, exact=True).click()
    await page.get_by_label("City *").fill(form_model.card_city)
    if form_model.card_country == 'United States':
        await page.locator("div").filter(
            has_text=re.compile(r"^State / Region \*$")
        ).locator("span").nth(1).click()
        await page.get_by_role("option", name=form_model.card_state).click()
    else:
        await page.get_by_label("State / Region *").fill(form_model.card_state)
    await page.get_by_label("Zip / Postal Code *").fill(form_model.card_postalcode)
    await page.get_by_role("button", name="Submit Payment").click()
    log_info(logger=logger, info=f'Payment submitted, now waiting for 1 minutes to complete all')
    await page.wait_for_timeout(60000)
    if await page.get_by_role('button', name='No Thanks').is_visible():
        await page.get_by_role('button', name='No Thanks').click()
    if await page.locator('div[class="mb-2 alert alert-danger"]').first.is_visible():
        log_info(logger=logger, info="Payment failed")
        return False
    else:
        log_info(logger=logger, info="Successfull payment")
        return True


async def save_info(
    page: Page, 
    customer_model: ApplicantModel, 
    company_model: CompanyModel, 
    is_paid: bool
    ):
    current_date = parse('now').strftime('%Y%m%d')
    application_string = await page.get_by_text("Application #").first.text_content()
    application_string = application_string.replace('Application #  ', '').replace('/', '').replace(',', '')
    file_name = f'{customer_model.given_name}{customer_model.family_name}-{application_string}-{current_date}'
    folder = Path(f'../informations/{file_name}')
    folder.mkdir(exist_ok=True)
    await page.pdf(path=f'{folder}/{file_name}.pdf')
    await page.screenshot(path=f'{folder}/{file_name}.png', full_page=True)
    model_info = {
        'customer': json.loads(customer_model.model_dump_json()),
        'company': json.loads(company_model.model_dump_json()),
        'success': is_paid,
    }
    with open(f'{folder}/{file_name}.json', 'w') as f:
        f.write(json.dumps(model_info))
    print('Data Saved')


def log_info(info, logger):
    print(info)
    logger['log'] = info


async def start_bot(customer_model: ApplicantModel, logger: dict):
    company_model = load_company_model()
    log_info(logger=logger, info="Running")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(slow_mo=300)
            page = await browser.new_page()
            await page.goto('https://patentcenter.uspto.gov/', wait_until='load')
            await expect(page.locator('div[class="progress-loader"]').first).to_be_hidden()
            log_info(logger=logger, info="Page LOADED")

            await page.get_by_role("button", name="New submission", exact=True).click()
            await page.get_by_role("link", name="Utility-Provisional").click()
            await expect(page.get_by_role("button", name="Continue")).to_be_visible(timeout=120000)
            await page.get_by_role("button", name="Continue").click()
            await expect(page.locator('div[class="progress-loader"]').first).to_be_hidden()
            await expect(page.locator('.web-ads-btn').first).to_be_enabled(timeout=120000)
            await page.click('.web-ads-btn')
            await expect(page.locator('div[class="progress-loader"]').first).to_be_hidden()
            log_info(logger=logger, info="Web ADS Selected")

            #First Form
            log_info(logger=logger, info="Adding customer inventor")
            await add_new_inventor(page, customer_model)
            log_info(logger=logger, info="Customer inventor added")
            
            log_info(logger=logger, info="Adding company inventor")
            await add_new_inventor(page, company_model)
            log_info(logger=logger, info="Company inventor added")
            
            #Second Form
            log_info(logger=logger, info="Adding correspondance and applicaton")
            await go_to_next_section(page)
            await page.get_by_text('provide a physical address').click()
            await add_correspondance(page, company_model)
            await add_application(page, customer_model)
            log_info(logger=logger, info="Done Adding correspondance and applicaton")
            
            #Third Form
            log_info(logger=logger, info="Checking boxes")
            await go_to_next_section(page)
            await go_to_next_section(page)
            await go_to_next_section(page)
            await page.click('input[id="chk-pdx"]')
            await page.click('input[id="chk-epo"]')
            log_info(logger=logger, info="Done Checking boxes")
            
            #Fourth Form
            log_info(logger=logger, info="Adding new applicant")
            await go_to_next_section(page)
            await page.get_by_role('button', name='Add new applicant').click()
            await add_new_applicant_assignee(page, company_model)
            log_info(logger=logger, info="Done adding new applicant")
            
            #Fifth Form
            log_info(logger=logger, info="Adding new assignee")
            await go_to_next_section(page)
            await page.get_by_role('button', name='Add new assignee').click()
            await add_new_applicant_assignee(page, company_model, is_applicant=False)
            log_info(logger=logger, info="Done adding new assignee")
            
            #Sixth Form
            log_info(logger=logger, info="Adding signature")
            await go_to_next_section(page)
            await go_to_next_section(page)
            await add_signature(page, company_model)
            log_info(logger=logger, info="Done adding signature")
            
            #Seventh Form
            log_info(logger=logger, info="Uploading pdf")
            await go_to_next_section(page, click_continue=True)
            #upload file
            await go_to_next_section(page, click_continue=True)
            log_info(logger=logger, info="Done Uploading pdf")
            
            #Eight Form
            log_info(logger=logger, info="Choosing payment type")
            await page.get_by_text("Small").click()
            await page.fill('input[formcontrolname="pageTotalQuantity"]', '2')
            log_info(logger=logger, info="Done Choosing payment type")
            
            #Nineth Form
            await go_to_next_section(page, click_continue=True)
            await page.click('input[id="chkBx_0"]')
            
            #Tenth Form
            log_info(logger=logger, info="Reviewing")
            await go_to_next_section(page, click_continue=True)
            await review_submit(page, company_model)
            log_info(logger=logger, info="Done Reviewing")
            
            #Pay Form
            log_info(logger=logger, info="Processing payment")
            await page.click('button[id="btn_fees"]')
            await expect(page.get_by_role('button', name='Pay as a guest').first).to_be_visible(timeout=100000)
            await page.get_by_role('button', name='Pay as a guest').click()
            await page.wait_for_load_state(timeout=100000)
            is_paid = await payment_form(page, company_model, logger)
            
            await save_info(page, customer_model, company_model, is_paid=is_paid)

            #await page.wait_for_timeout(100000)
            await browser.close()
    except Exception as e:
       log_info(logger=logger, info=f"Error: {e}")
        
if __name__ == '__main__':
    asyncio.run(start_bot())