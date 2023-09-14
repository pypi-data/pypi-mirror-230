from dataclasses import dataclass
import json
import logging
import pathlib
import requests
import sys
import tempfile

INFO_URL = "https://www.signupgenius.com/SUGboxAPI.cfm?go=s.getSignupInfo"
PARTICIPANT_URL = (
    "https://www.signupgenius.com/SUGboxAPI.cfm?go=s.getSignUpParticipantsBySlotItem"
)

logger = logging.getLogger(__name__)


class SignupApiError(Exception):
    pass


class CachingSignupApiWrapper:
    def __init__(self, cache_dir=None, refresh=False, never_refresh=False):
        self.cache_dir = pathlib.Path(cache_dir or tempfile.gettempdir())
        self.refresh = refresh
        self.never_refresh = never_refresh
        self.api = SignupApiWrapper()
        self.indent = 2

    @property
    def request_count(self):
        return self.api.request_count

    def get_info(self, url_id):
        path = self.cache_dir / f"{url_id}.json"
        if path.exists() and self.refresh is False:
            with open(path) as f:
                data = json.load(f)
        elif self.never_refresh is False:
            data = self.api.get_info(url_id)
            with open(path, "w") as f:
                json.dump(data, f, indent=self.indent)
        else:
            raise SignupApiError(
                f"Local cache file for {url_id} does not exist but never_refresh is set"
            )
        return data

    def get_participants(self, list_id, slot_item_id, offset=1, limit_to=100):
        file_name = f"{list_id}-{slot_item_id}.json"
        path = self.cache_dir / file_name
        if path.exists() and self.refresh is False:
            with open(path) as f:
                data = json.load(f)
        elif self.never_refresh is False:
            data = self.api.get_participants(list_id, slot_item_id)
            with open(path, "w") as f:
                json.dump(data, f, indent=self.indent)
        else:
            raise SignupApiError(
                f"Local cache file for {file_name} does not exist but never_refresh is set"
            )

        return data


class SignupApiWrapper:
    def __init__(self):
        self.request_count = 0

    def get_info(self, url_id):
        payload = {"forSignUpView": True, "urlid": url_id, "portalid": 0}
        resp = requests.post(INFO_URL, json=payload)
        self.request_count += 1
        if resp.status_code != 200:
            raise SignupApiError(
                f"Info API call, Status Code: {resp.status_code}\n{resp.text}"
            )
        data = resp.json()
        if data["SUCCESS"] is False:
            message = ", ".join(data["MESSAGE"])
            raise SignupApiError(f"Info API call failed with message {message}")
        return data

    def get_participants(self, list_id, slot_item_id, offset=1, limit_to=100):
        payload = {
            "listid": list_id,
            "slotitemid": slot_item_id,
            "offset": offset,
            "limitTo": limit_to,
        }
        resp = requests.post(PARTICIPANT_URL, json=payload)
        self.request_count += 1
        if resp.status_code != 200:
            raise SignupApiError(
                f"Participants API call, Status Code: {resp.status_code}\n{resp.text}"
            )
        data = resp.json()
        if data["SUCCESS"] is False:
            message = ", ".join(data["MESSAGE"])
            raise SignupApiError(f"Participants API call failed with message {message}")
        return data


def get_signups_from_api(url_id, api_wrapper=None):
    api_wrapper = api_wrapper or SignupApiWrapper()
    info = api_wrapper.get_info(url_id)
    slots = {}
    list_id = info["DATA"]["id"]
    for slot_outer_id, slot_dict in info["DATA"]["slots"].items():
        if "dates" in slot_dict:
            capacity = slot_dict["QTY"]
            for dated_slot_dict in slot_dict["dates"]:
                slot_inner_id = str(dated_slot_dict["slotitemid"])
                filled = dated_slot_dict.get("qtyTaken", 0)

                slots[slot_inner_id] = Slot(
                    id=slot_inner_id,
                    name=slot_dict["ITEM"].strip(),
                    date=dated_slot_dict.get("lastSlotDate", ""),
                    comments=slot_dict.get("ITEMCOMMENT", ""),
                    capacity=capacity,
                    filled=filled,
                )
        elif "items" in slot_dict:
            for item_slot_dict in slot_dict["items"]:
                slot_inner_id = str(item_slot_dict["slotitemid"])
                capacity = item_slot_dict.get("qty", 0)
                filled = item_slot_dict.get("qtyTaken", 0)

                slots[slot_inner_id] = Slot(
                    id=slot_inner_id,
                    name=item_slot_dict["item"].strip(),
                    date=slot_dict.get("LASTSLOTDATE", ""),
                    comments=item_slot_dict.get("itemcomment", ""),
                    capacity=capacity,
                    filled=filled,
                )
    signups = []
    for slot_item_id, participants_list in info["DATA"].get("participants", {}).items():
        slot_signups = []
        slot = slots[slot_item_id]
        total_count = 0
        for participant in participants_list:
            name = " ".join(
                [participant.get("firstname", ""), participant.get("lastname", "")]
            ).strip()
            count = participant.get("myqty", 0)
            comments = participant.get("mycomment", "")
            slot_signups.append(Signup(name, count, comments, slot))
            total_count += count
        if total_count < slot.filled:
            logger.info(
                f"{total_count} / {slot.filled} from inline participants for {slot.name}, retrieving instead via API"
            )
            slot_signups = signups_from_participant_api(
                api_wrapper, list_id, slot_item_id, slot
            )
        signups.extend(slot_signups)
    return signups


def signups_from_participant_api(api_wrapper, list_id, slot_item_id, slot):
    # todo - paging
    data = api_wrapper.get_participants(list_id, slot_item_id)

    signups = []
    total_count = 0
    for participant in data["DATA"]["participants"]:
        name = " ".join(
            [participant.get("firstname", ""), participant.get("lastname", "")]
        ).strip()
        count = participant.get("myqty", 0)
        comments = participant.get("mycomment", "")
        signups.append(Signup(name, count, comments, slot))
        total_count += count
    if total_count < slot.filled:
        raise ValueError(
            f"{slot.name}: Got {total_count} from participants api but slot has {slot.filled} filled"
        )
    return signups


@dataclass
class Slot:
    id: str
    name: str
    date: str
    comments: str = ""
    capacity: int = 1
    filled: int = 0

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


@dataclass
class Signup:
    name: str
    count: int
    comments: str
    slot: Slot


def url_id_from_url(url):
    url = url.rstrip("/")
    url = url.rstrip("#")
    return url.split("/")[-1]


def get_sug_info(url_id):
    payload = {"forSignUpView": True, "urlid": url_id, "portalid": 0}
    resp = requests.post(INFO_URL, json=payload)
    if resp.status_code != 200:
        raise ValueError(f"Info API call, Status Code: {resp.status_code}\n{resp.text}")
    return resp.json()


def get_sug_participants(list_id, slot_item_id, offset=1, limit_to=100):
    payload = {
        "listid": list_id,
        "slotitemid": slot_item_id,
        "offset": offset,
        "limitTo": limit_to,
    }
    resp = requests.post(PARTICIPANT_URL, json=payload)
    if resp.status_code != 200:
        raise ValueError(
            f"Participants API call, Status Code: {resp.status_code}\n{resp.text}"
        )
    return resp.json()


if __name__ == "__main__":
    # url = sys.argv[1]
    # url_id = url_id_from_url(url)
    # resp = get_sug_info(url_id)

    list_id = int(sys.argv[1])
    slot_item_id = int(sys.argv[2])
    resp = get_sug_participants(list_id, slot_item_id)

    print(json.dumps(resp, indent=2))
