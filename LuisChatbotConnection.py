#!/Library/anaconda3/envs/LuisChatbot/bin/python
"""

"""
from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from msrest.authentication import CognitiveServicesCredentials
import datetime
import configparser
import os


def initiateConnection():
    """
    This Function reads the ConfigurationInput.Ini file to create a connection with the Remote Luis platform.
    To get Details click on the NameInitials on the right top corner of the screen and
    :return: Client ID
    """
    configurationInput = "ConfigurationInput.ini"
    if not os.path.exists(configurationInput):
        exit("The {} file is missing which holds the Login details".format(configurationInput))
        pass
    config = configparser.ConfigParser()
    config.read(configurationInput)
    if 'Luis Bot' not in config.sections():
        exit("The config file does not have a 'Luis Bot' section")
        pass
    endpoint = config.get('Luis Bot', 'Endpoint_URL')
    authoring_key = config.get('Luis Bot', 'Primary_Key')
    return LUISAuthoringClient(endpoint, CognitiveServicesCredentials(authoring_key))


def create_app(clientID, app_name, app_desc, app_version, app_locale):
    # Create a new LUIS app
    app_id = clientID.apps.add(dict(name=app_name,
                                    initial_version_id=app_version,
                                    description=app_desc,
                                    culture=app_locale))
    print("Created LUIS app {}\n    with ID {}".format(app_name, app_id))
    return app_id, app_version


def add_intents(clientID, app_id, app_version, intentName):
    intentId = clientID.model.add_intent(app_id, app_version, intentName)
    print("Intent {} with ID {} added.".format(intentName, intentId))
    pass


def add_entities(clientID, app_id, app_version, entityName, roleList):
    EntityId = clientID.model.add_entity(app_id, app_version, entityName)
    print("Entity {} with EntityId {} added.".format(entityName, EntityId))
    for role in roleList:
        originRoleId = clientID.model.create_entity_role(app_id, app_version, EntityId, role)
        print("Role {} with RoleId {} has been added to Entity {}.".format(role, originRoleId, entityName))
    pass


def create_utterance(intent, utterance, *labels):
    """Add an example LUIS utterance from utterance text and a list of
       labels.  Each label is a 2-tuple containing a label name and the
       text within the utterance that represents that label.
       Utterances apply to a specific intent, which must be specified."""
    text = utterance.lower()

    def label(name, value):
        value = value.lower()
        start = text.index(value)
        return dict(entity_name=name, start_char_index=start,
                    end_char_index=start + len(value))

    return dict(text=text, intent_name=intent,
                entity_labels=[label(n, v) for (n, v) in labels])


def add_utterances(clientID, app_id, app_version, utterances):
    # Add the utterances in batch. You may add any number of example utterances
    # for any number of intents in one call.
    clientID.examples.batch(app_id, app_version, utterances)
    print("{} example utterance(s) added.".format(len(utterances)))
    pass


def train_app(clientID, app_id, app_version):
    response = clientID.train.train_version(app_id, app_version)
    waiting = True
    while waiting:
        info = clientID.train.get_status(app_id, app_version)
        # get_status returns a list of training statuses, one for each model. Loop through them and make sure all are
        # done.
        waiting = any(map(lambda x: 'Queued' == x.details.status or 'InProgress' == x.details.status, info))
        if waiting:
            print("Waiting 10 seconds for training to complete...")
            datetime.time.sleep(10)


def publish_app(clientID, app_id, app_version):
    response = clientID.apps.publish(app_id, app_version, is_staging=True)
    print("Application published. Endpoint URL: " + response.endpoint_url)


if __name__ == "__main__":
    client = initiateConnection()
    print("Connection Completed")

    app_name = "FlightBooking {}".format(datetime.datetime.now())
    app_desc = "Flight booking app built with LUIS Python SDK."
    app_version = "0.1"
    app_locale = "en-us"

    app_id = create_app(client,app_name,app_desc,app_version,app_locale)
    app_newEntity = ["Location", "Class"]
    app_newEntityRole = [["Origin", "Destination"],[]]

    # for i in range(0, len(app_newEntity)):


#     client.model.add_prebuilt(app_id, app_version, prebuilt_extractor_names=["number", "datetimeV2", "geographyV2", "ordinal"])
#
#     compositeEntityId = client.model.add_composite_entity(app_id, app_version, name="Flight",
#                                       children=["Location", "Class", "number", "datetimeV2", "geographyV2", "ordinal"])
#     print("compositeEntityId {} added.".format(compositeEntityId))


# utterances = [create_utterance("FindFlights", "find flights in economy to Madrid",
#                                    ("Flight", "economy to Madrid"),
#                                    ("Location", "Madrid"),
#                                    ("Class", "economy")),
#                   create_utterance("FindFlights", "find flights to London in first class",
#                                    ("Flight", "London in first class"),
#                                    ("Location", "London"),
#                                    ("Class", "first")),
#                   create_utterance("FindFlights", "find flights from seattle to London in first class",
#                                    ("Flight", "flights from seattle to London in first class"),
#                                    ("Location", "London"),
#                                    ("Location", "Seattle"),
#                                    ("Class", "first"))]
