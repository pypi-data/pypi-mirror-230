from typing import List
from dotenv import load_dotenv
try:
    # Works when running the tests from this package
    from .constants_profile_reaction import *
    from profile_reaction_dto import ProfileReactionDto
except Exception:
    # Works when importing this module from another package
    from profile_reaction_local.src.constants import *
    from profile_reaction_local.src.profile_reaction_dto import ProfileReactionDto

load_dotenv()
from logger_local.Logger import Logger  # noqa: E402
from circles_local_database_python.generic_crud import GenericCRUD  # noqa: E402
from circles_local_database_python.connector import Connector   # noqa: E402

logger = Logger.create_logger(object=OBJECT_TO_INSERT_CODE)

ERROR_MESSAGE_FAILED_INSERT = 'error: Failed to insert profile_reaction'
ERROR_MESSAGE_FAILED_READ = 'error: Failed to read profile_reaction'
ERROR_MESSAGE_FAILED_UPDATE = 'error: Failed to update profile_reaction'
ERROR_MESSAGE_FAILED_DELETE = 'error: Failed to delete profile_reaction'

# ProfileReaction class provides methods for all the CRUD operations to the profile_reaction db


class ProfileReactions(GenericCRUD):

    @staticmethod
    def insert(reaction_id: int, profile_id: int) -> int:
        INSERT_PROFILE_REACTION_METHOD_NAME = 'insert_profile_reaction'
        logger.start(INSERT_PROFILE_REACTION_METHOD_NAME, object={'reaction_id': reaction_id, 'profile_id': profile_id})

        json_data = {'reaction_id': reaction_id, 'profile_id': profile_id}
        try:
            if reaction_id <= 0 or profile_id <= 0:
                message = 'error: Invalid argument value for'
                if reaction_id < 0:
                    message += ' reaction_id=' + str(reaction_id) + ', must be greater than 0. '
                if profile_id < 0:
                    message += ' profile_id=' + str(profile_id) + ', must be greater than 0. '
                logger.exception(message)
                logger.end(INSERT_PROFILE_REACTION_METHOD_NAME, object={
                           'reaction_id': reaction_id, 'profile_id': profile_id, 'message': message})
                raise Exception(message)
            generic_crud = GenericCRUD(PROFILE_REACTION_DATABASE_NAME)
            profile_reaction_id = generic_crud.insert(PROFILE_REACTION_TABLE_NAME, json_data)
        except Exception as e:
            logger.exception(ERROR_MESSAGE_FAILED_INSERT, object=e)
            logger.end(INSERT_PROFILE_REACTION_METHOD_NAME, object={
                       'reaction_id': reaction_id, 'profile_id': profile_id, 'message': ERROR_MESSAGE_FAILED_INSERT})
            raise Exception(ERROR_MESSAGE_FAILED_INSERT)

        logger.end(INSERT_PROFILE_REACTION_METHOD_NAME, object={'profile_reaction_id': profile_reaction_id})
        return profile_reaction_id

    @staticmethod
    def insert_with_dto(profile_reaction_dto: ProfileReactionDto) -> int:
        INSERT_PROFILE_REACTION_METHOD_NAME = 'insert_profile_reaction'
        logger.start(INSERT_PROFILE_REACTION_METHOD_NAME, object={
                     'profile_reaction_dto': profile_reaction_dto.to_json()})

        json_data = profile_reaction_dto.get_arguments()
        profile_reaction_dto_json = profile_reaction_dto.to_json()
        try:
            if profile_reaction_dto.get('reaction_id') <= 0 or profile_reaction_dto.get('profile_id') <= 0:
                message = 'error: Invalid argument value for'
                if profile_reaction_dto.get('reaction_id') < 0:
                    message += ' ProfileReactionDto\'s reaction_id=' + str(
                        profile_reaction_dto.get('reaction_id')) + ', must be greater than 0. '
                if profile_reaction_dto.get('profile_id') < 0:
                    message += ' ProfileReactionDto\'s profile_id=' + str(
                        profile_reaction_dto.get('profile_id')) + ', must be greater than 0. '
                logger.exception(message)
                logger.end(INSERT_PROFILE_REACTION_METHOD_NAME, object={
                           'profile_reaction_dto_json': profile_reaction_dto_json, 'message': message})
                raise Exception(message)
            generic_crud = GenericCRUD(PROFILE_REACTION_DATABASE_NAME)
            profile_reaction_id = generic_crud.insert(PROFILE_REACTION_TABLE_NAME, json_data)
        except Exception as e:
            logger.exception(ERROR_MESSAGE_FAILED_INSERT, object=e)
            logger.end(INSERT_PROFILE_REACTION_METHOD_NAME, object={
                       'profile_reaction_dto_json': profile_reaction_dto_json, 'message': ERROR_MESSAGE_FAILED_INSERT})
            raise Exception(ERROR_MESSAGE_FAILED_INSERT)

        logger.end(INSERT_PROFILE_REACTION_METHOD_NAME, object={'profile_reaction_id': profile_reaction_id})
        return profile_reaction_id

    @staticmethod
    def read_by_profile_reaction_id(profile_reaction_id: int) -> (int, int):
        READ_PROFILE_REACTION_METHOD_NAME = 'read_profile_reaction'
        logger.start(READ_PROFILE_REACTION_METHOD_NAME, object={'profile_reaction_id': profile_reaction_id})

        read_result = None
        try:
            if profile_reaction_id <= 0:
                message = 'error: Invalid argument value for profile_reaction_id=' + str(profile_reaction_id) + \
                    ', must be greater than 0. '
                logger.exception(message)
                logger.end(READ_PROFILE_REACTION_METHOD_NAME, object={
                           'profile_reaction_id': profile_reaction_id, 'message': message})
                raise Exception(message)
            generic_crud = GenericCRUD(PROFILE_REACTION_DATABASE_NAME)
            # TODO: check if it's possible to change to select_one
            read_result = generic_crud.select(
                PROFILE_REACTION_VIEW_NAME, "*", PROFILE_REACTION_ID_COLUMN_NAME,
                profile_reaction_id)
            if len(read_result) == 0:
                message = 'error: profile_reaction_id does not exist'
                logger.exception(message)
                logger.end(READ_PROFILE_REACTION_METHOD_NAME, object={
                           'profile_reaction_id': profile_reaction_id, 'message': message})
                raise Exception(message)
        except Exception as e:
            logger.exception(ERROR_MESSAGE_FAILED_READ, object=e)
            logger.end(READ_PROFILE_REACTION_METHOD_NAME, object={
                       'profile_reaction_id': profile_reaction_id, 'message': ERROR_MESSAGE_FAILED_READ})
            raise Exception(ERROR_MESSAGE_FAILED_READ)
        profile_id = read_result[0][PROFILE_ID_COLUMN_NUMBER]
        reaction_id = read_result[0][REACTION_ID_COLUMN_NUMBER]

        logger.end(READ_PROFILE_REACTION_METHOD_NAME, object={'profile_id': profile_id, 'reaction_id': reaction_id})
        return profile_id, reaction_id

    @staticmethod
    def read_dto_by_profile_reaction_id(profile_reaction_id: int) -> List[ProfileReactionDto]:
        READ_PROFILE_REACTION_METHOD_NAME = 'read_profile_reaction'
        logger.start(READ_PROFILE_REACTION_METHOD_NAME, object={'profile_reaction_id': profile_reaction_id})

        read_results = None
        try:
            if profile_reaction_id < 0:
                message = 'error: Invalid argument value for profile_reaction_id' + str(profile_reaction_id) + \
                    ', must be greater than 0. '
                logger.exception(message)
                logger.end(READ_PROFILE_REACTION_METHOD_NAME, object={
                           'profile_reaction_id': profile_reaction_id, 'message': message})
                raise Exception(message)
            generic_crud = GenericCRUD(PROFILE_REACTION_DATABASE_NAME)
            # TODO: check if it's possible to change to select_one
            read_results = generic_crud.select(
                PROFILE_REACTION_VIEW_NAME, "*", PROFILE_REACTION_ID_COLUMN_NAME,
                profile_reaction_id)
            if len(read_results) == 0:
                logger.exception(ERROR_MESSAGE_FAILED_READ)
                logger.end(READ_PROFILE_REACTION_METHOD_NAME, object={
                           'profile_reaction_id': profile_reaction_id, 'message': ERROR_MESSAGE_FAILED_READ})
                raise Exception(ERROR_MESSAGE_FAILED_READ)
        except Exception as e:
            message = 'error: Failed to read profile_reaction'
            logger.exception(message, object=e)
            logger.end(READ_PROFILE_REACTION_METHOD_NAME, object={
                       'profile_reaction_id': profile_reaction_id, 'message': message})
            raise Exception(message)
        list_profile_reaction_dto = []
        list_profile_reaction_dto_json = []
        for read_result in read_results:
            profile_id = read_result[PROFILE_ID_COLUMN_NUMBER]
            reaction_id = read_result[REACTION_ID_COLUMN_NUMBER]
            profile_reaction_dto = ProfileReactionDto(profile_id=profile_id, reaction_id=reaction_id)
            list_profile_reaction_dto.append(profile_reaction_dto)
            list_profile_reaction_dto_json.append(profile_reaction_dto.to_json())

        logger.end(READ_PROFILE_REACTION_METHOD_NAME, object={
                   'list_profile_reaction_dto_json': list_profile_reaction_dto_json})
        return list_profile_reaction_dto

    @staticmethod
    def read_all_by_profile_id(profile_id: int) -> list((int, int)):
        READ_ALL_BY_PROFILE_ID_METHOD_NAME = 'read_all_by_profile_id'
        logger.start(READ_ALL_BY_PROFILE_ID_METHOD_NAME, object={'profile_id': profile_id})

        read_result = None
        try:
            if profile_id < 0:
                message = 'error: Invalid argument value for profile_id=' + \
                    str(profile_id) + ', must be greater than 0. '
                logger.exception(message)
                logger.end(READ_ALL_BY_PROFILE_ID_METHOD_NAME, object={'profile_id': profile_id, 'message': message})
                raise Exception(message)
            generic_crud = GenericCRUD(PROFILE_REACTION_DATABASE_NAME)
            # TODO: fix this method not to use "*"
            read_result = generic_crud.select(
                PROFILE_REACTION_VIEW_NAME, "*", PROFILE_ID_COLUMN_NAME, profile_id)
        except Exception as e:
            logger.exception(ERROR_MESSAGE_FAILED_READ, object=e)
            logger.end(READ_ALL_BY_PROFILE_ID_METHOD_NAME, object={
                       'profile_id': profile_id, 'message': ERROR_MESSAGE_FAILED_READ})
            raise Exception(ERROR_MESSAGE_FAILED_READ)
        results_list = []
        for row in read_result:
            profile_reaction_id = row[PROFILE_REACTION_ID_COLUMN_NUMBER]
            reaction_id = row[REACTION_ID_COLUMN_NUMBER]
            results_list.append((profile_reaction_id, reaction_id))

        logger.end(READ_ALL_BY_PROFILE_ID_METHOD_NAME, object={'results_list': results_list})
        return results_list

    @staticmethod
    def read_all_by_reaction_id(reaction_id: int) -> list((int, int)):
        READ_ALL_BY_REACTION_ID_METHOD_NAME = 'read_all_by_reaction_id'
        logger.start(READ_ALL_BY_REACTION_ID_METHOD_NAME, object={'reaction_id': reaction_id})

        read_result = None
        try:
            if reaction_id < 0:
                message = 'error: Invalid argument value for reaction_id=' + \
                    str(reaction_id) + ', must be greater than 0. '
                logger.exception(message)
                logger.end(READ_ALL_BY_REACTION_ID_METHOD_NAME, object={'reaction_id': reaction_id, 'message': message})
                raise Exception(message)
            generic_crud = GenericCRUD(PROFILE_REACTION_DATABASE_NAME)
            # TODO: fix this method not to use "*"
            read_result = generic_crud.select(
                PROFILE_REACTION_VIEW_NAME, "*", REACTION_ID_COLUMN_NAME, reaction_id)
        except Exception as e:
            logger.exception(ERROR_MESSAGE_FAILED_READ, object=e)
            logger.end(READ_ALL_BY_REACTION_ID_METHOD_NAME, object={
                       'reaction_id': reaction_id, 'message': ERROR_MESSAGE_FAILED_READ})
            raise Exception(ERROR_MESSAGE_FAILED_READ)
        results_list = []
        for row in read_result:
            profile_reaction_id = row[PROFILE_REACTION_ID_COLUMN_NUMBER]
            profile_id = row[PROFILE_ID_COLUMN_NUMBER]
            results_list.append((profile_reaction_id, profile_id))

        logger.end(READ_ALL_BY_REACTION_ID_METHOD_NAME, object={'results_list': results_list})
        return results_list

    @staticmethod
    def update(profile_reaction_id: int, reaction_id: int, profile_id: int) -> None:
        UPDATE_PROFILE_REACTION_METHOD_NAME = 'update_profile_reaction'
        logger.start(UPDATE_PROFILE_REACTION_METHOD_NAME, object={
                     'profile_reaction_id': profile_reaction_id, 'reaction_id': reaction_id, 'profile_id': profile_id})

        connector = Connector.connect(PROFILE_REACTION_DATABASE_NAME)
        cursor = connector.cursor()
        query_update = "UPDATE profile_reaction_table SET profile_id = %s, reaction_id = %s WHERE profile_reaction_id = %s"
        cursor.execute(query_update, (profile_id, reaction_id, profile_reaction_id))
        connector.commit()

        logger.end(UPDATE_PROFILE_REACTION_METHOD_NAME)

    @staticmethod
    def delete_by_profile_reaction_id(profile_reaction_id: int) -> None:
        DELETE_PROFILE_REACTION_METHOD_NAME = 'delete_by_profile_reaction_id'
        logger.start(DELETE_PROFILE_REACTION_METHOD_NAME, object={'profile_reaction_id': profile_reaction_id})

        connector = Connector.connect(PROFILE_REACTION_DATABASE_NAME)
        cursor = connector.cursor()
        query_delete = "UPDATE profile_reaction_table SET end_timestamp = NOW() WHERE profile_reaction_id = %s"
        cursor.execute(query_delete, (profile_reaction_id,))
        connector.commit()

        logger.end(DELETE_PROFILE_REACTION_METHOD_NAME)
