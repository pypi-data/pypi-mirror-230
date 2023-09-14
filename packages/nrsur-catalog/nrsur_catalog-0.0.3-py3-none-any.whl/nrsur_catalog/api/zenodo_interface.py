"""Module to get zenodo URLs from NRSur Catlog zenodo page"""
import functools
import re
from typing import List, Tuple

from .urls import LVK_URLS, NR_URLS


def get_zenodo_urls(lvk_posteriors=False) -> dict:
    """Returns a dictionary of the analysed events and their urls"""
    if lvk_posteriors:
        return LVK_URLS
    else:
        return NR_URLS


def check_if_event_in_zenodo(event_name: str, lvk_posteriors=False) -> Tuple[bool, str]:
    """Check if the event is in Zenodo

    Returns
    -------
        present: bool
            True if the event is in Zenodo
        event_name: str
            The name of the event in Zenodo
    """

    present = False
    urls_dict = get_zenodo_urls(lvk_posteriors)

    shortname = event_name.split("_")[0]
    fullname = shortname + r"\_\d{6}"

    if event_name in urls_dict:
        present = True
    elif shortname in urls_dict:
        present = True
        event_name = shortname
    else:
        for name in urls_dict.keys():
            if re.match(fullname, name):
                present = True
                event_name = name
                break

    return present, event_name


@functools.lru_cache
def get_analysed_event_names(lvk_posteriors=False) -> List[str]:
    """Return a list of analysed events.

    Parameters
    ----------
        lvk_posteriors: Optional[bool]
            True if you want to return the names of the analysed LVK events.
            False if you want to return the names of the analysed NRSur cat events.
    """
    events = list(set(get_zenodo_urls(lvk_posteriors).keys()))
    # remove None from the list
    events = [event for event in events if event is not None]
    return sorted(events)
