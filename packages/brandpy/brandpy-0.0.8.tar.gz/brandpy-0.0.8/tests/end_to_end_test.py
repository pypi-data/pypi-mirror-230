import datetime
import pandas as pd
from BrandPy.src import brandpy

TOKEN_FILE_PATH = "../../secrets/acjBWToken.json"
QUERY_NAME = "UkrianeWar_nofilters"

bw_auth_config = brandpy.BWAuthConfig(TOKEN_FILE_PATH)
bw_api_caller = brandpy.BWAPICaller(bw_auth_config)
bw_api_helper = brandpy.BWAPIHelper(bw_api_caller)

all_projects = bw_api_helper.get_projects()
print(type(all_projects))
print(all_projects)

found_proj_queries = bw_api_helper.find_query_id(QUERY_NAME)
print(f"Found {len(found_proj_queries)} matches.")
df = pd.DataFrame(found_proj_queries, columns=["ProjectID", "QueryID", "Project Name"])[["Project Name", "ProjectID", "QueryID"]]
df.index.name = "Index"
print(df)

if len(found_proj_queries) == 1:
    PROJECT_ID = found_proj_queries[0][0]
    QUERY_ID = found_proj_queries[0][1]
    PROJECT_NAME = found_proj_queries[0][2]
else:
    print("Picking 1st one")
    PROJECT_ID = found_proj_queries[0][0]
    QUERY_ID = found_proj_queries[0][1]
    PROJECT_NAME = found_proj_queries[0][2]

print(f"QueryID of '{QUERY_NAME}' is '{QUERY_ID}' in the project: '{PROJECT_NAME}' (ProjectID : '{PROJECT_ID}')")

start_time = datetime.datetime(2022, 2, 23,  0,  0,  0, tzinfo=datetime.timezone.utc)
end_time   = datetime.datetime(2022, 2, 23,  1,  0,  0, tzinfo=datetime.timezone.utc)

tm = bw_api_helper.total_mentions(PROJECT_ID, QUERY_ID, bw_api_helper.datetime_to_str(start_time), bw_api_helper.datetime_to_str(end_time))
print(tm)

am = bw_api_helper.retrieve_all_mentions(PROJECT_ID, QUERY_ID, bw_api_helper.datetime_to_str(start_time), bw_api_helper.datetime_to_str(end_time))
print(f"Mention results list contains {len(am)} pages.")

all_results = []
for i in range(len(am)):
    all_results.extend(am[i]['results'])

datadf = pd.DataFrame.from_records(all_results)
print(datadf)
