from abc import ABC, abstractmethod
from typing import List
from ddaptools.dda_constants import *
from ddaptools.dda_models import *
import json, random, string

from pytz import timezone
import math, datetime, pytz
from dateutil import parser, tz
import json
from typing import List


import psycopg2
from psycopg2.extras import DictCursor
# awsconfig_mapper import ConfigMapper



class DatabaseProvider(ABC):
    def __init__(self, credentials, settings):
        self.credentials = credentials
        self.settings = settings
        
    def update_status_staging(self, staging_event_guid, status, processed_item_count = 0, processing_error_count = 0):
        """Updates the status of the staging event
        """
        print("Updating status of staging event", staging_event_guid, "to", status)
        print("Processed item count:", processed_item_count)
        print("Processing error count:", processing_error_count)

    @abstractmethod
    def publish(self, events: List[dict]):
        # print("publishing to database:", events)
        pass

    @abstractmethod
    def getOne(self, key_value, key_column: str = "guid", table_name: str = "events"):
        print("Getting source with: ", key_value, "in", key_column, "column")

class MockDatabaseProvider(DatabaseProvider):
    """Prints publishing and getters, using for debugging, also returns static examples
    Records the json for quick edition and visualization in a local file.
    """
    def __init__(self, credentials, settings):
        super().__init__(credentials, settings)
        self.db = []

    def publish(self, events: List[dict], table_name="mock_db.json"):
        self.db.extend(events)

        # Save as .. code-block:: json
        
        with open(table_name, "w") as f:
            f.write(json.dumps(self.db, indent=4))

        return super().publish(events=events)
    
    def update_status_staging(self, staging_event_guid, status):
        """Updates the status of the staging event
        """
        print("Updating status of staging event", staging_event_guid, "to", status)

    def getOne(self, key_value, key_column: str = "guid", update_status=None):
        super().getOne(key_column)
        try:
            for(i, row) in enumerate(self.db):
                if row[key_column] == key_value:
                    return row
            return []
        except Exception as e:
            # print("key column", key_column, " : ", key_value, "not found")
            # print("Exception:", e)
            # print("self.db", len(self.db))
            for(i, row) in enumerate(self.db):
                print(i, row['guid'])
            return []


class MockStagingDatabaseProviderPrePopulated(MockDatabaseProvider):
    def __init__(self, credentials, settings):
        super().__init__(credentials, settings)
        self.db = STAGING_EVENTS_SAMPLE



class MockStagingDatabaseProviderWithChrome(MockDatabaseProvider):
    """Extension Mock Staging Database of rthe Config mapper to work better with Chrome
    """
    def __init__(self, credentials, settings):
        super().__init__(credentials, settings)
        self.db = STAGING_EVENTS_SAMPLE_WITH_CHROME


import psycopg2
    
