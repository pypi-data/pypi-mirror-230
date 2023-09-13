from datetime import datetime
from typing import Dict, List
from datetime import datetime
import uuid

class Source(str):
    pass

class Attachment:
    def __init__(self, id_attachment: str = "", uri: str = "", file_type = "", file_extension:str = "", size: int = 0):
        self.id = id_attachment
        self.uri = uri
        self.file_type = file_type
        self.file_extension = file_extension
        self.size = size

    def to_dict(self):
        return {
            "id": self.id,
            "uri": self.uri,
            "file_type": self.file_type,
            "file_extension": self.file_extension,
            "size": self.size
        }

class Event:
    """
    Time based events
    """
    def __init__(self,
                 user_id: str,
                 organization_guid: str,
                 application: str,
                 app: str,
                 app_type: str,
                 operation: str,
                 operation_type: str,
                 event_guid: str,
                 staging_guid: str,
                 platform_id: str,
                 organization_id: str,
                 local_timezone: str,
                 timestamp: datetime,
                 end_time: datetime,
                 timestamp_local: datetime,
                 end_time_local: datetime,
                 duration: float,
                 description: str,
                 title: str,
                 url: str,
                 site: str,
                 url_domain: str,
                 files: List[dict],
                 action_type: str,
                 geolocation: dict,
                 ipv4: str,
                 local_ipv4: str,
                 size: int,
                 sha2: str,
                 created_time: datetime,
                 last_updated: datetime,
                 email_subject: str,
                 from_address: str,
                 to_address: str,
                 email_cc: str,
                 email_bcc: str,
                 email_imid: str,
                 phone_result: str,
                 record_url: str,
                 recording_url: str,
                 record_id: int):
        
        self.user_id = user_id
        self.organization_guid = organization_guid
        self.application = application
        self.app = app
        self.app_type = app_type
        self.operation = operation
        self.operation_type = operation_type
        self.event_guid = event_guid
        self.staging_guid = staging_guid
        self.platform_id = platform_id
        self.organization_id = organization_id
        self.local_timezone = local_timezone
        self.timestamp = timestamp
        self.end_time = end_time
        self.timestamp_local = timestamp_local
        self.end_time_local = end_time_local
        self.duration = duration
        self.description = description
        self.title = title
        self.url = url
        self.site = site
        self.url_domain = url_domain
        self.files = files
        self.action_type = action_type
        self.geolocation = geolocation
        self.ipv4 = ipv4
        self.local_ipv4 = local_ipv4
        self.size = size
        self.sha2 = sha2
        self.created_time = created_time
        self.last_updated = last_updated
        self.email_subject = email_subject
        self.from_address = from_address
        self.to_address = to_address
        self.email_cc = email_cc
        self.email_bcc = email_bcc
        self.email_imid = email_imid
        self.phone_result = phone_result
        self.record_url = record_url
        self.recording_url = recording_url
        self.record_id = record_id

class Timeslot:
    def __init__(self,
                 timeslot: int,
                 timeslot_local: int,
                 hour: int,
                 minute: int,
                 day: int,
                 month: int,
                 year: int,
                 week: int,
                 weekday: int,
                 hour_local: int,
                 minute_local: int,
                 day_local: int,
                 month_local: int,
                 year_local: int,
                 week_local: int,
                 weekday_local: int,
                 mouse_clicks: int,
                 keyboard_clicks: int,
                 activity_pct: int,
                 action_type: str):
        
        self.timeslot = timeslot
        self.timeslot_local = timeslot_local
        self.hour = hour
        self.minute = minute
        self.day = day
        self.month = month
        self.year = year
        self.week = week
        self.weekday = weekday
        self.hour_local = hour_local
        self.minute_local = minute_local
        self.day_local = day_local
        self.month_local = month_local
        self.year_local = year_local
        self.week_local = week_local
        self.weekday_local = weekday_local
        self.mouse_clicks = mouse_clicks
        self.keyboard_clicks = keyboard_clicks
        self.activity_pct = activity_pct
        self.action_type = action_type


# TODO => Delete the following classes (legacy)

class GenericEvent:
    """Generic event inside the staging area
    """
    def __init__(self, event_guid: str, user_guid: str, timestamp_utc: datetime, loadbatch_id: int, raw_details: str, application: str):
        self.event_guid = event_guid
        self.user_guid = user_guid
        self.timestamp_utc = timestamp_utc
        self.loadbatch_id = loadbatch_id
        self.raw_details = raw_details
        self.application = application

    def to_dict(self):
        return {
            "event_guid": self.event_guid,
            "user_guid": self.user_guid,
            "timestamp_utc": self.timestamp_utc,
            "loadbatch_id": self.loadbatch_id,
            "raw_details": self.raw_details,
            "application": self.application
        }

