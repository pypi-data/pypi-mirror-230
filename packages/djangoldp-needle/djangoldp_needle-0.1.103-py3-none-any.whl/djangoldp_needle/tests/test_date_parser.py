import requests_mock

from rest_framework.test import APITestCase
from ..request_parser.parsers.jsonld import JSONLD


@requests_mock.Mocker(real_http=True)
class TestDateParser(APITestCase):

    def test_date_only_parser(self, m):
        jsonld_parser = JSONLD()
        date_strings = ["2022-12-25", "2022/12/25", "20221225", "25/12/2022", "12/25/2022"]

        for date_string in date_strings:
            print(date_string)
            date = jsonld_parser.try_strptimeAll(date_string)
            print("date.year", date.year)
            self.assertEqual(date.year, 2022)
            print("date.month", date.month)
            self.assertEqual(date.month, 12)
            print("date.day", date.day)
            self.assertEqual(date.day, 25)

    def test_date_time_parser(self, m):
        jsonld_parser = JSONLD()
        date_strings = [
            "2022-12-25T01:02:03+0000",
            "2022-12-25T01:02:03+00:00",
            "2022-12-25T01:02:03Z",
            "2022-12-25T01:02:03",
            "2022/12/25T01:02:03",
            "25/12/2022T01:02:03",
            "2022-12-25 01:02:03",
            "2022/12/25 01:02:03",
            "25/12/2022 01:02:03",
            "12/25/2022 01:02:03",
            "2022-12-25T01:02:03.1234",
            "2022/12/25T01:02:03.1234",
            "25/12/2022T01:02:03.1234",
            "2022-12-25 01:02:03.1234",
            "2022/12/25 01:02:03.1234",
            "25/12/2022 01:02:03.1234",
            "12/25/2022 01:02:03.1234",
            "12/25/2022T01:02:03.1234",
            "1671930123000",
            "1671930123",
            "25 dec. 2022 01:02:03",
            "Thu, 25 Dec 2022 01:02:03 GMT"

        ]

        for date_string in date_strings:
            print(date_string)
            date = jsonld_parser.try_strptimeAll(date_string)
            print("date.year", date.year)
            self.assertEqual(date.year, 2022)
            print("date.month", date.month)
            self.assertEqual(date.month, 12)
            print("date.day", date.day)
            self.assertEqual(date.day, 25)
            print("date.hour", date.hour)
            self.assertEqual(date.hour, 1)
            print("date.minute", date.minute)
            self.assertEqual(date.minute, 2)
            print("date.second", date.second)
            self.assertEqual(date.second, 3)
