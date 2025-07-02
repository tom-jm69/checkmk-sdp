#!/usr/bin/env python3

# -----------------------------------------------------------------------------#
# Requirements
# -----------------------------------------------------------------------------#
# python3-requests
#
# -----------------------------------------------------------------------------#

import json
import os
import traceback as tb

try:
    import requests
except ImportError:
    print("Please install `python3-requests`")
    exit(1)


API_URL = "http://172.18.0.3:8083"
NOTIFICATION_TYPE = os.environ.get("NOTIFY_WHAT", "")  # HOST / SERVICE
session = requests.Session()
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer hi",
}

session.headers.update(headers)
max_retry = 5
timeout = 10


# "Content-Type: application/json" -H "Authorization: Bearer hi"
if not NOTIFICATION_TYPE:
    print("No notification type... Exiting")
    exit(1)

SERVICE_ENVS = [
    "OMD_SITE",
    "USER",
    "NOTIFY_SERVICENOTIFICATIONNUMBER",
    "NOTIFY_HOSTALIAS",
    "NOTIFY_HOSTADDRESS",
    "NOTIFY_SERVICESTATE",
    "NOTIFY_HOSTACKAUTHOR",
    "NOTIFY_SERVICEATTEMPT",
    "NOTIFY_SERVICEACKCOMMENT",
    "NOTIFY_SERVICEPERFDATA",
    "NOTIFY_LASTHOSTSTATEID",
    "NOTIFY_NOTIFICATIONAUTHORNAME",
    "NOTIFY_HOSTNAME",
    "NOTIFY_LASTSERVICEPROBLEMID",
    "NOTIFY_HOSTSTATEID",
    "NOTIFY_SERVICECHECKCOMMAND",
    "NOTIFY_HOST_ADDRESS_4",
    "NOTIFY_CONTACTEMAIL",
    "NOTIFY_LONGHOSTOUTPUT",
    "NOTIFY_HOST_ADDRESS_6",
    "NOTIFY_SERVICEPROBLEMID",
    "NOTIFY_LASTHOSTSTATECHANGE",
    "NOTIFY_NOTIFICATIONCOMMENT",
    "NOTIFY_CONTACTNAME",
    "NOTIFY_CONTACTPAGER",
    "NOTIFY_SERVICEACKAUTHOR",
    "NOTIFY_HOST_ADDRESS_FAMILY",
    "NOTIFY_HOSTGROUPNAMES",
    "NOTIFY_HOSTOUTPUT",
    "NOTIFY_LONGDATETIME",
    "NOTIFY_LASTHOSTSTATE",
    "NOTIFY_SERVICEDESC",
    "NOTIFY_HOSTDOWNTIME",
    "NOTIFY_HOSTTAGS",
    "NOTIFY_LASTSERVICESTATEID",
    "NOTIFY_HOSTNOTIFICATIONNUMBER",
    "NOTIFY_HOSTSTATE",
    "NOTIFY_SERVICESTATEID",
    "NOTIFY_HOSTATTEMPT",
    "NOTIFY_HOSTACKCOMMENT",
    "NOTIFY_HOSTPERFDATA",
    "NOTIFY_LONGSERVICEOUTPUT",
    "NOTIFY_NOTIFICATIONAUTHOR",
    "NOTIFY_LASTSERVICESTATECHANGE",
    "NOTIFY_LASTHOSTPROBLEMID",
    "NOTIFY_HOSTCHECKCOMMAND",
    "NOTIFY_LASTHOSTUP",
    "NOTIFY_SERVICEGROUPNAMES",
    "NOTIFY_SERVICEOUTPUT",
    "NOTIFY_HOSTPROBLEMID",
    "NOTIFY_LASTSERVICESTATE",
    "NOTIFY_DATE",
    "NOTIFY_SHORTDATETIME",
    "NOTIFY_NOTIFICATIONTYPE",
    "NOTIFY_LASTSERVICEOK",
    "NOTIFY_NOTIFICATIONAUTHORALIAS",
    "NOTIFY_LOGDIR",
    "NOTIFY_OMD_SITE",
    "NOTIFY_WHAT",
    "NOTIFY_MONITORING_HOST",
    "NOTIFY_OMD_ROOT",
    "NOTIFY_MICROTIME",
    "NOTIFY_HOSTURL",
    "NOTIFY_SERVICEURL",
    "NOTIFY_LASTHOSTSTATECHANGE_REL",
    "NOTIFY_LASTSERVICESTATECHANGE_REL",
    "NOTIFY_LASTHOSTUP_REL",
    "NOTIFY_LASTSERVICEOK_REL",
    "NOTIFY_CONTACTS",
    "NOTIFY_PREVIOUSHOSTHARDSTATE",
    "NOTIFY_PREVIOUSSERVICEHARDSTATE",
    "NOTIFY_SERVICESHORTSTATE",
    "NOTIFY_LASTHOSTSHORTSTATE",
    "NOTIFY_HOSTSHORTSTATE",
    "NOTIFY_LASTSERVICESHORTSTATE",
    "NOTIFY_PREVIOUSHOSTHARDSHORTSTATE",
    "NOTIFY_PREVIOUSSERVICEHARDSHORTSTATE",
    "NOTIFY_SERVICEFORURL",
    "NOTIFY_HOSTFORURL",
    "NOTIFY_HOSTLABEL_cmk/os_family",
    "NOTIFY_HOSTLABEL_cmk/os_type",
    "NOTIFY_HOSTLABEL_cmk/os_platform",
    "NOTIFY_HOSTLABEL_cmk/os_name",
    "NOTIFY_HOSTLABEL_cmk/os_version",
    "NOTIFY_HOSTLABEL_cmk/device_type",
    "NOTIFY_HOSTLABEL_cmk/site",
    "NOTIFY_PARAMETERS",
    "NOTIFY_CONTACTALIAS",
]
HOST_ENVS = [
    "OMD_SITE",
    "USER",
    "NOTIFY_HOSTALIAS",
    "NOTIFY_HOSTADDRESS",
    "NOTIFY_HOSTACKAUTHOR",
    "NOTIFY_LASTHOSTSTATEID",
    "NOTIFY_NOTIFICATIONAUTHORNAME",
    "NOTIFY_HOSTNAME",
    "NOTIFY_HOSTSTATEID",
    "NOTIFY_SERVICECHECKCOMMAND",
    "NOTIFY_HOST_ADDRESS_4",
    "NOTIFY_CONTACTEMAIL",
    "NOTIFY_LONGHOSTOUTPUT",
    "NOTIFY_HOST_ADDRESS_6",
    "NOTIFY_LASTHOSTSTATECHANGE",
    "NOTIFY_NOTIFICATIONCOMMENT",
    "NOTIFY_CONTACTNAME",
    "NOTIFY_CONTACTPAGER",
    "NOTIFY_HOST_ADDRESS_FAMILY",
    "NOTIFY_HOSTGROUPNAMES",
    "NOTIFY_HOSTOUTPUT",
    "NOTIFY_LONGDATETIME",
    "NOTIFY_LASTHOSTSTATE",
    "NOTIFY_HOSTDOWNTIME",
    "NOTIFY_HOSTTAGS",
    "NOTIFY_HOSTNOTIFICATIONNUMBER",
    "NOTIFY_HOSTSTATE",
    "NOTIFY_HOSTATTEMPT",
    "NOTIFY_HOSTACKCOMMENT",
    "NOTIFY_HOSTPERFDATA",
    "NOTIFY_NOTIFICATIONAUTHOR",
    "NOTIFY_LASTHOSTPROBLEMID",
    "NOTIFY_HOSTCHECKCOMMAND",
    "NOTIFY_LASTHOSTUP",
    "NOTIFY_HOSTPROBLEMID",
    "NOTIFY_DATE",
    "NOTIFY_SHORTDATETIME",
    "NOTIFY_NOTIFICATIONTYPE",
    "NOTIFY_NOTIFICATIONAUTHORALIAS",
    "NOTIFY_LOGDIR",
    "NOTIFY_OMD_SITE",
    "NOTIFY_WHAT",
    "NOTIFY_MONITORING_HOST",
    "NOTIFY_OMD_ROOT",
    "NOTIFY_MICROTIME",
    "NOTIFY_HOSTURL",
    "NOTIFY_LASTHOSTSTATECHANGE_REL",
    "NOTIFY_LASTHOSTUP_REL",
    "NOTIFY_CONTACTS",
    "NOTIFY_PREVIOUSHOSTHARDSTATE",
    "NOTIFY_LASTHOSTSHORTSTATE",
    "NOTIFY_HOSTSHORTSTATE",
    "NOTIFY_PREVIOUSHOSTHARDSHORTSTATE",
    "NOTIFY_HOSTFORURL",
    "NOTIFY_HOSTLABEL_cmk_os_family",
    "NOTIFY_HOSTLABEL_cmk_os_type",
    "NOTIFY_HOSTLABEL_cmk_os_platform",
    "NOTIFY_HOSTLABEL_cmk_os_name",
    "NOTIFY_HOSTLABEL_cmk_os_version",
    "NOTIFY_HOSTLABEL_cmk_device_type",
    "NOTIFY_HOSTLABEL_cmk_site",
    "NOTIFY_PARAMETERS",
    "NOTIFY_CONTACTALIAS",
]


