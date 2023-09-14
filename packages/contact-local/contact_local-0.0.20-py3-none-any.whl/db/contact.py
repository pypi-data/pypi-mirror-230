from dotenv import load_dotenv
from logger_local.Logger import Logger
from circles_local_database_python.connector import Connector
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from contact_api.contact_local import CONTACT_LOCAL_PYTHON_COMPONENT_ID
from contact_api.contact_local import CONTACT_LOCAL_PYTHON_COMPONENT_NAME

obj = {
    'component_id': CONTACT_LOCAL_PYTHON_COMPONENT_ID,
    'component_name': CONTACT_LOCAL_PYTHON_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'shavit.m@circ.zone'
}
logger = Logger.create_logger(object=obj)


def create_contact_table():
    connection = Connector.connect("contact")
    mycursor = connection.cursor()
    mycursor.execute("USE contact")

    # Create the contact_table
    mycursor.execute("""
                            CREATE TABLE IF NOT EXISTS contact_table (
                            id BIGINT UNSIGNED AUTO_INCREMENT,
                            owner_profile_id BIGINT UNSIGNED NULL,
                            account_name VARCHAR(255) NULL,
                            person_id BIGINT UNSIGNED NULL,
                            uploaded_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                            last_sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
                            name_prefix VARCHAR(255) NULL,
                            first_name VARCHAR(255) NULL,
                            additional_name VARCHAR(255) NULL,
                            last_name VARCHAR(255) NULL,
                            full_name VARCHAR(255) NULL,
                            name_suffix VARCHAR(255) NULL,
                            nickname VARCHAR(255) NULL,
                            display_as VARCHAR(255) NULL,
                            title VARCHAR(255) NULL,
                            organization VARCHAR(255) NULL,
                            organization_profile_id BIGINT UNSIGNED NULL,
                            job_title VARCHAR(255) NULL,
                            department VARCHAR(255) NULL,
                            notes TEXT NULL,
                            email1 VARCHAR(255) NULL,
                            email2 VARCHAR(255) NULL,
                            email3 VARCHAR(255) NULL,
                            phone1 VARCHAR(255) NULL,
                            phone2 VARCHAR(255) NULL,
                            phone3 VARCHAR(255) NULL,
                            address1_street VARCHAR(255) NULL,
                            address1_city VARCHAR(255) NULL,
                            address1_state VARCHAR(255) NULL,
                            address1_postal_code VARCHAR(255) NULL,
                            address1_country VARCHAR(255) NULL,
                            address2_street VARCHAR(255) NULL,
                            address2_city VARCHAR(255) NULL,
                            address2_state VARCHAR(255) NULL,
                            address2_postal_code VARCHAR(255) NULL,
                            address2_country VARCHAR(255) NULL,
                            birthday DATE NULL,
                            day INT UNSIGNED NULL,
                            month INT UNSIGNED NULL,
                            year INT UNSIGNED NULL,
                            cira bool NULL,
                            anniversary DATE NULL,
                            website1 VARCHAR(255) NULL,
                            website2 VARCHAR(255) NULL,
                            website3 VARCHAR(255) NULL,
                            photo_url VARCHAR(255) NULL,
                            photo_file_name VARCHAR(255) NULL,
                            source VARCHAR(255) NULL,
                            PRIMARY KEY(id),
                            FOREIGN KEY(owner_profile_id) REFERENCES profile.profile(id)
                            )
                        """)
    # commit change and Close the database connection
    connection.commit()
    mycursor.close()
