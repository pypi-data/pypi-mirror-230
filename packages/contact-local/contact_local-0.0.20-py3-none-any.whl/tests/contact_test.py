import os
import sys
script_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_directory, '..'))

from dotenv import load_dotenv
from contact_api.contact_local import ContactsLocal
from logger_local.Logger import Logger
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from contact_api.contact_local import CONTACT_LOCAL_PYTHON_COMPONENT_ID
from contact_api.contact_local import CONTACT_LOCAL_PYTHON_COMPONENT_NAME


load_dotenv()


obj = {
    'component_id': CONTACT_LOCAL_PYTHON_COMPONENT_ID,
    'component_name': CONTACT_LOCAL_PYTHON_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'shavit.m@circ.zone'

}

logger = Logger.create_logger(object=obj)


def test_insert_select():

    logger.start()
    id = ContactsLocal.insert(
        "ai", "bye", "0539229102", "", "sami@gmail.com", "haifa", "sniper", "wha","hami")
    contactRes = ContactsLocal.get_contact_by_contact_id(id)
    contactRes is not None
    logger.end("contact added "+"ai")


def test_update():
    object1 = {
        'name': 'manana'
    }

    logger.start(object=object1)
    first_name = "manana"
    last_name = "banana"
    phone = "01291921"
    birthday = ""
    email = "sasa@gmail.com"
    location = "here"
    job_title = "jobber"
    organization = "what"
    display_as ="hamio"

    id = ContactsLocal.insert(first_name, last_name, phone,
                              birthday, email, location, job_title, organization,display_as)

    person_id = 11
    name_prefix = "sami"
    first_name = "ve"
    additional_name = 'sumo'
    job_title = "ars"

    ContactsLocal.update(person_id, name_prefix, first_name,
                         additional_name, job_title, id)
    contactRes = ContactsLocal.get_contact_by_contact_id(id)
    print(contactRes[3])
    assert contactRes[3] == person_id
    assert contactRes[6] == name_prefix
    assert contactRes[7] == first_name
    assert contactRes[8] == additional_name
    assert contactRes[17] == job_title
    logger.end("success")


def test_insert_multi():

    logger.start()
    contacts_to_insert = [
        {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '123-456-7890',
            'birthday': '',
            'email': 'john@example.com',
            'location': '123 Main St',
            'job_title': 'Software Developer',
            'organization': 'Tech Company',
            'display_as':'momo'
        },
        {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'phone': '987-654-3210',
            'birthday': '',
            'email': 'jane@example.com',
            'location': '456 Elm St',
            'job_title': 'Frontend Developer',
            'organization': 'Web Solutions',
            'display_as':'momo'

        }
    ]

    inserted_ids = ContactsLocal.insert_batch(contacts_to_insert)
    inserted_ids is not None
    logger.end("success")

test_insert_select()