from typing import Callable, Optional
from .._worker import get_single_worker
from anki import Vehicle as AVehicle, TrackPiece, errors
from anki.misc.lanes import BaseLane, Lane3, Lane4, _LaneType

class Vehicle:
    """This class represents a supercar. With it you can control all functions of said supercar.

    :param vehicle: :class:`anki.Vehicle`
    
    .. note::
        You should not create this class manually, use one of the connect methods in the :class:`Controller`.
    """

    def __init__(self, vehicle: AVehicle):
        self._internal = vehicle
        pass

    def wait_for_track_change(self, timeout: Optional[float]=None) -> Optional[TrackPiece]:
        """Waits until the current track piece changes.

        :param timeout: :class:`Optional[float]`
            The time (in seconds) to wait for a track piece. 
            If set to :class:`None` (the default) will wait indefinitely for a new track piece
        
        Returns
        -------
        :class:`Optional[TrackPiece]`
            The new track piece. `None` if :func:`Vehicle.map` is None
            (for example if the map has not been scanned yet)
        
        Raises
        ------
        :class:`TimeoutError`
            No new track piece was found before the given timeout
        """
        return get_single_worker().run_future(
            self._internal.wait_for_track_change(),
            timeout=timeout
        )
        pass

    def disconnect(self, 
        blocking: bool=True,
        timeout: Optional[float]=None,
        completion_callback: Callable[[],None]|None=None
        ) -> bool|None:
        """Disconnect from the Supercar

        .. note::
            Remember to execute this for every connected :class:`Vehicle` once the program exits.
            Not doing so will result in your supercars not connecting sometimes as they still think they are connected.

        :param blocking: :class:`bool`
            If set to :const:`True`, the function will wait until the Vehicle has finished disconnecting or until the given timeout.
        :param timeout: :class:`Optional[float]`
            The time to wait for a successful disconnect. If the timeout expires before the vehicle has disconnected, :class:`TimeoutError` is raised
            If set to :const:`None` (the default) the function will wait indefinitely.
        :param completion_callback: :class:`Optional[Callable[[],None]]`
            A function or similar to be called after the disconnect attempt has finished.
            This function must not require any positional or keyword arguments. This argument is optional.

        Returns
        -------
        :class:`bool`
        The connection state of the :class:`Vehicle` instance. This should always be :const:`False`

        Raises
        ------
        :class:`DisconnectFailedException`
            The attempt to disconnect from the supercar failed for an unspecified reason
        
        :class:`TimeoutError`
            The attempt to disconnect from the supercar did not succeed within the given timeout
        """
        try:
            result = get_single_worker().run_future(
                self._internal.disconnect(),
                blocking=blocking,
                completion_callback=completion_callback,
                timeout=timeout
            )
        except errors.DisconnectTimedoutException as e:
            raise TimeoutError("The disconnect attempt did not finish within the specified timeout") from e
            pass

        if blocking:
            return result
        pass

    def set_speed(self, 
        speed: int, 
        acceleration: int=500
        ):
        """Set the speed of the Supercar in mm/s

        :param speed: :class:`int`
            The speed in mm/s.
        :param acceleration: :class:`int`
            The acceleration in mm/s².
            The default for this is 500.
        """
        get_single_worker().run_future(
            self._internal.set_speed(speed,acceleration),
            False
        )
        pass

    def stop(self):
        """Stops the Supercar"""
        get_single_worker().run_future(
            self._internal.stop(),
            False
        )
        pass

    def change_lane(self, 
        lane: _LaneType, 
        horizontal_speed: int=300, 
        horizontal_acceleration: int=300
        ):
        """
        Change to a desired lane

        :param lane: :class:`BaseLane` 
            The lane to move into. These may be :class:`Lane3` or :class:`Lane4`.
        :param horizontal_speed: :class:`int`
            The speed the vehicle will move along the track at in mm/s.
            The default for this is 300.
        :param horizontal_acceleration: :class:`int`
            The acceleration in mm/s² the vehicle will move horizontally with.
            The default for this is 300.
        
        """
        get_single_worker().run_future(
            self._internal.change_lane(lane,horizontal_speed,horizontal_acceleration)
        )
        pass

    def change_position(self,
        road_center_offset: float,
        horizontal_speed: int=300,
        horizontal_acceleration: int=300
        ):
        """
        Change to a position offset from the track centre
        
        :param road_center_offset: :class:`float`
            The target offset from the centre of the track piece in mm.
        :param horizontal_speed: :class:`int`
            The speed the vehicle will move along the track at in mm/s.
            The default for this is 300.
        :param horizontal_acceleration: :class:`int`
            The acceleration in mm/s² the vehicle will move horizontally with .
            The default for this is 300.
        """
        get_single_worker().run_future(
            self._internal.change_position(road_center_offset,horizontal_speed,horizontal_acceleration)
        )
        pass

    def turn(self):
        """
        .. warning::
            This does not yet function properly. It is advised not to use this method
        """
        get_single_worker().run_future(
            self._internal.turn()
        )
        pass

    def get_lane(self, mode: _LaneType):
        """
        Get the current lane given a specific lane type

        :param mode: :class:`BaseLane` 
            A class such as :class:`Lane3` or :class:`Lane4` inheriting from :class:`BaseLane`. This is the lane system being used.
        
        Returns
        -------
        :class:`Optional[BaseLane]`
            The lane the vehicle is on. This may be none if no lane information is available.
            (such as at the start of the program, when the vehicles haven't moved much)
        """
        return self._internal.get_lane(mode)
        pass

    def align_to_start(self, 
        speed: int=300,
        blocking: bool=True,
        completion_callback: Callable[[],None]=None,
        ):
        """
        Align to the start piece. This only works if the map is already scanned in

        :param speed: :class:`int`
            The speed the vehicle should travel at during alignment
        :param blocking: :class:`bool`
            If set to :const:`True`, this method will wait for the Vehicle to be aligned to the start
        :param completion_callback: :class:`Optional[Callable[[],None]]`

        """
        get_single_worker().run_future(
            self._internal.align(speed),
            blocking,
            (lambda _: completion_callback()) 
            if completion_callback is not None 
            else None
        )
        pass

    
    def track_piece_change(self, func):
        """
        A decorator marking a function to be executed when the supercar drives onto a new track piece

        :param func: :class:`function`
            The listening function
        
        Returns
        -------
        :class:`function`
            The function that was passed in
        """
        self._internal.track_piece_change(func)
        pass

    def remove_track_piece_watcher(self, func):
        """
        Remove a track piece event handler added by :func:`Vehicle.trackPieceChange`

        :param func: :class:`function`
            The function to remove as an event handler
        
        Raises
        ------
        :class:`ValueError`
            The function passed is not an event handler
        """
        self._internal.remove_track_piece_watcher(func)
        pass

    
    # These properties just translate from the py-drivesdk.
    # Sadly, there is no easy way to automate this
    @property
    def is_connected(self) -> bool:
        """
        `True` if the vehicle is currently connected
        """
        return self._internal.is_connected
    
    @property
    def current_track_piece(self) -> TrackPiece|None:
        """
        The :class:`TrackPiece` the vehicle is currently located at

        .. note::
            This will return :class:`None` if either scan or align is not completed
        """
        return self._internal.current_track_piece
    
    @property
    def map(self) -> tuple[TrackPiece]|None:
        """
        The map the :class:`Vehicle` instance is using. 
        This is :class:`None` if the :class:`Vehicle` does not have a map supplied.
        """
        return self._internal.map
    
    @property
    def map_position(self) -> int|None:
        """
        The position of the :class:`Vehicle` instance on the map.
        This is :class:`None` if :func:`Vehicle.align` has not yet been called.
        """
        return self._internal.map_position
    
    @property
    def road_offset(self) -> float|None:
        """
        The offset from the road centre.
        This is :class:`None` if the supercar did not send any information yet. (Such as when it hasn't moved much)
        """
        return self._internal.road_offset
    
    @property
    def speed(self) -> int:
        """
        The speed of the supercar in mm/s.
        This is :class:`None` if the supercar has not moved or :func:`Vehicle.setSpeed` hasn't been called yet.
        """
        return self._internal.speed
    
    @property
    def current_lane3(self) -> Optional[Lane3]:
        """
        Short-hand for 
        
        .. code-block:: python
            
            Vehicle.getLane(Lane3)
        """
        return self._internal.current_lane3
    
    @property
    def current_lane4(self) -> Optional[Lane4]:
        """
        Short-hand for 
        
        .. code-block:: python
            
            Vehicle.getLane(Lane4)
        """
        return self._internal.current_lane4
    
    @property
    def id(self) -> int:
        """
        The id of the :class:`Vehicle` instance. This is set during initialisation of the object.
        """
        return self._internal.id
    pass