def notify_sdp(
    notification_type: str, env_keys: list, endpoint_suffix: str, session, api_url: str
):
    data = {
        key: value
        for key in env_keys
        if (value := os.environ.get(key)) is not None and value != ""
    }
    try:
        response = session.post(
            f"{api_url}/notify/{endpoint_suffix}", data=json.dumps(data)
        )
        if response.status_code == 409:
            print("Problem id has already been acknowledged.")
            exit(2)
        elif response.status_code == 422:
            print("Missing data. Maybe a env is missing or wrongly formatted")
            print(str(response.content))
            exit(1)
        elif response.status_code != 200:
            print(f"Uncatched Non-200 status from /notify/{endpoint_suffix}.")
            print(str(response.content))
            exit(1)
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            print("Failed to decode the response from api to JSON.")
            print(str(response.content))
            exit(1)
        if not response_data:
            print("Received empty JSON response. Exiting.")
            exit(1)
        if response_data.get("success"):
            request = response_data.get("request")
            if not request:
                print("Ticket might already been created.")
                exit(0)
            else:
                print(
                    f"Successfully created an SDP ticket with ID {request.get('id')}."
                )

        else:
            print(response_data)
            exit(1)
    except Exception:
        print(f"Failed to notify the API for {notification_type}.")
        print(tb.format_exc())
        exit(1)


NOTIFICATION_TYPE = NOTIFICATION_TYPE.lower()

if NOTIFICATION_TYPE == "service":
    notify_sdp("service", SERVICE_ENVS, "service", session, API_URL)
elif NOTIFICATION_TYPE == "host":
    notify_sdp("host", HOST_ENVS, "host", session, API_URL)
else:
    print("Invalid NOTIFICATION_TYPE.")
    exit(1)
