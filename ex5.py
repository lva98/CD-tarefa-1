import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

conn = sqlite3.connect('eplusout.sql')
report_data_dict = pd.read_sql_query("SELECT * FROM ReportDataDictionary", conn)
report_data = pd.read_sql_query("SELECT * FROM ReportData", conn)
time = pd.read_sql_query("SELECT * FROM Time", conn)
time = time[['TimeIndex', 'Day', 'Hour', 'Minute', 'SimulationDays']]

pairs = [
    ('THERMAL ZONE 1', 'Zone Mean Air Temperature'),
    ('Environment', 'Site Outdoor Air Drybulb Temperature'),
    ('NODE 10', 'System Node Mass Flow Rate'),
]

filtered_dict = report_data_dict[report_data_dict[['KeyValue', 'Name']]
    .apply(tuple, axis=1)
    .isin(pairs)]

filtered_dict.loc[:, 'Name'] = filtered_dict['KeyValue'] + '/' + filtered_dict['Name']
filtered_dict = filtered_dict[['ReportDataDictionaryIndex', 'Name']]

merged = pd.merge(report_data, filtered_dict, on='ReportDataDictionaryIndex')
merged = pd.merge(merged, time, on='TimeIndex')

pivot = merged.pivot(index=['TimeIndex', 'Hour', 'Minute', 'Day'], columns='Name', values='Value')
pivot['Time'] = pivot.index.get_level_values('Hour').astype(str).str.zfill(2) + ':' + pivot.index.get_level_values('Minute').astype(str).str.zfill(2)
pivot = pivot.sort_index(level='TimeIndex')
pivot.reset_index(inplace=True)
pivot.set_index('Time', inplace=True)

groups = pivot.groupby('Day')
group_iterator = iter(groups)

for i in range(7):
    figure, axis = plt.subplots(sharex='all', sharey='all', figsize=(10, 6))

    day, group = next(group_iterator)

    for key_value, value in pairs:
        column = key_value + '/' + value
        group[column].plot(ax=axis, label=column)

    axis.set_title(f'Day {day}')
    axis.set_xlabel('Time')
    axis.set_ylabel('Value')
    plt.legend(loc='upper left', bbox_to_anchor=(-0.05, 1.2))
    plt.tight_layout()
    plt.savefig(f'graph_day_{day}.png')