class PostgreSQLProvider(DatabaseProvider):
    """Publishes into PostgreSQL as key and expects a body column to be published as  
    """

    def __init__(self, credentials, settings):
        """Initiates with the database credentials, and settings as the specfici tables it is looking for
        Requires:
            pandas
            psycopg2

        Args:
            credentials (dict): Credentails for database {USERNAME, PASSWORD, HOST, DB}
            settings (dict): {TABLE}
        """
        super().__init__(credentials, settings)
        # Initiate SQl connection
        self.connection = psycopg2.connect(user=credentials['USERNAME'], password=credentials['PASSWORD'], host=credentials['HOST'], database=credentials['DB'])
        self.cursor = self.connection.cursor(cursor_factory=DictCursor)
        

    def fetchFromElse(self, fetchFrom: dict, key, elseGets):
        """Fetches value from dictionary otherwise it gets:

        Args:
            fetchFrom (dict): _description_
            key (_type_): _description_
            elseGets (_type_): _description_

        Returns:
            _type_: _description_
        """
        if key in fetchFrom:
            return fetchFrom[key]
        return elseGets
    
    def publish(self, events: List[dict], table_name="mock_db.json"):
        """Publishes
        Expected parameters to have unders settings:
        - TABLENAME
        - COLUMN_NAMES
    
        Args:
            events (List[dict]): List of events to publish.
        """

        # Fetches the proper credentials based on the environemnt


        # Update Settings"
        tablename_events= self.settings.get("TABLENAME_EVENTS", "events")
        column_names_events = self.settings.get("COLUMN_NAMES_EVENTS", [])

        tablename_timeslot = self.settings.get("TABLENAME_TIMESLOT", "timeslot")
        column_names_timeslot = self.settings.get("COLUMN_NAMES_TIMESLOT", [])
        


        # Pushes the changes into SQL
        insert_sql = f"INSERT INTO {tablename_events} ({', '.join(column_names_events)}) VALUES ({', '.join(['%s'] * len(column_names_events))})"
        # # print("Created insert_SQL:", insert_sql)
        # Execute the INSERT statement for each dictionary in the list
        # print("attepting to get rows from events:", events)

        import json
        from typing import List

        def cleanQueryArgument(queryArgument):
            # If the queryArg is a list or dict, format it into a way that is query insertable
            if isinstance(queryArgument, (dict)):
                # If the is List and the first element is a dict, then it is a list of objects
                return json.dumps(queryArgument)
            if isinstance(queryArgument, List) and len(queryArgument) >0 and isinstance(queryArgument[0], dict):
                # return an array of strings of the json
                for(i, item) in enumerate(queryArgument):
                    queryArgument[i] = cleanQueryArgument(item)
            
            return queryArgument

        for row in events:
            values = []
            for col in column_names_events:
                value = row.get(col, None)
                values.append(cleanQueryArgument(value))
            try:
                self.cursor.execute(insert_sql, values)
            except Exception as e:
                print("Exception at publish:", e, "values:", values)
        self.connection.commit()

        # Update the status of the staging table to PROCESSED


    def update_status_staging(self, staging_event_guid, status = "PROCESSED", processed_item_count = 0, processing_error_count = 0):
        """Updates the status of the staging table
        """
        tablename = "staging_events"
        if status is not None:
            if ( False ): print("Updating status of staging table to:", status, "for:", staging_event_guid)
            if(status == "PROCESSING"):
                
                current_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                update_query = f"UPDATE {tablename} SET status = '{status}', processing_start_time = '{current_timestamp}', processing_task = 'BASIC ENHANCEMENT' WHERE guid = '{staging_event_guid}'"
                self.cursor.execute(update_query)
            if(status == "PROCESSED"):
                current_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                update_query = f"UPDATE {tablename} SET status = '{status}', processing_end_time = '{current_timestamp}', processing_item_count = {processed_item_count}, processing_error_count = {processing_error_count} WHERE guid = '{staging_event_guid}'"
                self.cursor.execute(update_query)

            else:
                self.cursor.execute(f"UPDATE {tablename} SET status = '{status}' WHERE guid = '{staging_event_guid}'")
    
            self.connection.commit()
            if ( False ): print(f"update status completed {status} for {staging_event_guid}")
    
    def getOne(self, key_value, key_column: str = "guid", status=None):
        """Gets one
        Expected parameters to have under settings:
        - TABLENAME

        Args:
            source_id (str): _description_
        """
        # Get table name and other settings pdetailsroperties
        
        tablename= self.fetchFromElse(self.settings, "GET_TABLENAME", "event")
        row_dict = {}
        # Gets one of the sources
        self.cursor.execute(f"SELECT * FROM {tablename} WHERE {key_column} = '{key_value}'")
        print("Requested: "+ f"SELECT * FROM {tablename} WHERE {key_column} = '{key_value}'")
        
        row = self.cursor.fetchone()
        if row:
            row_dict = dict(zip([desc[0] for desc in self.cursor.description], row))

            # If is not None, then UPDATE  the status => ""

            if status is not None:
                self.update_status_staging(staging_event_guid=row_dict["guid"], status=status)

            # print(row_dict)
        else:
            print("No rows found")
        return row_dict

