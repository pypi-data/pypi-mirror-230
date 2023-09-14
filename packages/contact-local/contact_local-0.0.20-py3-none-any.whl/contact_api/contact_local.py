from dotenv import load_dotenv
from logger_local.Logger import Logger
from circles_local_database_python.connector import Connector
from datetime import datetime
from circles_local_database_python.generic_crud import GenericCRUD
from logger_local.LoggerComponentEnum import LoggerComponentEnum
load_dotenv()
CONTACT_LOCAL_PYTHON_COMPONENT_ID = 123
CONTACT_LOCAL_PYTHON_COMPONENT_NAME = 'contact-local'

obj = {
    'component_id': CONTACT_LOCAL_PYTHON_COMPONENT_ID,
    'component_name': CONTACT_LOCAL_PYTHON_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'shavit.m@circ.zone'
}

logger = Logger.create_logger(object=obj)


class ContactsLocal(GenericCRUD):

    def __init__(self) -> None:
        pass

    @staticmethod
    def insert(first_name: str, last_name: str, phone: str,
               birthday: str, email: str, location: str, job_title: str, organization: str,display_as:str) -> int:
        try:
            connection = Connector.connect("contact")
            object1 = {
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'birthday': birthday,
                'email': email,
                'location': location,
                'job_title': job_title,
                'organization': organization,
                'display_as':display_as

            }
            logger.start(object=object1)
            id = None

            cursor = connection.cursor(buffered=True)
            insert_query = """
            INSERT INTO contact_table (
                first_name,
                last_name,
                phone1,
                birthday,
                email1,
                address1_street,
                job_title,
                organization,
                display_as
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s,%s,%s
            )
            """

            data_values = (
                first_name,
                last_name,
                phone,
                birthday,
                email,
                location,
                job_title,
                organization,
                display_as
            )
            cursor.execute(insert_query, data_values)
            contact_id = cursor.lastrowid()

            connection.commit()
            cursor.close()
            logger.end("contact added", object={'contact_id': contact_id})
        except Exception as err:
            logger.exception(f"Contact.insert Error: {err}", object=err)
            cursor.close()
            logger.end()
            raise
        return contact_id

    @staticmethod
    def update(person_id: int, name_prefix: str, first_name: str, additional_name: str, job_title: str,
               contact_id: int) -> None:
        try:
            connection = Connector.connect("contact")

            object1 = {
                'person_id': person_id,
                'name_prefix': name_prefix,
                'first_name': first_name,
                'additional_name': additional_name,
                'job_title': job_title,
                'contact_id': contact_id
            }
            logger.start(object=object1)
            cursor = connection.cursor(buffered=True)
            update_query = """
            UPDATE contact_table
            SET
                person_id = %s,
                name_prefix = %s,
                first_name = %s,
                additional_name = %s,
                job_title=%s
            WHERE
                contact_id = %s
            """

            data_values = (
                person_id,
                name_prefix,
                first_name,
                additional_name,
                job_title,
                contact_id
            )

            cursor.execute(update_query, data_values)
            connection.commit()
            cursor.close()
            logger.end("contact updated", object={'contact_id': contact_id})
        except Exception as err:
            logger.exception(f"Contact.update Error: {err}", object=err)
            cursor.close()
            logger.end()
            raise

    @staticmethod
    def delete(contact_id: any) -> None:
        try:
            object1 = {
                'contact_id': contact_id,
            }
            logger.start(object=object1)
            connection = Connector.connect("contact")
            # bufferd=true because it fixes sql unread error
            cursor = connection.cursor(buffered=True)
            update_query = """
            UPDATE contact_table
            SET
                end_timestamp = NOW()
            WHERE
                contact_id = %s
        """
            data_values = (contact_id,)

            cursor.execute(update_query, data_values)
            connection.commit()
            cursor.close()
            logger.end("contact deleted", object={'contact_id': contact_id})
        except Exception as err:
            logger.exception(f"Contact.delete Error: {err}", object=err)
            cursor.close()
            logger.end()
            raise

    @staticmethod
    def insert_batch(contact_list: list) -> list:
        try:

            object1 = {
                'listToInsert': contact_list
            }
            logger.start(object=object1)
            connection = Connector.connect("contact")
            cursor = connection.cursor(buffered=True)
            insert_query = """
            INSERT INTO contact_table (
                first_name,
                last_name,
                phone1,
                birthday,
                email1,
                address1_street,
                job_title,
                organization
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            """

            inserted_ids = []

            for contact in contact_list:
                data_values = (
                    contact['first_name'],
                    contact['last_name'],
                    contact['phone'],
                    contact['birthday'],
                    contact['email'],
                    contact['location'],
                    contact['job_title'],
                    contact['organization']
                )
                cursor.execute(insert_query, data_values)
                inserted_ids.append(cursor.lastrowid)

            connection.commit()
            cursor.close()
        except Exception as err:
            logger.exception(f"Error: {err}", err)
            cursor.close()
            logger.end()
            raise
        finally:
            my_list = [str(item) for item in inserted_ids]
            inserted_ids = ", ".join(my_list)
            logger.end({'inserted_ids': inserted_ids})
            return inserted_ids

    def get_contact_by_contact_id(contact_id: int) -> tuple:
        try:
            connection = Connector.connect("contact")
            cursor = connection.cursor(buffered=True)
            select_query = """
            SELECT * FROM contact_view
            WHERE
                contact_id = %s
            """

            cursor.execute(select_query, (contact_id,))
            contact_result = cursor.fetchone()
            cursor.close()
        except Exception as err:
            logger.exception(
                f"Contact.get_contact_by_id Error: {err}", object=err)
            cursor.close()
            logger.end()
            raise
        return contact_result
