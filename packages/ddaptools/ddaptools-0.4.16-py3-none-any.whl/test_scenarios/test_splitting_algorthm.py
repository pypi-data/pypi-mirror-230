"""
2023-06-09 15:42:41 
Testing the splitting algorithm
"""

import unittest
from ddaptools.aws_classes.class_helpers import Utils
from ddaptools.dda_models import *
from ddaptools.aws_classes.class_helpers import *


class EventDataIntoTimeSlotsTests(unittest.TestCase):

    def test_eventDataIntoTimeSlots(self):
        eventData = {
            "guid": "460bcde5-adce-42e1-85de-1411a69e280b",
            "user_id": 1,
            "application": "CHROME",
            "app": "mazzzystar.github.io",
            "operation": "download",
            "event_guid": "0adeb6d2-c889-4592-0b46-e43e887e4d71",
            "platform_id": 2,
            "organization_id": 1,
            "user_timezone": "US/Eastern",
            "timestamp": "2023-05-11T16:03:31.434Z",
            "end_time": "2023-05-11T16:13:31.427Z",
            "timestamp_local": "2023-05-11T12:03:31.434000-04:00",
            "end_time_local": "2023-05-11T12:13:31.427000-04:00",
            "duration": 600000,
            "title": "The Leverage of LLMs for Individuals | TL;DR",
            "url": "https://mazzzystar.github.io/images/2023-05-10/superCLUE.jpg",
            "site": "mazzzystar.github.io",
            "url_domain": "mazzzystar.github.io",
            "file_count": 0,
            "action_type": "PASSIVE",
            "staging_guid": "0adeb6d2-c889-4592-0b46-e43e887e4d71",
            "staging_detail_guid": "0adeb6d2-c889-4592-0b46-staging-details-guid",
            "mouse_clicks": 13,
            "keystrokes": 10,
            "size": 0
        }



        nondurationeventData = {
            "guid": "460bcde5-adce-42e1-85de-1411a69e280b",
            "user_id": 1,
            "application": "CHROME",
            "app": "mazzzystar.github.io",
            "operation": "download",
            "event_guid": "0adeb6d2-c889-4592-0b46-e43e887e4d71",
            "platform_id": 2,
            "organization_id": 1,
            "user_timezone": "US/Eastern",
            "timestamp": "2023-05-11T16:03:31.434Z",
            "end_time": None,
            "timestamp_local": "2023-05-11T12:03:31.434000-04:00",
            "end_time_local": None,
            "duration": None,
            "title": "The Leverage of LLMs for Individuals | TL;DR",
            "url": "https://mazzzystar.github.io/images/2023-05-10/superCLUE.jpg",
            "site": "mazzzystar.github.io",
            "url_domain": "mazzzystar.github.io",
            "file_count": 0,
            "action_type": "PASSIVE",
            "staging_guid": "0adeb6d2-c889-4592-0b46-e43e887e4d71",
            "staging_detail_guid": "0adeb6d2-c889-4592-0b46-staging-details-guid",
            "mouse_clicks": 13,
            "keystrokes": 10,
            "size": 0
        }
        eventData = nondurationeventData
        
        expected_timeslots = [
            {
                'event_guid': '460bcde5-adce-42e1-85de-1411a69e280b', 
                'timeslot': 72, 
                'timeslot_local': 6, 
                'hour': 16, 
                'minute': 3, 
                'day': 11, 
                'month': 5, 
                'year': 2023, 
                'week': 19, 
                'weekday': 3, 
                'hour_local': 12, 
                'minute_local': 3, 
                'day_local': 11, 
                'month_local': 5, 
                'year_local': 2023, 
                'week_local': 19, 
                'weekday_local': 3, 
                'mouse_clicks': 13, 
                'staging_guid': '0adeb6d2-c889-4592-0b46-e43e887e4d71', 
                'keystrokes': 10
            }, 
            {
                'event_guid': '460bcde5-adce-42e1-85de-1411a69e280b', 
                'timeslot': 73, 
                'timeslot_local': 7, 
                'hour': 16, 
                'minute': 10, 
                'day': 11, 
                'month': 5, 
                'year': 2023, 
                'week': 19, 
                'weekday': 3, 
                'hour_local': 12, 
                'minute_local': 10, 
                'day_local': 11, 
                'month_local': 5, 
                'year_local': 2023, 
                'week_local': 19, 
                'weekday_local': 3, 
                'mouse_clicks': 13, 
                'staging_guid': '0adeb6d2-c889-4592-0b46-e43e887e4d71', 
                'keystrokes': 10
            }
        ]

        # Call the method to get the actual timeslots
        actual_timeslots = Utils.eventDataIntoTimeSlots(eventData, limit_minutes_per_slot=10)

        print(actual_timeslots)
        # Assert that the actual timeslots match the expected timeslots
        # What's important in this case is to have them splitted as the following:

        # 1. 2023-05-11T16:03
        # 2. 2023-05-11T16:10

        # Which has a cutoff there

        # self.assertEqual(actual_timeslots, expected_timeslots)

    def test_events_joining_same_span_guid(self):
        """Tests whether the same spanguid events are able to join in the same event.

        """
        
        credentials = {
            'USERNAME': "postgres",
            'PASSWORD': "dDueller123araM=!",
            "HOST": "test-ddanalytics-rds-v2.cpcwi20k2qgg.us-east-1.rds.amazonaws.com",
            "DB": "v1_2"
        }

        settings = {
            "GET_TABLENAME": "staging_events",
            "TABLENAME_EVENTS": "event",
            "COLUMN_NAMES_EVENTS": Event.get_attribute_keys(),
            "TABLENAME_TIMESLOTS": "timeslot",
            "COLUMN_NAMES_TIMESLOTS": Timeslot.get_attribute_keys()
        }
        publishingDBProvider = PostgreSQLProviderTimeSlotPlusEventsPublishing(credentials=credentials, settings=settings)
        

        eventDatas = [{
            "guid": "460bcde5-adce-42e1-85de-1411a69e280b",
            "user_id": 1,
            "application": "CHROME",
            "app": "mazzzystar.github.io",
            "operation": "download",
            "event_guid": "0adeb6d2-c889-4592-0b46-e43e887e4d71",
            "platform_id": 2,
            "organization_id": 1,
            "user_timezone": "US/Eastern",
            "timestamp": "2023-05-11T16:03:31.434Z",
            "end_time": "2023-05-11T16:13:31.427Z",
            "timestamp_local": "2023-05-11T12:03:31.434000-04:00",
            "end_time_local": "2023-05-11T12:13:31.427000-04:00",
            "duration": 600000,
            "title": "Part I",
            "url": "https://mazzzystar.github.io/images/2023-05-10/superCLUE.jpg",
            "site": "mazzzystar.github.io",
            "url_domain": "mazzzystar.github.io",
            "span_guid": "460bcde5-adce-42e1-85de-1411a69e280b",
            "span_sequence": 0,
            "file_count": 0,
            "action_type": "PASSIVE",
            "staging_guid": "0adeb6d2-c889-4592-0b46-e43e887e4d71",
            "staging_detail_guid": "0adeb6d2-c889-4592-0b46-staging-details-guid",
            "mouse_clicks": 13,
            "keystrokes": 10,
            "size": 0
        },{
            "guid": "460bcde5-adce-42e1-85de-1411a69e280b",
            "user_id": 1,
            "application": "CHROME",
            "app": "mazzzystar.github.io",
            "operation": "download",
            "event_guid": "0adeb6d2-c889-4592-0b46-e43e887e4d71",
            "platform_id": 2,
            "organization_id": 1,
            "user_timezone": "US/Eastern",
            "span_guid": "460bcde5-adce-42e1-85de-1411a69e280b",
            "span_sequence": 1,
            "timestamp": "2023-05-11T16:03:31.434Z",
            "end_time": "2023-05-11T16:13:31.427Z",
            "timestamp_local": "2023-05-11T12:03:31.434000-04:00",
            "end_time_local": "2023-05-11T12:13:31.427000-04:00",
            "duration": 600000,
            "title": "The Leverage of LLMs for Individuals | TL;DR",
            "url": "https://mazzzystar.github.io/images/2023-05-10/superCLUE.jpg",
            "site": "mazzzystar.github.io",
            "url_domain": "mazzzystar.github.io",
            "file_count": 0,
            "action_type": "PASSIVE",
            "staging_guid": "0adeb6d2-c889-4592-0b46-e43e887e4d71",
            "staging_detail_guid": "0adeb6d2-c889-4592-0b46-staging-details-guid",
            "mouse_clicks": 13,
            "keystrokes": 10,
            "size": 0
        }]

        column_names_events = settings["COLUMN_NAMES_EVENTS"]
        tablename_events = settings["TABLENAME_EVENTS"]

        # now you have to test if creating into both the timeslots will work.
        # actual_timeslots = Utils.eventData
        events = []
        for event in eventDatas:
            new_event = Event.from_dict(event)
            event.append(new_event)

        # The logic occurs at insertion (since it relies on Postgresql API)
        # Thus I am in need of the helpers lib.
        postgresqlProvider  = PostgreSQLProviderTimeSlotPlusEventsPublishing(credentials=credentials, settings=settings)
        self.publish_to(events["events"], column_names_events, tablename_events, update_span_guid=True)
        


