import pandas as pd
import sqlite3

conn = sqlite3.connect('eplusout.sql')
report_data_dict = pd.read_sql_query("SELECT * FROM ReportDataDictionary", conn)
report_data = pd.read_sql_query("SELECT * FROM ReportData", conn)

pairs = [
    ('THERMAL ZONE 1', 'Zone Mean Air Temperature'),
    ('Environment', 'Site Outdoor Air Drybulb Temperature'),
    ('Environment', 'Site Wind Speed'),
    ('Environment', 'Site Wind Direction'),
    ('Environment', 'Site Horizontal Infrared Radiation Rate per Area'),
    ('Environment', 'Site Diffuse Solar Radiation Rate per Area'),
    ('Environment', 'Site Direct Solar Radiation Rate per Area'),
    ('OFFICE WORK OCC', 'Schedule Value'),
    ('NODE 10', 'System Node Mass Flow Rate'),
]

filtered_dict = report_data_dict[report_data_dict[['KeyValue', 'Name']]
    .apply(tuple, axis=1)
    .isin(pairs)]

filtered_dict.loc[:, 'Name'] = filtered_dict['KeyValue'] + '/' + filtered_dict['Name']
filtered_dict = filtered_dict[['ReportDataDictionaryIndex', 'Name']]
merged = pd.merge(report_data, filtered_dict, on='ReportDataDictionaryIndex')
pivot = merged.pivot(index='TimeIndex', columns='Name', values='Value')

correlations = pivot.corrwith(pivot['THERMAL ZONE 1/Zone Mean Air Temperature'])
sorted = correlations.abs().sort_values(ascending=False)
print(sorted)
