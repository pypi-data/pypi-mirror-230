#
import json
import uuid
import random
import string
import datetime


#
import pytz
import pandas
import urllib3
from sqlalchemy import text, table, column
from sqlalchemy.dialects import postgresql


#


#
class LocalTimer:
    def __init__(self, conn_log, log_table):
        self.conn_log = conn_log
        self.log_table = log_table

    @staticmethod
    def new_call(group):
        code = str(uuid.uuid5(namespace=uuid.NAMESPACE_OID, name=group))
        return code

    def log_start(self, call_id_reporter, group, method):
        query = table('timings_reported',
                      column('service_name'),
                      column('internal'),
                      column('call_id_reporter'), column('group'), column('method'),
                      column('status'), column('timestamp')).insert() \
            .values({'service_name': 'host',
                     'internal': 'external',
                     'call_id_reporter': str(call_id_reporter), 'group': group, 'method': method,
                     'status': 'start', 'timestamp': datetime.datetime.utcnow().replace(tzinfo=pytz.utc).isoformat()})
        cursor = self.conn_log.connection.cursor()
        query.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": False})
        cursor.mogrify(str(query), query.params)
        self.conn_log.execute(query)

    def log_end(self, call_id_reporter, group, method):
        query = table('timings_reported',
                      column('service_name'),
                      column('internal'),
                      column('call_id_reporter'), column('group'), column('method'),
                      column('status'), column('timestamp')).insert() \
            .values({'service_name': 'host',
                     'internal': 'external',
                     'call_id_reporter': str(call_id_reporter), 'group': group, 'method': method,
                     'status': 'end', 'timestamp': datetime.datetime.utcnow().replace(tzinfo=pytz.utc).isoformat()})
        cursor = self.conn_log.connection.cursor()
        query.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": False})
        cursor.mogrify(str(query), query.params)
        self.conn_log.execute(query)


class Exceptor:
    def __init__(self, service_name, service_pw, api):
        self.service_name = service_name
        self.service_pw = service_pw
        self.api = api

    def send_report(self, code_id, group, data):
        http = urllib3.PoolManager()
        method = "exceptor_send_report"

        query = {
            "service_name": self.service_name,
            "service_pw": self.service_pw,
            "code_id": str(code_id),
            "group": group,
            "timestamp": datetime.datetime.utcnow().replace(tzinfo=pytz.utc).isoformat(),
            "data": data,
        }

        encoded_body = json.dumps(query)

        r = http.request('POST', '{0}/{1}'.format(self.api, method),
                         headers={'Content-Type': 'application/json'},
                         body=encoded_body
                         )
        result = r.data


class Timer:
    def __init__(self, service_name, service_pw, api):
        self.service_name = service_name
        self.service_pw = service_pw
        self.api = api

    @staticmethod
    def new_call(group):
        code = str(uuid.uuid5(namespace=uuid.NAMESPACE_OID, name=group))
        return code

    def log_start(self, call_id_reporter, group, method_used):
        http = urllib3.PoolManager()
        method = "timer_send_timing"

        query = {
            "service_name": self.service_name,
            "service_pw": self.service_pw,
            "call_id_reporter": call_id_reporter,
            "group": group,
            "method": method_used,
            "status": 'start',
            "timestamp": datetime.datetime.utcnow().replace(tzinfo=pytz.utc).isoformat(),
        }

        encoded_body = json.dumps(query)

        r = http.request('POST', '{0}/{1}'.format(self.api, method),
                         headers={'Content-Type': 'application/json'},
                         body=encoded_body
                         )
        result = r.data

    def log_end(self, call_id_reporter, group, method_used):
        http = urllib3.PoolManager()
        method = "timer_send_timing"

        query = {
            "service_name": self.service_name,
            "service_pw": self.service_pw,
            "call_id_reporter": call_id_reporter,
            "group": group,
            "method": method_used,
            "status": 'end',
            "timestamp": datetime.datetime.utcnow().replace(tzinfo=pytz.utc).isoformat(),
        }

        encoded_body = json.dumps(query)

        r = http.request('POST', '{0}/{1}'.format(self.api, method),
                         headers={'Content-Type': 'application/json'},
                         body=encoded_body
                         )
        result = r.data


class TimerFuture:
    def __init__(self, service_name, service_pw, api):
        self.service_name = service_name
        self.service_pw = service_pw
        self.api = api
        self.local = './{0}.csv'.format(''.join(random.choices(string.ascii_uppercase + string.digits, k=10)))
        pandas.DataFrame(columns=['call_id', 'group', 'method', 'status', 'timestamp']).to_csv(self.local, index=False)
        self.buff = open(self.local, 'a')

    def log_start(self, call_id, group, method):
        appendix = pandas.DataFrame(data={'call_id': [call_id],
                                          'group': [group],
                                          'method': [method],
                                          'status': ['start'],
                                          'timestamp': [
                                              datetime.datetime.utcnow().replace(tzinfo=pytz.utc).isoformat()]})
        appendix.to_csv(self.buff, header=False, index=False)

    def log_end(self, call_id, group, method):
        appendix = pandas.DataFrame(data={'call_id': [call_id],
                                          'group': [group],
                                          'method': [method],
                                          'status': ['end'],
                                          'timestamp': [
                                              datetime.datetime.utcnow().replace(tzinfo=pytz.utc).isoformat()]})
        appendix.to_csv(self.buff, header=False, index=False)

    def switch_logs(self):
        old_buff = self.buff
        self.local = './{0}.csv'.format(''.join(random.choices(string.ascii_uppercase + string.digits, k=10)))
        pandas.DataFrame(columns=['call_id', 'group', 'method', 'status', 'timestamp']).to_csv(self.local, index=False)
        self.buff = open(self.local, 'a')
        old_logs = pandas.read_csv(old_buff)
        self.send_log_table(old_logs)

    def send_log_table(self, log_table):
        http = urllib3.PoolManager()
        method = "timer_send_log_table"

        query = {
            "service_name": self.service_name,
            "service_pw": self.service_pw,
            "data": log_table.to_dict(),
        }

        encoded_body = json.dumps(query)

        r = http.request('POST', '{0}/{1}'.format(self.api, method),
                         headers={'Content-Type': 'application/json'},
                         body=encoded_body
                         )
        result = r.data