class PostgreSQLProviderTimeSlotPlusEventsPublishing(PostgreSQLProvider):
    """This improvement overwrites simple PostgreSQLProvider to be
     both Timeslot and also events to be published on publish time.
    """

    def __init__(self, credentials, settings):
        """Initiates with the database credentials, and settings as the specfici tables it is looking for
        Requires:
            pandas
            psycopg2

        Args:
            credentials (dict): Credentails for database {USERNAME, PASSWORD, HOST, DB}
            settings (dict): {TABLE}
        """
        super().__init__(credentials, settings)
        


        
    def publish(self, events: dict["events": List[dict], "timeslot": List[dict]], table_name=""):
        """Publishes
        Expected parameters to have unders settings:
        - TABLENAME
        - COLUMN_NAMES
    
        Args:
            events (List[dict]): List of events to publish.
        """

        # Fetches the proper credentials based on the environemnt


        # Update Settings"
        tablename_events= self.settings.get("TABLENAME_EVENTS", "events")
        column_names_events = self.settings.get("COLUMN_NAMES_EVENTS", [])

        tablename_timeslot = self.settings.get("TABLENAME_TIMESLOTS", "timeslot")
        column_names_timeslot = self.settings.get("COLUMN_NAMES_TIMESLOTS", [])

        self.publish_to(events["events"], column_names_events, tablename_events, update_span_guid=True)
        self.publish_to(events["timeslots"], column_names_timeslot, tablename_timeslot)




    def publish_to(self, events: List[dict], column_names: List[str], tablename: str, update_span_guid: bool = False):
        """Publishes into the postgresdatabase the timeslot and events
        @param events: List of events to publish.
        @param column_names: List of column names to publish  

        Notes:
        2023-06-15 16:36:20 Initiated Support for handling events and continuing the spanguid.      
    
        Args:
            events (List[dict]): List of events to publish.
        """


        # Pushes the changes into SQL
        insert_sql = f"INSERT INTO {tablename} ({', '.join(column_names)}) VALUES ({', '.join(['%s'] * len(column_names))})"
        def cleanQueryArgument(queryArgument):
            # If the queryArg is a list or dict, format it into a way that is query insertable
            if isinstance(queryArgument, (dict)):
                # If the is List and the first element is a dict, then it is a list of objects
                return json.dumps(queryArgument)
            if isinstance(queryArgument, List) and len(queryArgument) >0 and isinstance(queryArgument[0], dict):
                # return an array of strings of the json
                # seq = 0
                dict_result = {}
                for(i, item) in enumerate(queryArgument):
                    dict_result[i] = item
                return json.dumps(dict_result)
            
            return queryArgument

        for row in events:
            
            # If the update_span_guid setting is True, then post the updates.


            if(update_span_guid):
                # If span_sequence, assume the best case which means 1, 2, 3 and update it by the max
                span_sequence:int = row.get("span_sequence", None)
                print("span_sequence:", span_sequence)

                if(span_sequence is not None and span_sequence > 0):
                    # Otherwise I could ONLY update it if thats the case
                    span_guid:str = row.get("span_guid", None)
                    end_time:datetime.datetime = row.get("end_time", None)
                    # timestamp:datetime.datetime = row.get("datetime", None)
                    self.post_new_end_event_span_guid(span_guid=span_guid, end_time=end_time, timestamp=None)
                    continue  # You want to skip the loop and have ONLY updating the  last recent one.   

            values = []
            for col in column_names:
                value = row.get(col, None)
                values.append(cleanQueryArgument(value))
            # print("values:", values)
            
            
            try:
                self.cursor.execute(insert_sql, values)
            except Exception as e:
                
                print("publishing to "+ tablename +"; received the following events:", events)
                # print("attributes timeslot:", Timeslot.get_attribute_keys())
                print("Insert sql created:", insert_sql)
                print("Exception at publish:", e, "values:", values)
        self.connection.commit()

    def post_new_end_event_span_guid(self, span_guid:str, end_time:datetime.datetime, timestamp=None):
        """
        Gets the event with a specific span_guid from the event table and updates the end_time to the largest value 
        between the current end_time and the provided end_time. If the timestamp argument is not None, 
        it updates the timestamp to the smallest value between the current timestamp (if exists) and the provided timestamp.

        Parameters:
        - span_guid (str): The span_guid of the event to update.
        - end_time (datetime): The new end_time to be set.
        - timestamp (datetime, optional): The new timestamp to be set if not None.
        """

        update_sql = "UPDATE event SET end_time = CASE WHEN end_time < %s THEN %s ELSE end_time END"
        values = [end_time, end_time]

        # if timestamp is not None:
        #     update_sql += ", timestamp = CASE WHEN timestamp IS NULL THEN %s ELSE LEAST(timestamp, %s) END"
        #     values.extend([timestamp, timestamp])

        update_sql += " WHERE span_guid = %s"
        values.append(span_guid)

        try:
            print(f"Update at {span_guid} where update_sql = {update_sql} and values = {values}")
            self.cursor.execute(update_sql, values)
            self.connection.commit()
        except Exception as e:
            print("Failed to update event with span_guid:", span_guid)
            print("Exception:", e)



       
