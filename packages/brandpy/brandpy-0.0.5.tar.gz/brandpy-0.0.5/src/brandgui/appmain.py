import os.path
import re
import PySimpleGUI as sg

from BrandPy.src import brandpy

from bw_accessor import BwAccessor
from cache_values import CacheValues
from formatted_date_time import FormattedDateTime

# Filled by data
PROJECT_NAME_TO_ID = {}
QUERY_NAME_TO_ID = {}

SYSTEM_STATE = 0

BW_ACCESSOR = None

TOKEN_FILE_PATH = None
QUERY_CACHE_FILE_PATH = None
PROJECT_ID = None
PROJECT_NAME = None
QUERY_ID = None
QUERY_NAME = None
START_DATETIME = None
END_DATETIME = None
OUTPUT_FOLDER = None
OUTPUT_FILE_NAME = None

DEF_FONT = ("Courier", 10)

sg.theme('DarkAmber')  # Add a touch of color


def create_cache_file_path(in_token_file_path):
    return os.path.join(os.path.dirname(in_token_file_path),
                        "{}.queuetimes.txt".format(os.path.basename(in_token_file_path).split(".")[0]))


def new_token_window():
    status_msg = ""
    token_file_path = ""
    cache_file_path = ""
    pressed_ok = False

    def inputs_validated(in_email, in_password, in_token_file_path):
        nonlocal status_msg
        if type(in_email) is str and type(in_password) is str and type(in_token_file_path) is str:
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
            if re.fullmatch(regex, in_email):
                if os.path.exists(os.path.dirname(in_token_file_path)):
                    status_msg = "Sending request..."
                    return True
                else:
                    status_msg = "Please specify a valid absolute path to save token file."
                    return False
            else:
                status_msg = "Please enter a valid email address."
                return False
        status_msg = "Please enter valid a email and a password."
        return False

    layout = [
        [sg.Text("Email:", font=DEF_FONT, size=(15, 2)),
         sg.InputText(key="IT_Email", size=(20, 1), enable_events=True, font=DEF_FONT)],
        [sg.Text("Password:", font=DEF_FONT, size=(15, 2)),
         sg.InputText(key="IT_Password", password_char="x", size=(20, 1), enable_events=True, font=DEF_FONT)],
        [sg.InputText(key="IT_TokenFile", size=(40, 3), font=DEF_FONT, enable_events=True,
                      default_text="Please pick a Token File Path..."),
         sg.FileSaveAs(target="IT_TokenFile", font=DEF_FONT,
                       file_types=[("JSON files", "*.json")])],
        [sg.Text(key="IT_CacheFile", text="", font=DEF_FONT)],
        [sg.Text(" " * 40), sg.Button(key="B_Ok", button_text='Ok', font=DEF_FONT), sg.Text(" " * 30),
         sg.Button(key="B_Cancel", button_text='Cancel', font=DEF_FONT, button_color="red")],
        [sg.Text(key="T_Status", text=status_msg)]
    ]
    window = sg.Window("Request New Token", layout, modal=True)

    while True:
        event, values = window.read()
        # print("EVENT: ", event, " \t VALUES: ", values)
        if event == sg.WIN_CLOSED or event == 'B_Cancel':  # if user closes window or clicks cancel
            print("At exit: ", values)
            break
        if event == "IT_TokenFile":
            token_file_path = values["IT_TokenFile"]
            cache_file_path = create_cache_file_path(token_file_path)
            window["IT_CacheFile"].update(cache_file_path)
        if event == "B_Ok":
            if inputs_validated(values["IT_Email"], values["IT_Password"], values["IT_TokenFile"]):
                try:
                    resp = brandpy.BWAuthConfig.request_new_token(values["IT_Email"], values["IT_Password"])
                    brandpy.BWAuthConfig.save_token_data_to_file(values["IT_Email"], token_file_path, cache_file_path,
                                                                 resp)
                except Exception as e:
                    sg.popup_error(f"ARGS:{type(e)} ERROR: {str(e)}")
                else:
                    sg.popup_ok(f"Request Successful!")
                    pressed_ok = True
                    break
            else:
                sg.popup_error(status_msg)
        window["T_Status"].update(status_msg)
    window.close()
    return token_file_path, cache_file_path, pressed_ok


