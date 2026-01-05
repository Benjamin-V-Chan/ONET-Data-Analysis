from onet_data_collector.condensed_job_details import condense_job_details

input_json_path = 'data/raw/job_details.json'
output_csv_path = 'data/processed/condensed_job_details.csv'
condense_job_details(input_json_path, output_csv_path)