class Utils:
    """Some random utitlities
    
    Requirements:
    - json
    """
    
    def date_related_population(join_events: List[dict]) -> List[dict]:
        """
        For each of the events, populate the date-related items.
        
        Notes:

        2023-06-14 10:26:22 Supports endtime as None.
        If endtime is None:
        
                    # If end_time is None, set the remaining fields to None as well
                    event['end_time'] = None
                    event['end_time_local'] = None
                    event['duration'] = None

        """
        for event in join_events:
            # Convert timestamp to datetime object
            timestamp: datetime.datetime = parser.parse(event['timestamp']).replace(tzinfo=pytz.utc)
            timezone_str: str = event['user_timezone']
            local_timestamp: datetime.datetime = timestamp.astimezone(timezone(timezone_str))
            event['timestamp_local'] = local_timestamp.isoformat()
            event["local_timezone"] = timezone_str


            timeslot = (timestamp.hour * 60 + timestamp.minute) // 10
            timeslot_local = (local_timestamp.hour * 60 + local_timestamp.minute) // 10
            event['timeslot'] = timeslot
            event['timeslot_local'] = timeslot_local

            # Extract UTC date and time components
            event['hour'] = timestamp.hour
            event['minute'] = timestamp.minute
            event['day'] = timestamp.day
            event['month'] = timestamp.month
            event['year'] = timestamp.year
            event['week'] = timestamp.isocalendar()[1]
            event['weekday'] = timestamp.weekday()

            # Extract local date and time components
            event['hour_local'] = local_timestamp.hour
            event['minute_local'] = local_timestamp.minute
            event['day_local'] = local_timestamp.day
            event['month_local'] = local_timestamp.month
            event['year_local'] = local_timestamp.year
            event['week_local'] = local_timestamp.isocalendar()[1]
            event['weekday_local'] = local_timestamp.weekday()

            # Check if end_time is None
            if event['end_time'] is not None:
                # Convert end_time to datetime object
                endtime = parser.parse(event['end_time'])

                # Convert timestamp and end_time to the specified timezone
                local_endtime = endtime.astimezone(timezone(timezone_str))

                # Populate the timestamp_local, end_time_local, and duration fields as isoformat strings
                event['end_time_local'] = local_endtime.isoformat()
                event['duration'] = (endtime - timestamp).total_seconds() / 3600
            else:
                # If end_time is None, set the remaining fields to None as well
                event['end_time'] = None
                event['end_time_local'] = None
                event['duration'] = None

        return join_events


    def createRandomStr(length:int  = 10):
        """Generates random string with the length indicated

        Args:
            length (int, optional): length of the random string. Defaults to 10.
        """
        # Generate a random string
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        return random_string

    def escapedStrToListOfObjects(escapedStr: str):
        """Escapes String that might appear on the database or queries into a list of objects or dict

        Args:
            escapedStr (str): escaped String

        Returns:
            List: List of objects/or dict
            
        '[         {\"name\": \"Alice\", \"age\": 25, \"gender\": \"F\"},         {\"name\": \"Bob\", \"age\": 30, \"gender\": \"M\"},         {\"name\": \"Charlie\", \"age\": 35, \"gender\": \"M\"}     ]'
        ->
        [{'name': 'Alice', 'age': 25, 'gender': 'F'}, {'name': 'Bob', 'age': 30, 'gender': 'M'}, {'name': 'Charlie', 'age': 35, 'gender': 'M'}]
        """
        try:
            escapedStr = escapedStr.strip()
            return json.loads(escapedStr)
        except Exception as e:
            return []

    def NoneSafe(dictItem:dict, key:string, default=None):
        """Safely gets the value from the dictionary, if it does not exist, it returns the default

        Args:
            dictItem (dict): dictionary to get the value from
            key (string): key to get the value from
            default (string): default value to return if the key does not exist

        Returns:
            str: Value that is returned safely
        """
        # return dictItem.get(key, default)
        if key in dictItem:
            try:
                return dictItem[key]
            except Exception as e:
                # print("Exception at NoneSafe:", e
                #       , "dictItem:", type(dictItem) ,dictItem, 
                #       "key:",  type(key),key)
                pass
        return default
    
    

    def eventDataIntoTimeSlots(eventData: dict, limit_minutes_per_slot=10) -> List[Timeslot]:
        """
        Split the events into time slots based on the next 10th multiple of minutes.

        Notes + Decision: 
        - 2023-06-14 10:07:29 If the duration is None then, it should still create an empty Timeslot 
        - 2023-06-14 15:42:32 It should have an increasing if the span_sequence is None span_sequence when 
        splicing. + Should contain also have the span_guid if it is None => event_guid

        Args:
            eventData (dict): Event data dictionary.
            limit_minutes_per_slot (int, optional): The maximum time in minutes to split the events into. Defaults to 10.

        Returns:
            List[Timeslot]: A list of Timeslot events.
        """
        timeslots_res = []
        timeslots_event_data = []
        duration = eventData["duration"]
        span_sequence = eventData["span_sequence"] #should be 0 if not provided
        span_guid = eventData["span_guid"]

        def createEventDataCopy(eventData, start_time, current_endtime):
            """Creates a copy of evetData but overwriting the startTIme and current_endtime

            Args:
                eventData (EventData): original eventData to copy with
                start_time (datetime): start datetime for the current event to overwrite the eventData copy with
                current_endtime (datetime): end datetime for the current event to overwrite the eventData copy with

            Returns:
                EventData: Copy of the Event data with the overwriten start and endtimes
            """
            eventDataCopy = eventData.copy()
            eventDataCopy["timestamp"] = start_time
            eventDataCopy["end_time"] = current_endtime
            eventDataCopy["span_sequence"] = span_sequence
            eventDataCopy["span_guid"] = span_guid
            
            return eventDataCopy


        if duration is not None and duration > 0:
            start_time = parser.parse(eventData["timestamp"]).astimezone(tz.UTC)
            end_time = parser.parse(eventData["end_time"]).astimezone(tz.UTC)

            while start_time < end_time:

                next_minutes = start_time.minute + limit_minutes_per_slot - (start_time.minute % limit_minutes_per_slot)
                # Floor math of next_mintutes / 60
                
                next_minutes_carries_int = math.floor(next_minutes / 60)
                next_minutes %= 60

        
                next_tenth_minutes = datetime.datetime(
                    start_time.year, start_time.month, start_time.day,
                    start_time.hour, next_minutes,
                    tzinfo=tz.UTC
                )

                # Add the minute in datetime as delta if the minute carries 

                if(next_minutes_carries_int > 0):
                    minutes_to_add =  datetime.timedelta(hours=next_minutes_carries_int)
                    next_tenth_minutes += minutes_to_add



                current_endtime = min(next_tenth_minutes, end_time)
                eventDataCopy = createEventDataCopy(eventData, start_time.isoformat(), current_endtime.isoformat())
                timeslots_event_data.append(eventDataCopy)

                span_sequence += 1
                start_time = current_endtime

        else: 
            # Create a simple timeslot here

            start_time = eventData["timestamp"]
            # NOTE: Make sure that end_time can be None on the postgresql model.
            # 2023-06-14 10:12:17 It is Nullable in both local and utc, as well as in duration
            end_time = eventData["end_time"] # It will probably be None, so you have to create something on the date_related_population to support those cases

            eventDataCopy = createEventDataCopy(eventData=eventData, start_time=start_time, current_endtime=end_time)
            timeslots_event_data.append(eventDataCopy)

            

            

        if len(timeslots_event_data) > 0:
            # If the timeslot event data is here, it should be able to have the population of the date_related_population here.

            date_formatted_events_data = Utils.date_related_population(timeslots_event_data)

            for timeslot_event_data in date_formatted_events_data:
                timeslot_event_data["event_guid"] = eventData["guid"]
                timeslot = Timeslot.from_dict(timeslot_event_data).to_dict()
                timeslots_res.append(timeslot)
            try:
                print("")
            except Exception as e:
                print("Exception at eventDataIntoTimeSlots:", e)
                print("timeslots_event_data:", timeslots_event_data)
                

        return timeslots_res