class FileEvent(GenericEvent):
    def __init__(self, event_guid: str, user_guid: str,  timestamp_utc: datetime, loadbatch_id: int, raw_details: str, operation: str, version_source_uri: Attachment, source_uri: Attachment, application: str):
        super().__init__(event_guid, user_guid,  timestamp_utc, loadbatch_id, raw_details, application=application)
        self.operation = operation
        self.version_source_uri = version_source_uri
        self.source_uri = source_uri

    def to_dict(self):
        event_dict = super().to_dict()
        event_dict.update({
            "operation": self.operation,
            "version_source_uri": self.version_source_uri.to_dict(),
            "source_uri": self.source_uri.to_dict(),
        })
        return event_dict

class SalesEvent(GenericEvent):
    """Version 2.0 Introduction with support for sales events
    2023-05-12 17:53:20: Where are the 
    """
    def __init__(self, event_guid: str, user_guid: str,  timestamp_utc: datetime, loadbatch_id: int, raw_details: str, operation: str, category: str, application: str, description: str):
        super().__init__(event_guid, user_guid,  timestamp_utc, loadbatch_id, raw_details, application=application)
        self.operation = operation #activity__c
        self.category = category # Object being dealed: Opportunity, Lead, Account, Contact, etc.
        self.description = description # Description of the activity

    def to_dict(self):
        event_dict = super().to_dict()
        event_dict.update({
            "operation": self.operation,
            "category": self.category,
            "description": self.description
        })
        return event_dict

class ChromeEvent(SalesEvent):
    """Verion 3.0 Introduction with support for Chrome events This would be the mapped end interface.

        start_time	str
        end_time	str
        duration	double
        title	str
        description	str
        url	
        attachments	<ST-Attachment>List({id, url, file_type, file_extension_size})
        action_origin	str
        span_guid	String
        root_reference	STRING
        root_start	Datetime
        root_end	Datetime
        root_duration	Number


    """

    def __init__(self, event_guid: str, user_guid: str, timestamp_utc: datetime, loadbatch_id: int, raw_details: str, operation: str, category: str, application: str, description: str, 
                 start_time: str, end_time: str, duration: float, 
                 title: str, url: str, attachments: Dict[str, Attachment], 
                 action_origin: str, span_guid: str, root_reference: str, root_start: datetime, root_end: datetime, root_duration: float):
        super().__init__(event_guid, user_guid, timestamp_utc, loadbatch_id, raw_details, operation, category, application, description)
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.title = title
        self.url = url
        self.attachments = attachments
        self.action_origin = action_origin
        self.span_guid = span_guid
        self.root_reference = root_reference
        self.root_start = root_start
        self.root_end = root_end
        self.root_duration = root_duration




    def to_dict(self):
        event_dict = super().to_dict()
        event_dict.update({
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "title": self.title,
            "url": self.url,
            "attachments": self.attachments,
            "action_origin": self.action_origin,
            "span_guid": self.span_guid,
            "root_reference": self.root_reference,
            "root_start": self.root_start,
            "root_end": self.root_end,
            "root_duration": self.root_duration
        })
        return event_dict
        

class StagingModel():
    def __init__(self, version = "", connector_guid="", type = "", organization_guid = "", item_count = 2, details = [], hash_1 = "", hash_2 = ""):
        self.guid = str(uuid.uuid4()) #Random GUID
        self.version = version
        self.connector_guid = connector_guid
        self.type = type
        self.organization_guid = organization_guid
        self.item_count = item_count
        self.details = details
        self.hash_1 = hash_1
        self.hash_2 = hash_2

    def to_dict(self):
        return {
            "guid": self.guid,
            "version": self.version,
            "connector_guid": self.connector_guid,
            "type": self.type,
            "organization_guid": self.organization_guid,
            "actor": self.actor,
            "item_count": self.item_count,
            "details": self.details,
            "hash_1": self.hash_1,
            "hash_2": self.hash_2
        }
    
    def hash_model(self):
        """Using the content (details) it hashes into an secure key
        """
        return ""

    def test_hash(self, key):
        """Pass the key in order to unhash and test if the content hadn't een modified

        Args:
            key (_type_): _description_

        Returns:
            _type_: _description_
        """
        return True
    
    
    def populate_properties_from_dict(self, data: dict):
        """
        Populate the instance properties from a dictionary.
        """
        if 'guid' in data:
            self.guid = data['guid']
        if 'version' in data:
            self.version = data['version']
        if 'connector_guid' in data:
            self.connector_guid = data['connector_guid']
        if 'activity' in data:
            self.type = data['activity']
        if 'organization_guid' in data:
            self.organization_guid = data['organization_guid']
        if 'actor' in data:
            self.actor = data['actor']
        if 'item_count' in data:
            self.item_count = data['item_count']
        if 'details' in data:
            self.details = data['details']
        if 'hash_1' in data:
            self.hash_1 = data['hash_1']
        if 'hash_2' in data:
            self.hash_2 = data['hash_2']
    



