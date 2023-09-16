
from ddaptools.aws_classes.config_mapper_df import *
from ddaptools.aws_classes.class_helpers import *
from ddaptools.aws_classes.class_enhancement import *
from ddaptools.aws_classes.class_adapters import *
import json

sample_salesforce_raw_input = {
  "guid": "f27ecb0c-975d-dbac-82af-152b68e89902",
  "previous_guid": "91e52161-2a47-7ea4-8121-186f9b378e4a",
  "version": "1.0.0",
  "date": "2023-04-27 16:45:07",
  "connector_guid":"salesforce-testing-connector",
  "organization_guid": "123e4567-e89b-12d3-a456-client",
  "details": [
  {
    "Id": "a1k7c000001fqySAAQ",
    "Name": "0000043628",
    "OwnerId": "0055x00000C68rTAAR",
    "User__c": "0055x00000C68rTAAR",
    "sfid__c": "00Q7c00000Et2nGEAR",
    "Actor__c": "nwang@ddapfilings.com",
    "Object__c": "LEAD",
    "Activity__c": "UPDATE",
    "CreatedById": "0055x00000C68rTAAR",
    "Source_IP__c": "68.160.247.154",
    "ActionDate__c": "2023-04-27T20:11:10.000Z",
    "Description__c": "Peter Pan ()",
    "Record_Link__c": "<a href=\"/00Q7c00000Et2nGEAR\" target=\"_blank\">LEAD</a>",
    "SessionType__c": "Aura",
    "IsInteractive__c": True,
    "LastModifiedById": "0055x00000C68rTAAR"
  },
  {
    "Id": "a1k7c000001fqyTAAQ",
    "Name": "0000043632",
    "OwnerId": "0055x00000C68rTAAR",
    "User__c": "0055x00000C68rTAAR",
    "sfid__c": "00Q7c00000Et2nGEAR",
    "Actor__c": "nwang@ddapfilings.com",
    "Object__c": "LEAD",
    "Activity__c": "UPDATE",
    "CreatedById": "0055x00000C68rTAAR",
    "Source_IP__c": "68.160.247.154",
    "ActionDate__c": "2023-04-27T20:14:18.000Z",
    "Description__c": "Peter Pan ()",
    "Record_Link__c": "<a href=\"/00Q7c00000Et2nGEAR\" target=\"_blank\">LEAD</a>",
    "SessionType__c": "Aura",
    "IsInteractive__c": True,
    "LastModifiedById": "0055x00000C68rTAAR"
  },
  {
    "Id": "a1k7c000001fqyWAAQ",
    "Name": "0000043627",
    "OwnerId": "0055x00000C68rTAAR",
    "User__c": "0055x00000C68rTAAR",
    "sfid__c": "00Q7c00000Et2nGEAR",
    "Actor__c": "nwang@ddapfilings.com",
    "Object__c": "LEAD",
    "Activity__c": "UPDATE",
    "CreatedById": "0055x00000C68rTAAR",
    "Source_IP__c": "68.160.247.154",
    "ActionDate__c": "2023-04-27T20:09:28.000Z",
    "Description__c": "Peter Pan ()",
    "Record_Link__c": "<a href=\"/00Q7c00000Et2nGEAR\" target=\"_blank\">LEAD</a>",
    "SessionType__c": "Aura",
    "IsInteractive__c": True,
    "LastModifiedById": "0055x00000C68rTAAR"
  },
  {
    "Id": "a1k7c000001fqybAAA",
    "Name": "0000043629",
    "OwnerId": "0055x00000C68rTAAR",
    "User__c": "0055x00000C68rTAAR",
    "sfid__c": "00Q7c00000Et2nGEAR",
    "Actor__c": "nwang@ddapfilings.com",
    "Object__c": "LEAD",
    "Activity__c": "UPDATE",
    "CreatedById": "0055x00000C68rTAAR",
    "Source_IP__c": "68.160.247.154",
    "ActionDate__c": "2023-04-27T20:11:14.000Z",
    "Description__c": "Peter Pan ()",
    "Record_Link__c": "<a href=\"/00Q7c00000Et2nGEAR\" target=\"_blank\">LEAD</a>",
    "SessionType__c": "Aura",
    "IsInteractive__c": True,
    "LastModifiedById": "0055x00000C68rTAAR"
  },
  {
    "Id": "a1k7c000001fqycAAA",
    "Name": "0000043633",
    "OwnerId": "0055x00000C68rTAAR",
    "User__c": "0055x00000C68rTAAR",
    "sfid__c": "00Q7c00000Et2nGEAR",
    "Actor__c": "nwang@ddapfilings.com",
    "Object__c": "LEAD",
    "Activity__c": "UPDATE",
    "CreatedById": "0055x00000C68rTAAR",
    "Source_IP__c": "68.160.247.154",
    "ActionDate__c": "2023-04-27T20:14:21.000Z",
    "Description__c": "Peter Pan ()",
    "Record_Link__c": "<a href=\"/00Q7c00000Et2nGEAR\" target=\"_blank\">LEAD</a>",
    "SessionType__c": "Aura",
    "IsInteractive__c": True,
    "LastModifiedById": "0055x00000C68rTAAR"
  },
  {
    "Id": "a1k7c000001fqylAAA",
    "Name": "0000043631",
    "OwnerId": "0055x00000C68rTAAR",
    "User__c": "0055x00000C68rTAAR",
    "sfid__c": "00Q7c00000Et2nGEAR",
    "Actor__c": "nwang@ddapfilings.com",
    "Object__c": "LEAD",
    "Activity__c": "UPDATE",
    "CreatedById": "0055x00000C68rTAAR",
    "Source_IP__c": "68.160.247.154",
    "ActionDate__c": "2023-04-27T20:14:14.000Z",
    "Description__c": "Peter Pan ()",
    "Record_Link__c": "<a href=\"/00Q7c00000Et2nGEAR\" target=\"_blank\">LEAD</a>",
    "SessionType__c": "Aura",
    "IsInteractive__c": True,
    "LastModifiedById": "0055x00000C68rTAAR"
  },
  {
    "Id": "a1k7c000001fqyqAAA",
    "Name": "0000043634",
    "OwnerId": "0055x00000C68rTAAR",
    "User__c": "0055x00000C68rTAAR",
    "sfid__c": "00Q7c00000Et2nGEAR",
    "Actor__c": "nwang@ddapfilings.com",
    "Object__c": "LEAD",
    "Activity__c": "UPDATE",
    "CreatedById": "0055x00000C68rTAAR",
    "Source_IP__c": "68.160.247.154",
    "ActionDate__c": "2023-04-27T20:18:23.000Z",
    "Description__c": "Peter Pan ()",
    "Record_Link__c": "<a href=\"/00Q7c00000Et2nGEAR\" target=\"_blank\">LEAD</a>",
    "SessionType__c": "Aura",
    "IsInteractive__c": True,
    "LastModifiedById": "0055x00000C68rTAAR"
  }
],
  "hash_1": "d8298e88a929de23ab1bcb06f7a05d0e694f871fb15ef31800d8027d0f76a2ff",
  "hash_2": "3baea71e7edcb8b8aa4417fb640c0fa0d7f9791c8a2b17ca3f499d10f7a43dcd"
}


