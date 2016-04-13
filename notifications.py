from gcm import GCM

__author__ = 'gambrinius'

# JSON request


def gcm_notification(registration_ids, title, message):
    API_KEY = ""    # key for API server

    gcm = GCM(API_KEY)

    # registration_ids = []  # tokens from app installed on devices

    notification = {
        "title": title,  # "Bazzzar notification"
        "message": message,  # "message": "Amazing message!!! =)"
        "uri": "market://details?id=gcm.play.android.samples.com.gcmquickstart",
        "icon": "my icon",  # can add "icon"
    }

    response = gcm.json_request(registration_ids=registration_ids,
                                data=notification,
                                collapse_key='awesomeapp_update',  # set param to update last unread notification
                                tag='ssfaefaf',  # test
                                id='idssss',    # test
                                restricted_package_name="gcm.play.android.samples.com.gcmquickstart",
                                priority='high',    # maybe 'normal'
                                delay_while_idle=False)
    # time_to_live from 0 to 2,419,200 seconds (4 weeks)

    # GCM allows a maximum of 4 different collapse keys to be used by the app server per device at any given time
    # Messages not be delivered until the device becomes active by using the delay_while_idle flag.
    # Note that there is limit of 100 multiple senders.

    # Successfully handled registration_ids
    log_list = list()
    if response and 'success' in response:
        for reg_id, success_id in response['success'].items():
            log_list.append('Successfully sent notification for reg_id {0}'.format(reg_id))
    # When an app server posts a message to GCM and receives a message ID back,
    # it does not mean that the message was already delivered to the device.

    # Handling errors
    if 'errors' in response:
        for error, reg_ids in response['errors'].items():
            # Check for errors and act accordingly
            if error in ['NotRegistered', 'InvalidRegistration']:
                # Remove reg_ids from database
                for reg_id in reg_ids:
                    log_list.append("Removing reg_id: {0} from db".format(reg_id))

    return log_list

"""
    # Replace reg_id with canonical_id in your database
    if 'canonical' in response:
        for reg_id, canonical_id in response['canonical'].items():
            print("Replacing reg_id: {0} with canonical_id: {1} in db".format(reg_id, canonical_id))
"""