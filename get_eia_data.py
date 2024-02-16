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

# data_getter.get_data_from_route('electricity/operating-generator-capacity/',
#                     data_cols=['nameplate-capacity-mw', 'net-summer-capacity-mw', 'net-winter-capacity-mw', 'operating-year-month', 'planned-retirement-year-month', 'planned-derate-year-month', 'planned-derate-summer-cap-mw', 'planned-uprate-year-month', 'planned-uprate-summer-cap-mw', 'county', 'longitude', 'latitude'],
#                     fcts_dict={'stateid':'MA'},
#                     start='2022-12-31'
#                     )

# Uncomment to generate a map of electric plants in Massachusets using OpenStreetMap data.
# Set the mapbox flag to True if you want Mapbox data (but you'll need a Mapbox API token (see README). 
data_getter.map_electric_plants(facets={'stateid':['MA']}, mapbox=False, open_street=True,
                                static_fig_title="Map of Electric Power Plants in Massachusets<br><sup>Size Represents Nameplate Capacity</sup>",
                                dynamic_fig_title="Map of Electric Power Plants in Massachusets<br><sup>Size Represents Nameplate Capacity<br>(hover for details)</sup>")

# Uncomment to generate a map of electric plants in New England using OpenStreetMap data.
# Set the mapbox flag to True if you want Mapbox data (but you'll need a Mapbox API token (see README). 
# data_getter.map_electric_plants(facets={'stateid':['MA', "NH", "CT", "ME", "VT", "RI"]}, mapbox=False, open_street=True,
#                                 open_street_file_name="open_street_NE_electric",
#                                 static_fig_title="Map of Electric Power Plants in New England<br><sup>Size Represents Nameplate Capacity</sup>",
#                                 dynamic_fig_title="Map of Electric Power Plants in New England<br><sup>Size Represents Nameplate Capacity<br>(hover for details)</sup>")                                