from concurrent.futures import Future
from typing import Iterable, Optional, Callable
from anki import (
    Controller as AController, 
    Vehicle as AVehicle, 
    TrackPiece, 
    TrackPieceType
)

from .._worker import get_single_worker
from .vehicle import Vehicle

async def _wrap_vehicle(v: AVehicle):
        # Wraps py-drivesdk's Vehicle object into ours. This is done in an async function to make sure the event listener register there
        return Vehicle(v)
        pass

class Controller:
    """
    This object controls all vehicle connections. With it you can connect to any number of vehicles and disconnect cleanly.

    :param timeout: :class:`float` The time until the controller gives up searching for a vehicle.
    """
    def __init__(self,*, timeout: float=10):
        self._internal= AController(timeout=timeout)
        pass

    def connect_one(self, vehicle_id: Optional[int]=None) -> Vehicle:
        """Connect to one non-charging Supercar and return the Vehicle instance
        
        :param vehicle_id: :class:`Optional[int]` 
            The id given to the :class:`Vehicle` instance on connection

        Returns
        -------
        :class:`Vehicle`
            The connected supercar
        
        Raises
        ------
        :class:`VehicleNotFound` 
            No supercar was found in the set timeout
        
        :class:`ConnectionTimedoutException` 
            The connection attempt to the supercar did not succeed within the set timeout
        
        :class:`ConnectionDatabusException` 
            A databus error occured whilst connecting to the supercar
        
        :class:`ConnectionFailedException` 
            A generic error occured whilst connection to the supercar
        """
        worker = get_single_worker()
        return worker.run_future(_wrap_vehicle(worker.\
            run_future(self._internal.connect_one(vehicle_id))))
        pass

    def connect_specific(
            self, 
            address: str, 
            vehicle_id: Optional[int]=None
        ) -> Vehicle:
        """Connect to a supercar with a specified MAC address
        
        :param address: :class:`str`
            The MAC-address of the vehicle to connect to. Needs to be uppercase seperated by colons
        :param vehicle_id: :class:`Optional[int]`
            The id passed to the :class:`Vehicle` object on its creation

        Returns
        -------
        :class:`Vehicle`
            The connected supercar
        
        Raises
        ------
        :class:`VehicleNotFound`
            No supercar was found in the set timeout
        
        :class:`ConnectionTimedoutException`
            The connection attempt to the supercar did not succeed within the set timeout
        
        :class:`ConnectionDatabusException`
            A databus error occured whilst connecting to the supercar
        
        :class:`ConnectionFailedException`
            A generic error occured whilst connection to the supercar
        """
        worker = get_single_worker()
        return worker.run_future(_wrap_vehicle(worker.\
            run_future(self._internal.connect_specific(
                address,
                vehicle_id
            ))))
        pass

    def connect_many(
            self, 
            amount: int, 
            vehicle_ids: Iterable[int]|None=None
        ) -> tuple[Vehicle]:
        """Connect to <amount> non-charging Supercars
        
        :param amount: :class:`int`
            The amount of vehicles to connect to
        :param vehicle_ids: :class:`Optional[Iterable[int]]` 
            The vehicle ids passed to the :class:`Vehicle` instances

        Returns
        -------
        :class:`tuple[Vehicle]`
            The connected supercars

        Raises
        ------
        :class:`ValueError`
            The amount of requested supercars does not match the length of :param vehicle_ids:

        :class:`VehicleNotFound`
            No supercar was found in the set timeout

        :class:`ConnectionTimedoutException`
            A connection attempt to one of the supercars timed out

        :class:`ConnectionDatabusException`
            A databus error occured whilst connecting to a supercar

        :class:`ConnectionFailedException`
            A generic error occured whilst connecting to a supercar

        """
        worker = get_single_worker()
        return tuple(worker.run_future(_wrap_vehicle(v))
            for v in worker.\
                run_future(
                    self._internal.connect_many(amount,vehicle_ids)
                )
            )
        pass

    def scan(self, 
        scan_vehicle: Vehicle|None=None, 
        align_pre_scan: bool=True, 
        blocking: bool=True, 
        completion_callback: Callable[
            [list[TrackPiece]],
            None
        ]|None=None
        ) -> list[TrackPiece]:
        """Assembles a digital copy of the map and adds it to every connected vehicle.
        
        :param scan_vehicle: :class:`Optional[Vehicle]`
            When passed a Vehicle object, this Vehicle will be used as a scanner. Otherwise one will be selected automatically.
        :param align_pre_scan: 
            When set to True, the supercars can start from any position on the map and align automatically before scanning. Disabling this means your supercars need to start between START and FINISH
        :param blocking: :class:`bool`
            If set to :const:`True`, this function will wait until the scan is complete
        :param completion_callback: :class:`Optional[Callable[[list[TrackPiece]],None]]`
            A function or similar receiving one argument (a :class:`list[TrackPiece]`) that gets executed when the scan is completed.
            This argument is optional.

        Returns
        -------
        :class:`list[TrackPiece]`
            The resulting map

        Raises
        ------
        :class:`DuplicateScanWarning`
            The map was already scanned in. This scan will be skipped.
        """
        def callback(future: Future):
            completion_callback(future.result())

        return get_single_worker().run_future(
            self._internal.scan(
                scan_vehicle._internal if 
                    scan_vehicle is not None 
                    else None,
                align_pre_scan
            ),
            blocking,
            callback if completion_callback is not None else None
            )
        pass

    def disconnect_all(self, 
        blocking: bool=True, 
        completion_callback: Callable[[],None]|None=None):
        """Disconnects from all the connected supercars
        
        :param blocking: :class:`bool`
            If set to :const:`True`, this method will wait for all disconnects to finish before it completes.
        :param completion_callback: :class:`Optional[Callable[[],None]]`
            A function or similar to be called when the disconnects are complete.
            This function cannot require any argument.

        Raises
        ------
        :class:`DisconnectTimedoutException`
            A disconnection attempt timed out
        :class:`DisconnectFailedException`
            A disconnection attempt failed for unspecific reasons
        """
        get_single_worker().run_future(
            self._internal.disconnect_all(),
            blocking,
            (lambda _: completion_callback()) 
            if completion_callback is not None 
            else None
        )
        pass

    @property
    def map_types(self) -> tuple[TrackPieceType]|None:
        """A list of :attr:`TrackPiece.type` of the map, in-order"""
        return self._internal.map_types
        pass


    def __enter__(self):
        return self
        pass

    def __exit__(self,*args):
        self.disconnect_all()
        pass
    pass