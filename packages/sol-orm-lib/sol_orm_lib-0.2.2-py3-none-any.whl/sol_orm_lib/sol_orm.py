import os
import sys
import urllib.parse

import requests
from loguru import logger

from .models import *

logger.remove()
logger.add(sys.stdout, colorize=True, 
           format="<le>[{time:DD-MM-YYYY HH:mm:ss}]</le> <lvl>[{level}]: {message}</lvl>", 
           level="INFO")


class SolORM:
    """Interface with the SOL database API.

    This class provides methods to interact with the SOL database API for adding, retrieving, and managing various entities.

    Attributes:
        add_paths (dict): A dictionary mapping entity classes to their corresponding API paths for adding entities.
        get_paths (dict): A dictionary mapping entity classes to their corresponding API paths for retrieving entities.
        util_paths (dict): A dictionary mapping utility methods to their corresponding API paths.

    Methods:
        __init__: Initialize the SolORM instance.
        add_entity: Add an entity to the database.
        get_entity: Retrieve an entity from the database by its ID.
        get_last_entity: Retrieve the last N entities of a certain type.
        get_since_entity: Retrieve entities of a certain type since a specified timestamp.
        util_create_TIC_TACs: Create TICs and TACs for a specified number of years.
    """
    # Add Methods paths
    add_paths = {
        TIC.__name__: "TICs/add",
        TAC.__name__: "TACs/add",
        SpotPublishedTIC.__name__: "SpotPublishedTICs/add",
        SpotEstimatedTIC.__name__: "SpotEstimatedTICs/add",
        ReceivedForecast.__name__: "ReceivedForecasts/add",
        SAMParameter.__name__: "SAMParameters/add",
        OptimizationParameter.__name__: "OptimizationParameters/add",
        MeasuredWeather.__name__:"MeasuredWeathers/add",
        MeasuredWeatherTIC.__name__: "MeasuredWeatherTICs/add"
    }

    add_range_paths = {
        SpotEstimatedTIC.__name__: "SpotEstimatedTICs/addRange"
    }

    # Update Method paths
    update_paths = {
        TIC.__name__: "TICs/update",
        TAC.__name__: "TACs/update",
        SpotPublishedTIC.__name__: "SpotPublishedTICs/update",
        SpotEstimatedTIC.__name__: "SpotEstimatedTICs/update",
        ReceivedForecast.__name__: "ReceivedForecasts/update",
        SAMParameter.__name__: "SAMParameters/update",
        OptimizationParameter.__name__: "OptimizationParameters/update",
        MeasuredWeather.__name__:"MeasuredWeathers/update",
        MeasuredWeatherTIC.__name__: "MeasuredWeatherTICs/update"
    }

    update_range_paths = {
        SpotEstimatedTIC.__name__: "SpotEstimatedTICs/updateRange"
    }

    # Get Methods paths
    get_paths = {
        TIC.__name__: "TICs",
        TAC.__name__: "TACs",
        SpotPublishedTIC.__name__: "SpotPublishedTICs",
        SpotEstimatedTIC.__name__: "SpotEstimatedTICs",
        ReceivedForecast.__name__ : "ReceivedForecasts",
        SAMParameter.__name__: "SAMParameters",
        OptimizationParameter.__name__: "OptimizationParameters",
        MeasuredWeather.__name__:"MeasuredWeathers",
        MeasuredWeatherTIC.__name__: "MeasuredWeatherTICs",
        WeatherEstimateTAC.__name__: "WeatherEstimateTACs",
        WeatherEstimateTIC.__name__: "WeatherEstimateTICs"
    }

    # Get last method paths
    get_last_k_paths = {
        TIC.__name__: "TICs/getLastK",
        MeasuredWeatherTIC.__name__: "MeasuredWeatherTICs/getLastK",
        SpotEstimatedTIC.__name__: "SpoteEstimatedTICs/getLastK",
    }

    get_last_kn_paths = {
        TAC.__name__: "TACs/getLastKN",
        WeatherEstimateTAC.__name__: "WeatherEstimateTACs/getLastKN",
    }

    get_last_timestamp_paths = {
        TIC.__name__: "TICs/getLastTimestamp",
        TAC.__name__: "TACs/getLastTimestamp",
    }

    get_last_estimation_TIC_timestamp_paths = {
        SpotEstimatedTIC.__name__: "SpotEstimatedTICs/getLastEstimationTICTimestamp",
    }

    get_last_measured_timestamp_paths = {
        MeasuredWeatherTIC.__name__: "MeasuredWeatherTICs/getLastMeasuredTimestamp",
    }

    get_last_store_timestamp_paths = {
        WeatherEstimateTAC.__name__: "WeatherEstimateTACs/getLastStoreTimestamp",
        WeatherEstimateTIC.__name__: "WeatherEstimateTICs/getLastStoreTimestamp",
        MeasuredWeatherTIC.__name__: "MeasuredWeatherTICs/getLastStoreTimestamp",
    }

    get_last_forecast_store_timestamp_paths = {
        WeatherEstimateTAC.__name__: "WeatherEstimateTACs/getLastForecastStoreTimestamp",
        WeatherEstimateTIC.__name__: "WeatherEstimateTICs/getLastForecastStoreTimestamp"
    }

    # Get Since method paths

    get_since_timestamp_paths = {
        TIC.__name__: "TICs/getSinceTimestamp",
        TAC.__name__: "TACs/getSinceTimestamp",
    }

    get_since_k_paths = {
        TIC.__name__: "TICs/getSinceK",
        MeasuredWeatherTIC.__name__: "MeasuredWeatherTICs/getSinceK",
        SpotEstimatedTIC.__name__: "SpotEstimatedTICs/getSinceK",
        SpotPublishedTIC.__name__: "SpotPublishedTICs/getSinceK",
    }
    
    get_since_kn_paths = {
        TAC.__name__: "TACs/getSinceKN",
        WeatherEstimateTAC.__name__: "WeatherEstimateTICs/getSinceKN"
    }

    get_since_store_timestamp_paths = {
        TIC.__name__: "TICs/getSinceStoreTimestamp",
        TAC.__name__: "TACs/getSinceStoreTimestamp",
        MeasuredWeatherTIC.__name__: "MeasuredWeatherTICs/getSinceStoreTimestamp",
    }

    get_since_measured_timestamp_paths = {
        MeasuredWeatherTIC.__name__: "MeasuredWeatherTICs/getSinceMeasuredTimestamp",
    }

    get_since_forecast_store_timestamp_paths = {
        TIC.__name__: "TICs/getSinceForecastStoreTimestamp",
        TAC.__name__: "TACs/getSinceForecastStoreTimestamp",
    }

    get_since_estimation_TIC_timestamp_paths = {
        SpotEstimatedTIC.__name__: "SpotEstimatedTICs/getSinceEstimationTICTimestamp",
    }

    get_current_paths = {
        TIC.__name__: "TICs/getCurrent",
        TAC.__name__: "TACs/getCurrent",
    }

    # Util Methods
    util_paths = {
        'CreateTICsAndTACs': "Utilities/CreateTICsAndTACs"
    }

    def __init__(self, base_url=None, debug=False, verify_ssl=True):
        """Initialize the SolORM instance.

        Args:
            base_url (str, optional): The base URL of the SOL database API. If not provided, it's fetched from the DB_API_URL environment variable.
            debug (bool, optional): Enable debugging mode for logging. Default is False.
            verify_ssl (bool, optional): Verify SSL certificates when making requests. Default is True.
        """
        if base_url is not None:
            self.base_url = base_url
        else:
            self.base_url = os.getenv("DB_API_URL")
            if self.base_url is None:
                raise ValueError("DB_API_URL environment variable not set")
            
        if debug:
            logger.remove()
            logger.add(sys.stdout, colorize=True, 
                       format="<le>[{time:DD-MM-YYYY HH:mm:ss}]</le> <lvl>[{level}]: {message}</lvl>", 
                       level="DEBUG")
            
        self.session = self._create_session(verify_ssl)
        
    def _create_session(self, verify_ssl):
        session = requests.Session()
        session.headers = {'Accept': 'text/plain', 'Content-Type': 'application/json'}
        session.verify = verify_ssl
        return session
    
    def _get_url(self, path):
        return urllib.parse.urljoin(self.base_url, path)
    
    def add_entity(self, entity):
        """Add an entity to the database.

        Args:
            entity: An instance of an entity class (e.g., TIC, TAC, etc.) to be added.

        Returns:
            entity: The entity created with the values stored in the ORM.

        Raises:
            HTTPError: If the request fails or the response status code is not 201 (Created).
            NotImplementedError: If the entity supplied does not have an associated add method
        """
        if (entity.__class__.__name__ in self.add_paths.keys()):
            endpoint = self._get_url(self.add_paths[entity.__class__.__name__])
            response = self.session.post(endpoint, json=entity.dict(exclude_none=True))

            if response.status_code == 201:
                logger.debug("Request successful")
                return type(entity).parse_obj(response.json())
            else:
                logger.debug(response.text)
                response.raise_for_status()
        else:
            raise NotImplementedError

        
    def add_range_entity(self, entity_list: list):
        """Add a range of entities of the same type to the database. This method works as a transaction, so either all the elements are added or none.

        Args:
            entity_list: A list of instances of an entity class (e.g., TIC, TAC, etc.) to be added.

        Returns:
            entity_list: The list of entities created in the ORM

        Raises:
            HTTPError: If the request fails or the response status code is not 201 (Created).
            NotImplementedError: If the entity supplied does not have an associated add range method

        """
        if entity_list.count == 0:
            raise Exception(f"This method can only be used with not empty lists")
        
        if (entity_list[0].__class__.__name__ in self.add_range_paths.keys()):
            endpoint = self._get_url(self.add_range_paths[entity_list[0].__class__.__name__])
            response = self.session.post(endpoint, json = [x.dict(exclude_none=True) for x in entity_list])
            
            if response.status_code == 201:
                logger.debug("Request successful")
                json_result = response.json()
                return [type(entity_list[0]).parse_obj(x) for x in json_result]
            else:
                logger.debug(response.text)
                response.raise_for_status()
        else:
            raise NotImplementedError

    def update_entity(self, entity):
        """Update an entity to the database.

        Args:
            entity: An instance of an entity class (e.g., TIC, TAC, etc.) to be updated.

        Returns:
            entity: The entity updated with the values stored in the ORM.

        Raises:
            HTTPError: If the request fails or the response status code is not 201 (Created).
            NotImplementedError: If the entity supplied does not have an associated update method

        """
        if (entity.__class__.__name__ in self.update_paths.keys()):
            endpoint = self._get_url(self.update_paths[entity.__class__.__name__])
            response = self.session.put(endpoint, json=entity.dict(exclude_none=True))

            if response.status_code == 202:
                logger.debug("Request successful")
                return type(entity).parse_obj(response.json())
            else:
                logger.debug(response.text)
                response.raise_for_status()
        else:
            raise NotImplementedError

    def update_range_entity(self, entity_list: list):
        """Update a range of entities of the same type to the database. This method works as a transaction, so either all the elements are updated or none.

        Args:
            entity_list: A list of instances of an entity class (e.g., TIC, TAC, etc.) to be updated.

        Returns:
            entity_list: The list of entities created in the ORM

        Raises:
            HTTPError: If the request fails or the response status code is not 201 (Created).
            NotImplementedError: If the entity supplied does not have an associated update range method
        """
        if entity_list.count == 0:
            raise Exception(f"This method can only be used with not empty lists")
        
        if (entity_list[0].__class__.__name__ in self.update_range_paths.keys()):
            
            endpoint = self._get_url(self.update_range_paths[entity_list[0].__class__.__name__])
            response = self.session.put(endpoint, json = [x.dict(exclude_none=True) for x in entity_list])
            
            if response.status_code == 202:
                logger.debug("Request successful")
                json_result = response.json()
                return [type(entity_list[0]).parse_obj(x) for x in json_result]
            else:
                logger.debug(response.text)
                response.raise_for_status()
        else:
            raise NotImplementedError
    
    def get_entity(self, entity_class, id, id2=None):
        """Returns an entity from the database.

        Args:
            entity_class: An entity class (e.g., TIC, TAC, etc.) to be retrieved.

        Returns:
            entity: The entity obtained from the ORM or None, if none exists with the provided ids

        Raises:
            HTTPError: If the request fails or the response status code is not 201 (Created).
            NotImplementedError: If the entity supplied does not have an associated get method
        """
        if (entity_class.__name__ in self.get_paths.keys()):
            endpoint = self._get_url(self.get_paths[entity_class.__name__]) + "/" + str(id) + ("/" + str(id2) if id2 is not None else "")
            response = self.session.get(endpoint)
            
            if response.status_code == 200:
                logger.debug("Request successful")
                return entity_class.parse_obj(response.json())
            elif response.status_code == 204:
                logger.debug("Request successful. No result")
                return None
            else:
                logger.debug(response.text)
                response.raise_for_status()
        else:
            raise NotImplementedError

    def get_current_entity(self, entity_class, timestamp = None):
        """Returns the entity associated with the current timestamp if no timestamp is provided. If timestamp is provided the query
         will return the same entity as if it this method was called at the moment represented by timestamp.

        Args:
            entity_class: An entity class (e.g., TIC, TAC, etc.) to be retrieved.
            timestamp: A timestamp to be used to retrieving the corresponding entity

        Returns:
            entity: The entity obtained from the ORM or None, if none exists with the provided ids

        Raises:
            HTTPError: If the request fails or the response status code is not 201 (Created).
            NotImplementedError: If the entity supplied does not have an associated get_current method
        """
        if (entity_class.__name__ in self.get_current_paths.keys()):
            endpoint = self._get_url(self.get_current_paths[entity_class.__name__]) + "/" + (str(timestamp) if timestamp is not None else "")
            response = self.session.get(endpoint)
            
            if response.status_code == 200:
                logger.debug("Request successful")
                return entity_class.parse_obj(response.json())
            elif response.status_code == 204:
                logger.debug("Request successful. No result")
                return None
            else:
                logger.debug(response.text)
                response.raise_for_status()
        else:
            raise Exception("Not Implemented")

    def get_last_k_entity(self, entity_class, number=10):
        """Retrieve the last N entities of a certain type ordered by K parameter.

        Args:
            entity_class (cls): The class of the entity to be retrieved.
            number (int, optional): The number of entities to retrieve. Default is 10.

        Returns:
            entities: A list (either filled or empty) of objects retrieved from the ORM.

        Raises:
            HTTPError: If the request fails or the response status code is not 200 (OK).
            NotImplementedError: If the entity supplied does not have an associated get_last_k_entity method
        """
        if (entity_class.__name__ in self.get_paths.keys()):
            endpoint = self._get_url(self.get_paths[entity_class.__name__]) + "/getLastK/" + str(number)
            response = self.session.get(endpoint)
            
            if response.status_code == 200:
                logger.debug("Request successful")
                json_result = response.json()
                return [entity_class.parse_obj(x) for x in json_result]
            else:
                logger.debug(response.text)
                response.raise_for_status()
        else:
            raise NotImplementedError


    def get_last_estimation_TIC_timestamp(self, entity_class, number=10):
        """Retrieve the last N entities of a certain type ordered by the related Estimation TICTimestamp parameter.

        Args:
            entity_class (cls): The class of the entity to be retrieved.
            number (int, optional): The number of entities to retrieve. Default is 10.

        Returns:
            entities: A list (either filled or empty) of objects retrieved from the ORM.

        Raises:
            HTTPError: If the request fails or the response status code is not 200 (OK).
            NotImplementedError: If the entity supplied does not have an associated get_last_estimation_TIC_timestamp method
        """
        endpoint = self._get_url(self.get_last_estimation_TIC_timestamp_paths[entity_class.__name__]) + "/" + str(number)
        response = self.session.get(endpoint)
        
        if response.status_code == 200:
            logger.debug("Request successful")
            json_result = response.json()
            return [entity_class.parse_obj(x) for x in json_result]
        else:
            logger.debug(response.text)
            response.raise_for_status()

    def get_last_timestamp_entity(self, entity_class, number=10):
        """Retrieve the last N entities of a certain type ordered by Timestamp parameter.

        Args:
            entity_class (cls): The class of the entity to be retrieved.
            number (int, optional): The number of entities to retrieve. Default is 10.

        Returns:
            entities: A list (either filled or empty) of objects retrieved from the ORM.

        Raises:
            HTTPError: If the request fails or the response status code is not 200 (OK).
            NotImplementedError: If the entity supplied does not have an associated get_last_timestamp_entity method
        """
        if (entity_class.__name__ in self.get_last_timestamp_paths.keys()):
            endpoint = self._get_url(self.get_last_timestamp_paths[entity_class.__name__]) + "/" + str(number)
            response = self.session.get(endpoint)
            
            if response.status_code == 200:
                logger.debug("Request successful")
                json_result = response.json()
                return [entity_class.parse_obj(x) for x in json_result]
            else:
                logger.debug(response.text)
                response.raise_for_status()
        else:
            raise NotImplementedError    

    def get_last_store_timestamp_entity(self, entity_class, number=10):
        """Retrieve the last N entities of a certain type ordered by StoreTimestamp parameter.

        Args:
            entity_class (cls): The class of the entity to be retrieved.
            number (int, optional): The number of entities to retrieve. Default is 10.

        Returns:
            entities: A list (either filled or empty) of objects retrieved from the ORM.

        Raises:
            HTTPError: If the request fails or the response status code is not 200 (OK).
            NotImplementedError: If the entity supplied does not have an associated get_last_store_timestamp method
        """
        if (entity_class.__name__ in self.get_last_store_timestamp_paths.keys()):
            endpoint = self._get_url(self.get_last_store_timestamp_paths[entity_class.__name__]) + "/" + str(number)
            response = self.session.get(endpoint)
            
            if response.status_code == 200:
                logger.debug("Request successful")
                json_result = response.json()
                return [entity_class.parse_obj(x) for x in json_result]
            else:
                logger.debug(response.text)
                response.raise_for_status()
        else:
            raise NotImplementedError

    def get_last_measured_timestamp_entity(self, entity_class, number=10):
        """Retrieve the last N entities of a certain type ordered by MeasuredTimestamp parameter.

        Args:
            entity_class (cls): The class of the entity to be retrieved.
            number (int, optional): The number of entities to retrieve. Default is 10.

        Returns:
            entities: A list (either filled or empty) of objects retrieved from the ORM.

        Raises:
            HTTPError: If the request fails or the response status code is not 200 (OK).
            NotImplementedError: If the entity supplied does not have an associated get_last_measured_timestamp method
        """
        if (entity_class.__name__ in self.get_last_measured_timestamp_paths.keys()):
            endpoint = self._get_url(self.get_last_measured_timestamp_paths[entity_class.__name__]) + "/" + str(number)
            response = self.session.get(endpoint)
            
            if response.status_code == 200:
                logger.debug("Request successful")
                json_result = response.json()
                return [entity_class.parse_obj(x) for x in json_result]
            else:
                logger.debug(response.text)
                response.raise_for_status()
        else:
            raise NotImplementedError

    def get_last_forecast_store_timestamp_entity(self, entity_class, number=10):
        """Retrieve the last N entities of a certain type ordered by ForecastStoreTimestamp parameter.

        Args:
            entity_class (cls): The class of the entity to be retrieved.
            number (int, optional): The number of entities to retrieve. Default is 10.

        Returns:
            entities: A list (either filled or empty) of objects retrieved from the ORM.

        Raises:
            HTTPError: If the request fails or the response status code is not 200 (OK).
            NotImplementedError: If the entity supplied does not have an associated get_last_forecast_store_timestamp method
        """
        if (entity_class.__name__ in self.get_last_forecast_store_timestamp_paths.keys()):
            endpoint = self._get_url(self.get_last_forecast_store_timestamp_paths[entity_class.__name__]) + "/" + str(number)
            response = self.session.get(endpoint)
            
            if response.status_code == 200:
                logger.debug("Request successful")
                json_result = response.json()
                return [entity_class.parse_obj(x) for x in json_result]
            else:
                logger.debug(response.text)
                response.raise_for_status()
        else:
            raise NotImplementedError

    def get_since_k_entity(self, entity_class, since, number=10):
        """Retrieve entities of a certain type since a specified K.

        Args:
            entity_class (cls): The class of the entity to be retrieved.
            since (int): The K since which to retrieve entities.
            number (int, optional): The number of entities to retrieve. Default is 10. The Max is 200.

        Returns:
            entities: A list (either filled or empty) of objects retrieved from the ORM.

        Raises:
            HTTPError: If the request fails or the response status code is not 200 (OK).
            NotImplementedError: If the entity supplied does not have an associated get_since_k_entity method
        """
        if (entity_class.__name__ in self.get_since_k_paths.keys()):
            endpoint = self._get_url(self.get_since_k_paths[entity_class.__name__]) + "/" + str(since) + "/" + str(number) 
            response = self.session.get(endpoint)
            
            if response.status_code == 200:
                logger.debug("Request successful")
                json_result = response.json()
                return [entity_class.parse_obj(x) for x in json_result]
            else:
                logger.debug(response.text)
                response.raise_for_status()
        else:
            raise NotImplementedError

    def get_since_kn_entity(self, entity_class, since_k, since_n, number=10):
        """Retrieve entities of a certain type since a specified K,N.

        Args:
            entity_class (cls): The class of the entity to be retrieved.
            since_k (int): The K since which to retrieve entities.
            since_n (int): The N since which to retrieve entities.
            number (int, optional): The number of entities to retrieve. Default is 10. The Max is 200.

        Returns:
            entities: A list (either filled or empty) of objects retrieved from the ORM.

        Raises:
            HTTPError: If the request fails or the response status code is not 200 (OK).
            NotImplementedError: If the entity supplied does not have an associated get_since_kn_entity method
        """
        if (entity_class.__name__ in self.get_since_kn_paths.keys()):
            endpoint = self._get_url(self.get_since_kn_paths[entity_class.__name__]) + "/" + str(since_k) + "/" + str(since_n) + "/" + str(number) 
            response = self.session.get(endpoint)
            
            if response.status_code == 200:
                logger.debug("Request successful")
                json_result = response.json()
                return [entity_class.parse_obj(x) for x in json_result]
            else:
                logger.debug(response.text)
                response.raise_for_status()
        else:
            raise NotImplementedError

    def get_since_timestamp_entity(self, entity_class, timestamp: int, count: int = 10):
        """Retrieve entities of a certain type since a specified Timestamp.

        Args:
            entity_class (cls): The class of the entity to be retrieved.
            since (int): The Timestamp since which to retrieve entities.
            number (int, optional): The number of entities to retrieve. Default is 10. The Max is 200.

        Returns:
            entities: A list (either filled or empty) of objects retrieved from the ORM.

        Raises:
            HTTPError: If the request fails or the response status code is not 200 (OK).
            NotImplementedError: If the entity supplied does not have an associated get_since_timestamp_entity method
        """
        if (entity_class.__name__ in self.get_since_timestamp_paths.keys()):
            endpoint = self._get_url(self.get_since_timestamp_paths[entity_class.__name__]) + "/" + str(timestamp) + "/" + str(count) 
            response = self.session.get(endpoint)
            
            if response.status_code == 200 :
                logger.debug("Request successful")
                json_result = response.json()
                return [entity_class.parse_obj(x) for x in json_result]
            elif response.status_code == 204:
                return []
            else:
                logger.debug(response.text)
                response.raise_for_status()
        else:
            raise NotImplementedError

    def get_since_estimation_TIC_timestamp(self, entity_class, timestamp: int, count: int = 10):
        """Retrieve entities of a certain type since a specified Estimation TIC  Timestamp.

        Args:
            entity_class (cls): The class of the entity to be retrieved.
            since (int): The Timestamp since which to retrieve entities.
            number (int, optional): The number of entities to retrieve. Default is 10. The Max is 200.

        Returns:
            entities: A list (either filled or empty) of objects retrieved from the ORM.

        Raises:
            HTTPError: If the request fails or the response status code is not 200 (OK).
            NotImplementedError: If the entity supplied does not have an associated get_since_estimation_TIC_timestamp method
        """
        if (entity_class.__name__ in self.get_since_estimation_TIC_timestamp_paths.keys()):
            endpoint = self._get_url(self.get_since_estimation_TIC_timestamp_paths[entity_class.__name__]) + "/" + str(timestamp) + "/" + str(count) 
            response = self.session.get(endpoint)
            
            if response.status_code == 200 :
                logger.debug("Request successful")
                json_result = response.json()
                return [entity_class.parse_obj(x) for x in json_result]
            elif response.status_code == 204:
                return []
            else:
                logger.debug(response.text)
                response.raise_for_status()
        else:
            raise NotImplementedError

    def get_since_measured_timestamp_entity(self, entity_class, timestamp: int, count: int = 10):
        """Retrieve entities of a certain type since a specified Measured Timestamp.

        Args:
            entity_class (cls): The class of the entity to be retrieved.
            since (int): The Timestamp since which to retrieve entities.
            number (int, optional): The number of entities to retrieve. Default is 10. The Max is 200.

        Returns:
            entities: A list (either filled or empty) of objects retrieved from the ORM.

        Raises:
            HTTPError: If the request fails or the response status code is not 200 (OK).
            NotImplementedError: If the entity supplied does not have an associated get_since_measured_timestamp method
        """
        if (entity_class.__name__ in self.get_since_measured_timestamp_paths.keys()):
            endpoint = self._get_url(self.get_since_measured_timestamp_paths[entity_class.__name__]) + "/" + str(timestamp) + "/" + str(count) 
            response = self.session.get(endpoint)
            
            if response.status_code == 200 :
                logger.debug("Request successful")
                json_result = response.json()
                return [entity_class.parse_obj(x) for x in json_result]
            elif response.status_code == 204:
                return []
            else:
                logger.debug(response.text)
                response.raise_for_status()
        else:
            raise NotImplementedError
    
    def get_since_forecast_store_timestamp_entity(self, entity_class, timestamp: int, count: int = 10):
        """Retrieve entities of a certain type since a specified forecast store Timestamp.

        Args:
            entity_class (cls): The class of the entity to be retrieved.
            since (int): The Timestamp since which to retrieve entities.
            number (int, optional): The number of entities to retrieve. Default is 10. The Max is 200.

        Returns:
            entities: A list (either filled or empty) of objects retrieved from the ORM.

        Raises:
            HTTPError: If the request fails or the response status code is not 200 (OK).
            NotImplementedError: If the entity supplied does not have an associated get_since_forecast_store_timestamp method
        """
        if (entity_class.__name__ in self.get_since_forecast_store_timestamp_paths.keys()):
            endpoint = self._get_url(self.get_since_forecast_store_timestamp_paths[entity_class.__name__]) + "/" + str(timestamp) + "/" + str(count) 
            response = self.session.get(endpoint)
            
            if response.status_code == 200 :
                logger.debug("Request successful")
                json_result = response.json()
                return [entity_class.parse_obj(x) for x in json_result]
            elif response.status_code == 204:
                return []
            else:
                logger.debug(response.text)
                response.raise_for_status()
        else:
            raise NotImplementedError

    def get_since_store_timestamp_entity(self, entity_class, timestamp: int, count: int = 10):
        """Retrieve entities of a certain type since a specified store Timestamp.

        Args:
            entity_class (cls): The class of the entity to be retrieved.
            since (int): The Timestamp since which to retrieve entities.
            number (int, optional): The number of entities to retrieve. Default is 10. The Max is 200.

        Returns:
            entities: A list (either filled or empty) of objects retrieved from the ORM.

        Raises:
            HTTPError: If the request fails or the response status code is not 200 (OK).
            NotImplementedError: If the entity supplied does not have an associated get_since_store_timestamp range method
        """
        if (entity_class.__name__ in self.get_since_store_timestamp_paths.keys()):
            endpoint = self._get_url(self.get_since_store_timestamp_paths[entity_class.__name__]) + "/" + str(timestamp) + "/" + str(count) 
            response = self.session.get(endpoint)
            
            if response.status_code == 200 :
                logger.debug("Request successful")
                json_result = response.json()
                return [entity_class.parse_obj(x) for x in json_result]
            elif response.status_code == 204:
                return []
            else:
                logger.debug(response.text)
                response.raise_for_status()
        else:
            raise NotImplementedError
    
    
        
    def util_create_TIC_TACs(self, years=1):
        """
        Create TICs and TACs for a specified number of years.

        Args:
            years (int, optional): The number of years for which to create TICs and TACs. Default is 1.

        Returns:
            dict: The JSON response from the API.

        Raises:
            HTTPError: If the request fails or the response status code is not 201 (Created).
        """
        endpoint = self._get_url(self.util_paths["CreateTICsAndTACs"])
        response = self.session.post(endpoint, json={"years": years})
        
        if response.status_code == 201:
            logger.debug("Request successful")
            return response.json()
        else:
            logger.debug(response.text)
            response.raise_for_status()
        