import logging
import time
import urllib.parse
from hashlib import sha256
from hmac import new
from base64 import b64encode
import requests

from komora_syncer.config import get_config

# Log Warnings and higher errors from imported modules
logging.getLogger(requests.__name__).setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class KomoraConnection:
    """
    A class for establishing and managing a connection to a Komora instance.
    """

    @staticmethod
    def checkout_url(model, params=""):
        """
        Constructs a signed URL for accessing a Komora API endpoint.

        Args:
            model (str): The name of the API endpoint.
            params (str): Optional query parameters to include in the URL.

        Returns:
            str: The signed URL.
        """
        private_key, sign_app = get_config()['komora']['PRIVATE_KEY'], get_config()[
            'komora']['SIGN_APP']
        komora_url = get_config()['komora']['KOMORA_API_URL']

        base_url = f"{komora_url}/{model}"
        signDate = str(int(time.time()))

        if params:
            params = f"?{params}&signApp={sign_app}&signDate={signDate}"
        else:
            params = f"?signApp={sign_app}&signDate={signDate}"

        digest = new(bytes(private_key, "utf-8"),
                     msg=str.encode(params), digestmod=sha256).digest()
        signature = b64encode(digest).decode()
        parsed_signature = urllib.parse.quote_plus(signature)

        result_url = f"{base_url}{params}&signHash={parsed_signature}"
        return result_url

    @staticmethod
    def __get_page(api, page, page_size, filter_params=""):
        """
        Retrieves a page of records from a Komora API endpoint.

        Args:
            api (str): The name of the API endpoint.
            page (int): The page number to retrieve.
            page_size (int): The number of records per page.
            filter_params (str): Optional filter parameters to include in the request.

        Returns:
            tuple: A tuple containing the list of records and the total number of records.
        """
        params = f"Page={page}&PageSize={page_size}"
        if filter_params:
            params = params + "&" + filter_params

        url = KomoraConnection.checkout_url(api, params)

        try:
            response = requests.get(url)
            response.raise_for_status()
        except Exception as e:
            logger.exception("Unable to get page")
            logger.debug(f"URL {url}")
            raise e
        else:
            response = response.json()
            result = response.get('data', [])

            # Check number of all records
            total = response.get('total', 0)

            return result, int(total)

    @staticmethod
    def get_records(api, filter_params=""):
        """
        Retrieves all records from a Komora API endpoint.

        Args:
            api (str): The name of the API endpoint.
            filter_params (str): Optional filter parameters to include in the request.

        Returns:
            list: A list of all records from the API endpoint.
        """
        page_size = 100
        page = 0

        try:
            # load first page
            record_list, total = KomoraConnection.__get_page(
                api, page, page_size, filter_params=filter_params)

            # if less records are returned than total number of records -> get rest of records
            while len(record_list) < total:
                page += 1
                try:
                    next_data = KomoraConnection.__get_page(
                        api, page, page_size, filter_params=filter_params)[0]
                    record_list.extend(next_data)
                except Exception as e:
                    logger.exception("Unable to get page")
                    logger.debug(f"API {api}, page {page}")
                    break

            if len(record_list) == total:
                return record_list
            # TODO: generate proper error
            else:
                raise Exception
        except Exception as e:
            logger.exception("Unable to get records")
            logger.debug(f"API {api}")
