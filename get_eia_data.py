import eia

data_getter = eia.Eia()

# Uncomment the next line if you want a map of all of the
# EIA API routes.
#map_df = data_getter.map_tree()

# Uncomment the following if you want a csv file of
# all of the routes.
#map_df.to_csv('all_routes_map.csv')

# Add a route to get a subtree.
# This call will map the routes under the electicity node.
elec_map_df = data_getter.map_tree('electicity')
elec_map_df.to_csv('all_routes_map.csv')

# Create a CSV file with the data from the electicity retail-sales route.
# data_getter.get_data_from_route('electricity/retail-sales',
#                                 data_cols=['revenue', 'sales', 'price', 'customers'],
#                                 fcts_dict={'stateid':'MA', 'sectorid':'RES'},
#                                 freq_list=['monthly'])

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

# This is super useful. It gives practically up to the minute hourly info about how many megawatthours
# of electricity each fueltype produces.
# get_data_from_route('electricity/rto/fuel-type-data/',
#                     data_cols=['value'],
#                     freq_list=['local-hourly'],
#                     fcts_dict={'respondent':['ISNE']},
#                     start='2024-01-20'
#                     )

# Oddly, this doesn't seem to include subregion data for New England.
# get_data_from_route('electricity/rto/region-sub-ba-data/',
#                     data_cols=['value'],
#                     freq_list=['local-hourly'],
#                     #fcts_dict={'respondent':['ISNE']},
#                     start='2024-01-21'
#                     )

# This is cool. It shows how electricity moves from one regional
# balancing authority to another on an hourly basis.
# get_data_from_route('electricity/rto/interchange-data/',
#                     data_cols=['value'],
#                     freq_list=['local-hourly'],
#                     fcts_dict={'fromba':['ISNE']},
#                     start='2024-01-22'
#                     )

# This shows net generation, total demand, and how much came from the interchange.
# get_data_from_route('electricity/rto/daily-region-data/',
#                     data_cols=['value'],
#                     freq_list=['daily'],
#                     fcts_dict={'respondent':['ISNE'], 'type': ['NG', 'TI', 'D'], 'timezone':['Eastern']},
#                     start='2023-12-31'
#                     )

# As above, this doesn't seem to include data for new england.
# get_data_from_route('electricity/rto/daily-region-sub-ba-data/',
#                     data_cols=['value'],
#                     freq_list=['daily'],
#                     #fcts_dict={'respondent':['ISNE'], 'type': ['NG', 'TI', 'D'], 'timezone':['Eastern']},
#                     start='2024-01-20'
#                     )


# ******** Cool. This shows daily amount of electricity generated
# using a particular fuel.
# get_data_from_route('electricity/rto/daily-fuel-type-data/',
#                     data_cols=['value'],
#                     freq_list=['daily'],
#                     fcts_dict={'respondent':['ISNE'], 'timezone':['Eastern']},
#                     start='2024-01-15'
#                     )


# This is cool. It shows how electricity moves from one regional
# balancing authority to another on an daily basis.
# get_data_from_route('electricity/rto/daily-interchange-data/',
#                     data_cols=['value'],
#                     freq_list=['daily'],
#                     fcts_dict={'fromba':['ISNE'], 'timezone':['Eastern']},
#                     start='2024-01-15'
#                     )

# Shows Annual Emissions by state.
# get_data_from_route('electricity/state-electricity-profiles/emissions-by-state-by-fuel',
#                     data_cols=['so2-rate-lbs-mwh', 'so2-short-tons', 'nox-rate-lbs-mwh', 'nox-short-tons', 'co2-rate-lbs-mwh', 'co2-thousand-metric-tons'],
#                     fcts_dict={'stateid':'MA'},
#                     start='2020-12-31'
#                     )

# Shows state capability profile by type.
# get_data_from_route('electricity/state-electricity-profiles/capability/',
#                     data_cols=['capability'],
#                     fcts_dict={'stateId':'MA'},
#                     start='2020-12-31'
#                     )

# get_data_from_route('electricity/state-electricity-profiles/energy-efficiency/',
#                     data_cols=['energy-savings', 'potential-peak-savings', 'customer-incentive', 'all-other-costs'],
#                     fcts_dict={'state':'MA'},
#                     start='2020-12-31'
#                     )