# UPDATE : Reflect changes in details here.
sample_chrome_raw_input = {
    'guid': '387a26ff-ceed-5015-a6c9-a2cad90329c0',
    'previous_guid': 'b5a496cb-8bfb-39fd-67f2-4d14feef1fa1',
    'version': "1.0.0",
    'date': "2023-05-12 17:50:00.026",
    'connector_guid': "chrome-extension-ddap-1",
    "organization_guid": "organization-1",
    "details":[
      {
      "domain": "www.google.com",
      "endTime": "2023-06-12T14:24:11.821Z",
      "guid": "ac30bcd1-3e16-5ade-6bd6-8bb51735d053",
      "incognito": False,
      "interactions": {},
      "isEventComplete": False,
      "params": {},
      "spanGUID": "460a111f-8bbf-870c-0428-cd927ba2b7c4",
      "spanSequence": 1,
      "spanStartTime": "2023-06-12T14:23:40.480Z",
      "timestamp": "2023-06-12T14:23:40.480Z",
      "title": "queriable site? - Google Search",
      "type": "tab-focus",
      "duration": 31.34,
      "url": "https://www.google.com/search?q=queriable+site%3F&rlz=1C1GCEA_enUS1016US1016&oq=queriable+site%3F&aqs=chrome..69i57j33i10i160.2846j1j7&sourceid=chrome&ie=UTF-8"
    },
    {
      "domain": "www.google.com",
      "timestamp": "2023-06-12T14:24:11.821Z",
      "endTime": "2023-06-12T14:24:11.821Z",
      "duration": 10,
      "guid": "ac30bcd1-3e16-5ade-6bd6-8bb51735d054",
      "incognito": False,
      "interactions": {},
      "isEventComplete": True,
      "params": {},
      "spanGUID": "460a111f-8bbf-870c-0428-cd927ba2b7c4",
      "spanSequence": 1,
      "spanStartTime": "2023-06-12T14:23:40.480Z",
      "title": "queriable site? - Google Search (Part 2)",
      "type": "tab-focus",
      "url": "https://www.google.com/search?q=queriable+site%3F&rlz=1C1GCEA_enUS1016US1016&oq=queriable+site%3F&aqs=chrome..69i57j33i10i160.2846j1j7&sourceid=chrome&ie=UTF-8"
    },
    # An extra large event.
    {
    "domain": "pnp.github.io",
    "timestamp": "2023-06-12T14:23:36.135Z",
    "endTime": "2023-06-12T15:43:40.477Z",
    "duration": 1204.34,
    "guid": "fee6724b-2abe-f829-d6a3-46eb5bd6c477",
    "incognito": False,
    "interactions": {
        "scroll": 1
    },
    "isEventComplete": True,
    "params": {},
    "spanGUID": "58e82818-800d-249e-dbac-42617821dbdb",
    "spanSequence": 0,
    "spanStartTime": "2023-06-12T14:23:36.135Z",
    "title": "queryable - PnP/PnPjs",
    "type": "tab-focus",
    "url": "https://pnp.github.io/pnpjs/queryable/queryable/"
  },
  {
    "id": 16,
    "url": "https://mazzzystar.github.io/images/2023-05-10/superCLUE.jpg",
    "guid": "0adeb6d2-c889-4592-0b46-e43e887e4d71",
    "mime": "image/jpeg",
    "type": "download",
    "state": "complete",
    "title": "The Leverage of LLMs for Individuals | TL;DR",
    "danger": "safe",
    "domain": "mazzzystar.github.io",
    "exists": True,
    "paused": False,
    "endTime": "2023-05-11T16:03:31.427Z",
    "fileSize": 72801,
    "filename": "C:\\Users\\NelsonWang\\Downloads\\guide\\superCLUE (2).jpg",
    "finalUrl": "https://mazzzystar.github.io/images/2023-05-10/superCLUE.jpg",
    "referrer": "https://mazzzystar.github.io/2023/05/10/LLM-for-individual/",
    "canResume": False,
    "incognito": False,
    "startTime": "2023-05-11T16:03:28.431Z",
    "timestamp": "2023-05-11T16:03:31.434Z",
    "totalBytes": 72801,
    "bytesReceived": 72801
  },
  {
    "url": "https://imgbb.com/",
    "guid": "cfe2aea7-dfdf-b8a7-1d55-c870e14fc203",
    "type": "upload",
    "files": [
      {
        "name": "iamge-.jpg",
        "size": 17292,
        "type": "image/jpeg",
        "lastModified": 1683577149679,
        "lastModifiedDate": "2023-05-08T20:19:09.679Z",
        "webkitRelativePath": ""
      }
    ],
    "title": "ImgBB — Upload Image — Free Image Hosting",
    "domain": "imgbb.com",
    "timestamp": "2023-05-11T16:01:02.290Z"
  },
  
],
    "hash_1": "d8298e88a929de23ab1bcb06f7a05d0e694f871fb15ef31800d8027d0f76a2ff",
    "hash_2": "3baea71e7edcb8b8aa4417fb640c0fa0d7f9791c8a2b17ca3f499d10f7a43dcd"
}