class OrganizationalQuerier(ABC):
    def __init__(self):
        pass

    def initialization(self, organization_id, platform_type = None):
        """Prepares the Querier with all the organization data.
        """
        self.organization_id = organization_id
        
    def getCredential(organization_id: str, service: str):
        """Gets organization identification. 

        Args:
            organization_id (str): 
            service (str): gets ervices
        """
        pass

    def getEmployeesDenormalized(organization_id: str):
        """Gets all of the employees data in the organization

        Args:
            organization_id (str): organization string
        """
        

        pass
    def getEmployeeDenormalized(user_id: str):
        """Gets the data of the employee based on th

        Args:
            user_id (str): id of th employee which data we want to denormalize
        """
        pass

    
    def getOrganizationParameters_identity(self):
        """Gets the organization parameters for identity

        Returns:
            dict: {identity: user_profile_json}
        """
        pass
    
    def getOrganizationParameters_salesforce(organization_id: str):
        """Gets the organization parameters for salesforce

        Args:
            organization_id (str): organization id

        Returns:
            dict: organization parameters
        """
        return {}
    
    def getOrganizationParametersByOrganizationID(organization_id: str):
        """Gets the organization parameters by organization id

        Args:
            organization_id (str): organization id

        Returns:
            dict: organization parameters
        """
        return {}
    
    def getOrganizationParameters_connectorguid(organization_name: str):
        """Gets the organization parameters by organization name

        Args:
            organization_name (str): organization name

        Returns:
            dict: organization parameters
        """
        return {}
    
    def getOrganizationParameters(self) -> List[dict]:
        return []
        
    def get_platform_id(connector_guid: str):
        """Gets the platform id from the connector guid

        Args:
            connector_guid (str): connector guid

        Returns:
            str: platform id
        """
        return 1