def main():
    global SYSTEM_STATE
    global BW_ACCESSOR
    global PROJECT_NAME_TO_ID
    global QUERY_NAME_TO_ID
    global TOKEN_FILE_PATH
    global QUERY_CACHE_FILE_PATH
    global PROJECT_ID
    global PROJECT_NAME
    global QUERY_ID
    global QUERY_NAME
    global START_DATETIME
    global END_DATETIME
    global OUTPUT_FOLDER
    global OUTPUT_FILE_NAME

    all_projects = list(PROJECT_NAME_TO_ID.keys())
    all_projects.sort()
    project_queries = list(QUERY_NAME_TO_ID.keys())
    project_queries.sort()

    cached_values = CacheValues("gui_cache_data.json")

    layout = [
        [sg.Text("(1)Token file:", font=DEF_FONT, size=(15, 2)),
         sg.Checkbox(key="C_NoToken", text="-\"I don't have a token file\" ", default=False, enable_events=True,
                     tooltip="Check this box if you don't have a token file.", font=DEF_FONT),
         sg.Button(key="B_RequestToken", button_text="Get New Token", visible=False, font=DEF_FONT)],

        [sg.InputText(key="IT_TokenFile", size=(60, 3), font=DEF_FONT, enable_events=True),
         sg.FileBrowse(target="IT_TokenFile", font=DEF_FONT,
                       file_types=[("JSON files", "*.json"),
                                   ("All files", "*")])],
        [sg.Text(key="T_CacheFile", text="", size=(70, 1), font=DEF_FONT)],
        [sg.HorizontalSeparator()],

        [sg.Text("(2)Select project:", font=DEF_FONT), sg.Text(" " * 30),
         sg.Text("(3)Select query:", font=DEF_FONT)],
        [sg.Button(k="B_LoadProjects", button_text="Load all projects", font=DEF_FONT), sg.Text(" " * 30),
         sg.Button(k="B_LoadQueries", button_text="Load Queries from the Project", font=DEF_FONT)],

        [sg.Text("Filter >", font=DEF_FONT), sg.Input(key="I_ProjectFilter", enable_events=True, size=(20, 5), font=DEF_FONT),
         sg.Text("  Filter >", font=DEF_FONT), sg.Input(key="I_QueryFilter", enable_events=True, size=(20, 5), font=DEF_FONT)],

        [sg.Listbox(key="LB_Projects", values=all_projects, enable_events=True, size=(30, 10), font=DEF_FONT),
         sg.Listbox(key="LB_Queries", values=project_queries, enable_events=True, size=(30, 10), font=DEF_FONT)],

        [sg.HorizontalSeparator()],

        [sg.Text("(4)Select Start Date and Time             (5)Select End Date and Time", font=DEF_FONT)],
        [sg.Text("Start Datetime                UTC-Timezone           End Datetime", font=DEF_FONT)],

        [sg.InputText(key="I_StartDate", size=(20, 1), enable_events=True, font=DEF_FONT),
         sg.CalendarButton(key="CB_StartDate", button_text='Date', target='I_StartDate', format='%Y_%m_%d',
                           close_when_date_chosen=True, font=DEF_FONT),
         sg.Text(" " * 30),
         sg.InputText(key="I_EndDate", size=(20, 1), enable_events=True, font=DEF_FONT),
         sg.CalendarButton(key="CB_StartDate", button_text='Date', target='I_EndDate', format='%Y_%m_%d',
                           close_when_date_chosen=True, font=DEF_FONT)
         ],

        [sg.Slider(k="S_StartHours", range=(0, 23), default_value=0, resolution=1, orientation='horizontal',
                   size=(20, 20), tooltip="Hours of Start Datetime", enable_events=True, font=DEF_FONT),
         sg.Text("            Hours            ", font=DEF_FONT),
         sg.Slider(k="S_EndHours", range=(0, 23), default_value=23, resolution=1, orientation='horizontal',
                   size=(20, 20), tooltip="Hours of End Datetime", enable_events=True, font=DEF_FONT)],

        [sg.Slider(k="S_StartMinutes", range=(0, 59), default_value=0, resolution=1, orientation='horizontal',
                   size=(20, 20), tooltip="Minutes of Start Datetime", enable_events=True, font=DEF_FONT),
         sg.Text("           Minutes           ", font=DEF_FONT),
         sg.Slider(k="S_EndMinutes", range=(0, 59), default_value=59, resolution=1, orientation='horizontal',
                   size=(20, 20), tooltip="Minutes of End Datetime", enable_events=True, font=DEF_FONT)],

        [sg.Slider(k="S_StartSeconds", range=(0, 59), default_value=0, resolution=1, orientation='horizontal',
                   size=(20, 20), tooltip="Seconds of Start Datetime", enable_events=True, font=DEF_FONT),
         sg.Text("           Seconds           ", font=DEF_FONT),
         sg.Slider(k="S_EndSeconds", range=(0, 59), default_value=59, resolution=1, orientation='horizontal',
                   size=(20, 20), tooltip="Seconds of End Datetime", enable_events=True, font=DEF_FONT)],

        [sg.Text(key="T_StartDateTime", text="", font=DEF_FONT), sg.Text("     ", font=DEF_FONT),
         sg.Text(key="T_EndDateTime", text="", font=DEF_FONT)],

        [sg.HorizontalSeparator()],

        [sg.InputText(key="IT_OutputFolder", enable_events=True, size=(60, 1), font=DEF_FONT),
         sg.FolderBrowse(target="IT_OutputFolder", button_text="(6)Output Folder", font=DEF_FONT)],
        [sg.Button(key="B_Download", button_text='(7)Download', font=DEF_FONT),
         sg.Text(key="T_OutputFile", text="", expand_x=False, size=(50, 3), font=DEF_FONT),
         sg.Button(key="B_Exit", button_text='(8)Exit', font=DEF_FONT, button_color="red")],

        [sg.HorizontalSeparator()],

        [sg.Text(key="T_Status")]
    ]

    column_layout = [[sg.Column(layout, scrollable=True, expand_x=True, expand_y=True, vertical_scroll_only=True,
                                size_subsample_width=1, size_subsample_height=1)]]

    time_handlers = {"I_StartDate", "I_EndDate", "S_StartHours", "S_EndHours", "S_StartMinutes", "S_EndMinutes",
                     "S_StartSeconds", "S_EndSeconds"}

    # Create the Window
    window = sg.Window("Chathura's Brandwatch Data Downloader", column_layout, finalize=True, resizable=True)
    for k in cached_values.values:
        window[k].update(cached_values.values[k])
        if k == "T_CacheFile":
            QUERY_CACHE_FILE_PATH = cached_values.values[k]
        if k == "IT_TokenFile":
            TOKEN_FILE_PATH = cached_values.values[k]

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        # print("EVENT: ", event, " \t VALUES: ", values)
        if event == sg.WIN_CLOSED or event == 'B_Exit':  # if user closes window or clicks cancel
            print("At exit: ", values)
            if event != sg.WIN_CLOSED:
                values_and_texts = {"T_CacheFile": window["T_CacheFile"].DisplayText}
                values_and_texts.update(values)
                cached_values.update_values(values_and_texts)
            break
        if event == "IT_TokenFile":
            TOKEN_FILE_PATH = values["IT_TokenFile"]
            QUERY_CACHE_FILE_PATH = create_cache_file_path(values["IT_TokenFile"])
            window["T_CacheFile"].update(QUERY_CACHE_FILE_PATH)
        if event == "B_LoadProjects":
            if BW_ACCESSOR is None:
                print("Token file: ", TOKEN_FILE_PATH)
                print("Cache file: ", QUERY_CACHE_FILE_PATH)
                BW_ACCESSOR = BwAccessor(TOKEN_FILE_PATH, QUERY_CACHE_FILE_PATH)
            PROJECT_NAME_TO_ID = BW_ACCESSOR.load_projects()
            all_projects = list(PROJECT_NAME_TO_ID.keys())
            all_projects.sort()
            window["LB_Projects"].update(all_projects)
        if event == "B_LoadQueries":
            if BW_ACCESSOR is None:
                sg.popup_error("Load the projects first!")
            else:
                if PROJECT_ID is None:
                    sg.popup_error("Select a project first!")
                QUERY_NAME_TO_ID = BW_ACCESSOR.load_queries(PROJECT_ID)
                project_queries = list(QUERY_NAME_TO_ID.keys())
                project_queries.sort()
                window["LB_Queries"].update(project_queries)
        if event == "I_QueryFilter":
            print("qf: ", values["I_QueryFilter"])
            qfilter = values["I_QueryFilter"]
            if qfilter != "":
                filtered_queries = [pq for pq in project_queries if re.search(qfilter, pq, re.IGNORECASE)]
            else:
                filtered_queries = project_queries
            window["LB_Queries"].update(filtered_queries)
        if event == "LB_Projects":
            PROJECT_NAME = values["LB_Projects"][0] if len(values["LB_Projects"]) > 0 else None
            PROJECT_ID = PROJECT_NAME_TO_ID[PROJECT_NAME] if PROJECT_NAME is not None else None
            window["T_Status"].update(
                "Project: {} Query: {} Datetime Range: {} to {}".format(PROJECT_ID, QUERY_ID, START_DATETIME.get_regular() if START_DATETIME is not None else None,
                                                                        END_DATETIME.get_regular() if END_DATETIME is not None else None))
        if event == "LB_Queries":
            QUERY_NAME = values["LB_Queries"][0] if len(values["LB_Queries"]) > 0 else None
            QUERY_ID = QUERY_NAME_TO_ID[QUERY_NAME] if QUERY_NAME is not None else None
            window["T_Status"].update(
                "Project: {} Query: {} Datetime Range: {} to {}".format(PROJECT_ID, QUERY_ID, START_DATETIME.get_regular() if START_DATETIME is not None else None,
                                                                        END_DATETIME.get_regular() if END_DATETIME is not None else None))
        if event == "C_NoToken":
            window["B_RequestToken"].update(visible=values["C_NoToken"])
        if event == "B_RequestToken":
            token_file_path, cache_file_path, pressed_ok = new_token_window()
            if pressed_ok:
                TOKEN_FILE_PATH = token_file_path
                QUERY_CACHE_FILE_PATH = cache_file_path
                window["IT_TokenFile"].update(TOKEN_FILE_PATH)
                window["T_CacheFile"].update(QUERY_CACHE_FILE_PATH)
                window["C_NoToken"].update(False)
                window["B_RequestToken"].update(visible=False)
        if event == "IT_OutputFolder":
            OUTPUT_FOLDER = values["IT_OutputFolder"]
        if event in time_handlers:
            START_DATETIME = FormattedDateTime(values["I_StartDate"], values["S_StartHours"], values["S_StartMinutes"], values["S_StartSeconds"])
            END_DATETIME = FormattedDateTime(values["I_EndDate"], values["S_EndHours"], values["S_EndMinutes"], values["S_EndSeconds"])
            window["T_StartDateTime"].update(START_DATETIME.get_bw_format())
            window["T_EndDateTime"].update(END_DATETIME.get_bw_format())
            window["T_Status"].update(
                "Project: {} Query: {} Datetime Range: {} to {}".format(PROJECT_ID, QUERY_ID, START_DATETIME,
                                                                        END_DATETIME))
            OUTPUT_FOLDER = values["IT_OutputFolder"]
            OUTPUT_FILE_NAME = "{}_to_{}_{}_BWAPI_{}.csv.zip".format(START_DATETIME.get_file_name_format(),
                                                                     END_DATETIME.get_file_name_format(),
                                                                     "" if BW_ACCESSOR is None else
                                                                     BW_ACCESSOR.user,
                                                                     QUERY_NAME)
            window["T_OutputFile"].update(OUTPUT_FILE_NAME)
            SYSTEM_STATE = 6
        if event == "B_Download":
            if SYSTEM_STATE >= 6:
                print(os.path.join(OUTPUT_FOLDER, OUTPUT_FILE_NAME))
                data_df = BW_ACCESSOR.download_data(PROJECT_ID, QUERY_ID, START_DATETIME.get_bw_format(), END_DATETIME.get_bw_format())
                data_df.to_csv(os.path.join(OUTPUT_FOLDER, OUTPUT_FILE_NAME), index=False)
        print(PROJECT_ID, QUERY_ID)
    window.close()
    cached_values.save()

#
# if __name__ == "__main__":
#     main()
