import eia

# Create an Eia object
data_getter = eia.Eia()

## Examples of Mapping the API data hierarchy.

# Uncomment the following two lines if you want a map of all of the
# EIA API routes and a csv file of them.

#map_df = data_getter.map_tree()
#map_df.to_csv('all_routes_map.csv')

# Specify a parent node if you only want the routes under
# that heading.
# For example, the next two lines will map the routes under
# the electricity node and create a CSV file of them.

# elec_map_df = data_getter.map_tree(route='electricity')
# elec_map_df.to_csv('elec_routes_map.csv')

## Examples of Retrieving Data.

# Create a CSV file with the data from the electricity/retail-sales route.
# Note the use of data columns, facets, and frequency.

# data_getter.get_data_from_route('electricity/retail-sales',
#                                 data_cols=['revenue', 'sales', 'price', 'customers'],
#                                 fcts_dict={'stateid':'MA', 'sectorid':'RES'},
#                                 freq_list=['monthly'])

# A few other examples.

# get_data_from_route('electricity/electric-power-operational-data/',
#                     data_cols=['generation', 'total-consumption', 'consumption-for-eg', 'consumption-uto', 'total-consumption-btu', 'consumption-for-eg-btu', 'consumption-uto-btu', 'stocks', 'receipts', 'receipts-btu', 'cost', 'cost-per-btu', 'sulfur-content', 'ash-content', 'heat-content'],
#                     freq_list=['quarterly'],
#                     fcts_dict={'location':'MA', 'sectorid':'99'}
#                     )

# get_data_from_route('electricity/rto/region-data/',
#                     data_cols=['value'],
#                     freq_list=['hourly'],
#                     fcts_dict={'respondent':['ISNE']}
#                     )

# get_data_from_route('electricity/rto/fuel-type-data/',
#                     data_cols=['value'],
#                     freq_list=['local-hourly'],
#                     fcts_dict={'respondent':['ISNE']},
#                     start='2024-01-20'
#                     )

# get_data_from_route('electricity/rto/interchange-data/',
#                     data_cols=['value'],
#                     freq_list=['local-hourly'],
#                     fcts_dict={'fromba':['ISNE']},
#                     start='2024-01-22'
#                     )

# get_data_from_route('electricity/rto/daily-region-data/',
#                     data_cols=['value'],
#                     freq_list=['daily'],
#                     fcts_dict={'respondent':['ISNE'], 'type': ['NG', 'TI', 'D'], 'timezone':['Eastern']},
#                     start='2023-12-31'
#                     )