# Grab local json file named sample_windows
sample_widows_raw_input = {}



DEBUG = False


def test_salesforce_enahncement_integration():
    """Tests if things can be updated adapted then enhanced then published, no checks
    """
    organizationDBProvider = MockOrganizationQuerier()
    credentials = {}
    settings = {}
    publishingDBProvider = MockDatabaseProvider(credentials=credentials, settings=settings)

    basic_enhancment = BasicEnhancement(
        organizationDBProvider=organizationDBProvider,
        publishingDBProvider=publishingDBProvider,
        source_adapter=SalesforceAdapter(organizationQuerier=organizationDBProvider)
    )

    enhanced_events: dict["events": List[Event], "timeslots": List[Timeslot]] = basic_enhancment.transform(staging_events_events=sample_salesforce_raw_input)
    print(type(enhanced_events), enhanced_events)
    # basic_enhancment.publish(enhanced_events=enhanced_events)
    # basic_enhancment.publish(enhanced_events=enhanced_events["events"], table_name="events_sf.json")
    # basic_enhancment.publish(enhanced_events=enhanced_events["timeslots"], table_name="timeslots_sf.json")


def xtest_chrome_enhancment_integration():
  """Tests if the adapter can be used correctly
  """
  organizationDBProvider = MockOrganizationQuerier()
  credentials = {}
  settings = {}
  publishingDBProvider = MockDatabaseProvider(credentials=credentials, settings=settings)

  basic_enhancment = BasicEnhancement(
      organizationDBProvider=organizationDBProvider,
      publishingDBProvider=publishingDBProvider,
      source_adapter=ChromeAdapter(organizationQuerier=organizationDBProvider)
  )

  enhanced_events: dict["events": List[Event], "timeslots": List[Timeslot]] = basic_enhancment.transform(staging_events_events=sample_chrome_raw_input)
  print(enhanced_events)
  # basic_enhancment.publish(enhanced_events=enhanced_events["events"])
  basic_enhancment.publish(enhanced_events=enhanced_events["timeslots"], table_name="timeslots.json", status="PROCESSED")
  basic_enhancment.publish(enhanced_events=enhanced_events["events"], table_name="events.json" )







