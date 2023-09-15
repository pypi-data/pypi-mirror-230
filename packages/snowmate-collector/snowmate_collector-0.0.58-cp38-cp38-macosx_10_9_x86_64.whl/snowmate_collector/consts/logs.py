PROCESS_FINISHED = "Process finished. Waiting for Snowmate to finish \
tests collection. This may take a few seconds…"
PROCESS_TIMEOUT = "Process exit timed out."
COLLECTOR_DONE = "Snowmate collector is done."
DEBUG_MODE = "Please notice that Snowmate does not \
run in debug mode (pause Snowmate to mute this message)."
NO_SUCH_PROJECT_ID = (
    "No such project id, snowmate_collector is exiting.\n\n"
    "You need to create a Snowmate project for your repository through Snowmate Web App "
    "at https://app.snowmate.io and pass its ID to snowmate_collector.start()."
)

COLLECTOR_COMMUNICATION_ERROR = (
    "snowmate_collector couldn't communicate with snowmate servers, is exiting.\n\n"
)

AUTH_ERROR = (
    "Snowmate Auth Error: Please make sure you are using the correct Snowmate client ID and secret key.\n"
    "You can request new ones from your Snowmate admin, \
        or generate new credentials in the project setup page."
)
LOGGER_NAME = "snowmate"
DEBUG_LOGGER_NAME = "snowmate_debug"
RUNNING_IN_SANITY_MODE = (
    "Snowmate data collector is running in Sanity mode...\n"
    "(Sanity mode collects 100% of your function invocations, so it will"
    " slow down your code considerably)\n"
)

GENERAL_METRICS_WERE_COLLECTED_SUCCESSFULLY = (
    "* General metadata was collected successfully"
)
TESTS_METRICS_WERE_COLLECTED_SUCCESSFULLY = (
    "* Tests metadata was collected successfully"
)
TESTS_DATA_WAS_COLLECTED_SUCCESSFULLY = "* Tests data was collected successfully"
SUCCESSFUL_AUTH = "* Authentication was successful"