# Sample profile of an employee, that is just used by default.

sample_profile_user_1 = {
            "organization_guid": 1,
            "user_guid": "ab3c-asd1-100G",
            "user_id": 1,
            "user_team_id": [1, 2],
            "profile_id": [1],
            "user_timezone": "Asia/Tokyo",
            "user_time_slot_split": 6,
            "user_work_hours_start": [9, 9, 9, 9, 9, 0, 0],
            "user_work_days": [0, 1, 2, 3, 4],
            "user_work_hours_end": [17, 17, 17, 17, 17, 0, 0],
            "user_work_settings": {
                "WORK": {
                    0: [{"start": 9, "end": 17}],
                    1: [{"start": 9, "end": 17}],
                    2: [{"start": 9, "end": 17}],
                    3: [{"start": 9, "end": 17}],
                    4: [{"start": 9, "end": 17}],
                },
                "BREAK": {
                    0: [{"start": 12, "end": 13}],
                    1: [{"start": 12, "end": 13}],
                    2: [{"start": 12, "end": 13}],
                    3: [{"start": 12, "end": 13}],
                    4: [{"start": 12, "end": 13}],
                }
            },
            "profile_mapping_instruction": {"instruction1": "value1", "instruction2": "value2"}
    }

sample_profile_user_2 =  {
                "organization_guid": 1,
                "user_id": 2,
                "user_team_id": [1],
                "user_guid": "ab3c-asd1-561a",
                "profile_id": [1, 2],
                "user_timezone": "Asia/Tokyo",
                "user_time_slot_split": 6,
                "user_work_hours_start": [9, 10, 11, 9, 9, 0, 0],
                "user_work_days": [0, 1, 2, 3, 4],
                "user_work_hours_end": [17, 18, 19, 17, 17, 0, 0],
                "user_escape_dates": ["2022-03-01", "2022-09-01"],
                "profile_mapping_instruction": {"instruction5": "value5", "instruction6": "value6"}
            }

