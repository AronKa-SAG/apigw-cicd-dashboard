from abc import ABC, abstractmethod
import logging


class Asset(ABC):
    """Abstract base class for all API Gateway assets.
    
    :param payload: payload dict of the asset
    """
    
    name:str = ""
    id:str = ""
    asset_type: str = ""
    
    def __init__(self, payload: dict) -> None:
        self._payload = payload
        self.logger = logging.getLogger('azure')
        self.logger.setLevel(logging.DEBUG)  
        logging.basicConfig(format='[%(levelname)7s - %(asctime)s - %(funcName)25s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    def get_payload(self) -> dict:
        """Returns asset payload as dictionary."""
        self._update_payload()
        return self._payload
    
    @abstractmethod
    def _update_payload(self) -> None:
        """Updates objects payload"""
        pass

    def __repr__(self):
        return(f"{self.asset_type}[ name: {self.name} --- id: {self.id} ]")