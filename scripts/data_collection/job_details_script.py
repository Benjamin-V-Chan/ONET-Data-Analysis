from onet_data_collector.job_details import fetch_job_details
from utils import get_user_input

username = get_user_input('Enter O*NET Web Services username')
password = get_user_input('Enter O*NET Web Services password')
input_csv_path = 'data/raw/keyword_search_results.csv'
output_json_path = 'data/raw/job_details.json'
fetch_job_details(username, password, input_csv_path, output_json_path)