class MockOrganizationQuerier(OrganizationalQuerier):
    
    def __init__(self):
        """
        Populates all organizations table information, gets it ready for the utilization at initialization.
        """
        pass

        
    def initialization(self, organization_guid, platform_type = None):
        """Prepares the Querier with all the organization data.
        To be initialized in the adapter.
        platform_type: specifically only fetches for certain platforms only as there is only one platform per staging_guid.
        This parameter is for optimization purposes, but you can select any of them.
        """

        super().initialization(organization_guid, platform_type)
        # TODO Here is just the mock, edit it to publish it.

        # 1. Create a dict of users. {id: user_profile}
        # 2. Create a dict of dict of users. | separated each identity by each platform. 
        
        # {platform_id: {identity: user_id}}

        # Then transform that into the format that we want.

        self.organization_365_formatted = {
            "organization_guid": organization_guid,
            "nelson@o365.devcooks.com": sample_profile_user_1,
            "apolo@o365.devcooks.com": sample_profile_user_1
        }

        self.organization_salesforce_formatted= {
            "organization_guid": organization_guid,
            "nwang@platinumfilings.com": sample_profile_user_1,
            "nwang@ddapfilings.com": sample_profile_user_1,
        }


        self.organization_connectorguid_formatted = {
            "organization_guid": organization_guid,
            "chrome-extension-ddap-1": sample_profile_user_1
        }


        self.organization_param_guid = {"organization_guid": organization_guid, "user_profile": sample_profile_user_1}



    def getOrganizationParameters_365(self) -> dict:
        """Returns in format:

        {
            "organization_guid": "8de4e5d3-49de-4b57-a209-organization",
            "nelson@o365.devcooks.com": sample_profile_user_1,
            "apolo@o365.devcooks.com": sample_profile_user_1
        }

        """
        # What I need get the organization guid, and the data of each employee.
        return self.organization_365_formatted
    


    def getOrganizationParameters_salesforce(self):
        return self.organization_salesforce_formatted
    
    def getOrganizationParamters_identity(self):
        return self.getOrganizationParameters_salesforce()
    
    
    def getOrganizationParameters_connectorguid(self, connector_guid: str):
        """
        Based on the organization parameters, it will return the organization parameters for the connector.
        """
        return {"user_profile": sample_profile_user_1, "organization_guid": connector_guid}

    def getOrganizationParameters(self):
        return [sample_profile_user_1, sample_profile_user_2]

    def get_platform_id(self, connector_guid: str):
        
        adapter_map = {
            "salesforce-connector":  1,
            "chrome-extension-ddap-1": 2,
            'salesforce-testing-connector': 1,
            3: 3
        }

        if connector_guid in adapter_map:
            return adapter_map[connector_guid]

        return 1