# Shows capacity by sector (RES, etc.)
# get_data_from_route('electricity/state-electricity-profiles/net-metering/',
#                     data_cols=['capacity', 'customers'],
#                     fcts_dict={'state':'MA'},
#                     start='2020-12-31'
#                     )

# Shows the number of meters.
# get_data_from_route('electricity/state-electricity-profiles/meters/',
#                     data_cols=['meters'],
#                     fcts_dict={'state':'MA'},
#                     start='2020-12-31'
#                     )

# Shows capacity and ranking.
# get_data_from_route('electricity/state-electricity-profiles/summary/',
#                     data_cols=['net-summer-capacity', 'net-summer-capacity-rank', 'capacity-elec-utilities', 'capacity-elect-utilities-rank', 'capacity-ipp', 'capacity-ipp-rank', 'net-generation', 'net-generation-rank', 'generation-elect-utils', 'generation-elect-utils-rank', 'generation-ipp', 'generation-ipp-rank', 'sulfer-dioxide', 'sulfer-dioxide-rank', 'nitrogen-oxide', 'nitrogen-oxide-rank', 'carbon-dioxide', 'carbon-dioxide-rank', 'sulfer-dioxide-lbs', 'sulfer-dioxide-rank-lbs', 'nitrogen-oxide-lbs', 'nitrogen-oxide-rank-lbs', 'carbon-dioxide-lbs', 'carbon-dioxide-rank-lbs', 'total-retail-sales', 'total-retail-sales-rank', 'fsp-service-provider-sales', 'fsp-sales-rank', 'eop-sales', 'eop-sales-rank', 'direct-use', 'direct-use-rank', 'average-retail-price', 'average-retail-price-rank', 'prime-source'],
#                     fcts_dict={'stateID':'MA'},
#                     start='2020-12-31'
#                     )


# Cool. Shows operator generator capacity and lat long locations.
# get_data_from_route('electricity/operating-generator-capacity/',
#                     data_cols=['nameplate-capacity-mw', 'net-summer-capacity-mw', 'net-winter-capacity-mw', 'operating-year-month', 'planned-retirement-year-month', 'planned-derate-year-month', 'planned-derate-summer-cap-mw', 'planned-uprate-year-month', 'planned-uprate-summer-cap-mw', 'county', 'longitude', 'latitude'],
#                     fcts_dict={'stateid':'MA'},
#                     start='2022-12-31'
#                     )

# Cool. Shows fuel used by each facility.
# get_data_from_route('electricity/facility-fuel/',
#                     data_cols=['generation', 'gross-generation', 'total-consumption', 'total-consumption-btu', 'consumption-for-eg', 'consumption-for-eg-btu', 'average-heat-content'],
#                     fcts_dict={'state':'MA'},
#                     freq_list=['annual'],
#                     start='2020-12-31'
#                     )

#get_data_from_route(base_url+'electricity/retail-sales')
#get_data_from_route(base_url+'electricity/rto/fuel-type-data')
#get_data_from_route(base_url+'electricity/rto/fuel-type-data')
#get_data_from_route(base_url+'electricity/state-electricity-profiles/summary/')
#get_data_from_route(base_url+'electricity/rto/daily-fuel-type-data/')
#https://api.eia.gov/v2/electricity/rto/daily-fuel-type-data/
#https://api.eia.gov/v2/electricity/state-electricity-profiles/source-disposition/
#https://api.eia.gov/v2/electricity/state-electricity-profiles/meters/
#https://api.eia.gov/v2/electricity/operating-generator-capacity/
#https://api.eia.gov/v2/electricity/facility-fuel/
#https://api.eia.gov/v2/electricity/state-electricity-profiles/summary/
#get_data_from_route(https://api.eia.gov/v2/electricity/rto/region-data/)
#map_df = map_tree(base_url, route='electricity')
#print(map_df.head())
#map_df.to_csv("route_map.csv")

        
#map_elec_tree()
 
#get_route() 
        
#get_elec_retail_sales()
#get_elec_power_ops()