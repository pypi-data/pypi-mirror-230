import pandas as pd

import brandpy


class BwAccessor:
    def __init__(self, in_token_file, in_queue_file):
        self.auth = None
        self.caller = None
        self.helper = None
        self.user = None
        self.connect(in_token_file, in_queue_file)

    def connect(self, in_token_file, in_queue_file):
        self.auth = brandpy.BWAuthConfig(in_token_file, in_queue_file)
        self.caller = brandpy.BWAPICaller(self.auth)
        self.helper = brandpy.BWAPIHelper(self.caller)
        self.user = self.auth.email.split("@")[0]

    def load_projects(self):
        data = self.helper.get_projects()
        return {proj["name"]: proj["id"] for proj in data["results"]}

    def load_queries(self, in_project_id):
        data = self.helper.get_queries(in_project_id)
        return {query["name"]: query["id"] for query in data["results"]}

    def download_data(self, in_project_id, in_query_id, in_start_datetime_tz, in_end_datetime_tz):
        data = self.helper.retrieve_all_mentions(in_project_id, in_query_id, in_start_datetime_tz, in_end_datetime_tz)
        all_results = []
        for i in range(len(data)):
            all_results.extend(data[i]['results'])
        data = pd.DataFrame.from_records(all_results)
        return data