class PostgresqlOrganizationQuerier(OrganizationalQuerier):
    """In charge of fetching the organization parameters from
    the postgresql database.

    """

    def __init__(self, credentials = {}):
        """
        Populates the querier credentials for Postgresql. Should be on the following format:
        credentials = {
            'USERNAME': "postgres",
            'PASSWORD': "dDueller123araM=!",
            "HOST": "test-ddanalytics-rds-v2.cpcwi20k2qgg.us-east-1.rds.amazonaws.com",
            "DB": "v1_2"
        }
        """
        self.connection = psycopg2.connect(user=credentials['USERNAME'], password=credentials['PASSWORD'], host=credentials['HOST'], database=credentials['DB'])
        # DictCursor
        self.cursor = self.connection.cursor(cursor_factory=DictCursor)
        

        
    def initialization(self, organization_guid, platform_type = None):
        """Prepares the Querier with all the organization data.
        To be initialized in the adapter.
        platform_type: specifically only fetches for certain platforms only as there is only one platform per staging_guid.
        This parameter is for optimization purposes, but you can select any of them.
        """

        super().initialization(organization_guid, platform_type)
        # TODO Here is just the mock, edit it to publish it.

        # 1. Create a dict of users. {id: user_profile}
        # 2. Create a dict of dict of users. | separated each identity by each platform.
        
        cursor = self.cursor
        connection = self.connection

        # Query all users
        cursor.execute("SELECT * FROM users")
        users_selection = cursor.fetchall()

        # Query all identities
        cursor.execute("SELECT * FROM identity")
        identities_selections = cursor.fetchall()
        
        def profile_mapping(profile_user):
            """Ensures that all corresponding fields are at least there. 

            Args:
                profile_user (dict): the profile of the user fetched from db.

            Returns:
                dict<profile_user>: the profile of the user
            """

            profile_mapped = sample_profile_user_1.copy()
            for key, value in profile_user.items():
                updated_key = f"user_{key}"
                profile_mapped[updated_key] = value
            
            profile_mapped.update(profile_mapped)
            return profile_mapped

        # Query all connectors with an user id where the user id is not null
        cursor.execute("SELECT * FROM connector WHERE user_id IS NOT NULL")
        connectors_selections = cursor.fetchall()


        identities = { identity["identity"]:identity["user_id"] for identity in identities_selections }
        connectors = { connector["guid"]:connector["user_id"] for connector in connectors_selections }
        users_as_list = [profile_mapping(user) for user in users_selection]
        
        

        users = {}
        for user in users_selection:
            user_id = user["id"]
            users[user_id] = profile_mapping(user)

        identities_user = { identity: users[user_id] for identity, user_id in identities.items() if user_id in users }
        connectors_user = { connector: users[user_id] for connector, user_id in connectors.items() if user_id in users }

        print("users dict", users)
        print("users as list", users_as_list)
        print("identity dict", identities)
        print("connectors dict", connectors)

        # print("identity user dict", identities_user)
        print("connectors user dict", connectors_user)

        """
        timezone: getting the user timezone.


        {
            "organization_guid": 1,
            "user_guid": "ab3c-asd1-100G",
            "user_id": 1,
            "user_team_id": [1, 2],
            "profile_id": [1],
            "user_timezone": "US/Eastern",
            "user_time_slot_split": 6,
            "user_work_hours_start": [9, 10, 11, 9, 9, 0, 0],
            "user_work_days": [0, 1, 2, 3, 4],
            "user_work_hours_end": [17, 18, 19, 17, 17, 0, 0],
            "profile_mapping_instruction": {"instruction1": "value1", "instruction2": "value2"}
        }
        """
        # In which you can have the id, and the guid, working in a way where you just map them with the correct user, id, it doesnt matter, the 
        

        self.organization_identity_formatted = identities_user
        self.organization_connectorguid_formatted = connectors_user
        self.users_as_list = users_as_list
        self.organization_guid = organization_guid

        # self.organization_param_guid = {"organization_guid": organization_guid, 
        #                                 "user_profile": sample_profile_user_1}


    def __del__(self):
        # Code to be executed when the object is destroyed
        self.connection.close()
        self.cursor.close()
    
    
    def getOrganizationParameters_identity(self):
        return self.organization_identity_formatted
    
    
    
    def getOrganizationParameters_connectorguid(self, connector_guid: str):
        """
        Based on the organization parameters, it will return the organization parameters for the connector.
        """
        print('PostgresqlOrganization Querier Called with connector_guid', connector_guid)
        user_profile = self.organization_connectorguid_formatted.get(connector_guid, None)

        return {"user_profile": user_profile, "organization_guid": self.organization_guid}

    def getOrganizationParameters(self):
        return self.users_as_list


    def get_platform_id(self, connector_guid: str):
        """Gets the platform id from the connector guid.

        Args:
            connector_guid (str): Connector guid

        Returns:
            int: platform_id
        """
        
        # Get the connector
        # Try and return the connector_id
        cursor = self.cursor
        query = "SELECT * FROM connector WHERE guid = '" + connector_guid + "'"
        cursor.execute(query)
        connector = cursor.fetchone()
        # If the connector is not found, return 2
        if connector is None:
            print("Connector not found")
            print("Query used: ", query)
            return 2


        return connector.get("platform_id", None)



