import pandas as pd
import requests
import time
import json
import plotly.graph_objects as go
import plotly.express as px


class Eia :
    """
    This class defines various methods for accessing data from the API at the EIA
    (U.S. Energy Information Administration).
    
    Attributes
    ----------
    api_key : string
        your EIA api key
    mapbox_token : string
        your mapbox api token (if you have one)
    base_url : string
        the base url of the EIA API

    Methods
    -------
    __init__()
        Create a new Eia object by setting base_url and the api_key
    make_api_call(params)
        Make a call to the Eia api given the specified parameters.
    
    """
    
    def __init__(self) -> None:
        """
        Create a new Eia object.

        When the object is created, the constructor sets the base eia api url
        and retrieves the api key that should already be stored in a file in the same
        directory called api_key.json.
        """
        # Set the base url
        self.base_url = 'https://api.eia.gov/v2/'
        # Retrieve the api key for EIA and for mapbox
        try :
            with open('api_key.json') as json_file:
                apis = json.load(json_file)
                self.api_key = apis['api_key']
                self.mapbox_token = apis['mapbox_token'] if 'mapbox_token' in apis else None
        except FileNotFoundError:
            print('api_key.json does not exist yet. Consult the Readme.')
            quit()

    def make_api_call(self, route="", params={}) :
        """
        Make a call to the EIA api using the given parameters.
    
        The method waits a second before making the call to avoid hitting
        the API's rate limit. The documentation does not specify what that limit
        is, but it mentions that there is one.
        
        Args:
            route (string) : the path through the API
            params (dict): dictionary containing the parameters such as
            facets, data column names, and frequencies
            
        Returns:
        dict
            a dictionary holding the api call response
        """
        
        # Add the api key to the parameters.
        params['api_key'] = self.api_key
        # Sleep for 1 second before making the request to prevent hitting
        # the API's rate limit (not sure what it is) when there are repeated calls.
        # Add the route to the base url.
        # Make the request.
        # Return the response.
        try :
            time.sleep(1)
            r = requests.get(self.base_url+route, params=params)
        except requests.exceptions.RequestException as e:
            print("Could not make the API request")
            print(e)
        else :
            r = r.json()
            if 'response' in r :
                return r['response']
            else :
                print("The returned dictionary did not contain a key equal to 'response'. There must have been an error. Printing the full dictionary.")
                print(r)
                return {}


    # Recursively map all of the routes in the tree starting from a
    # parent route.
    # Make a call at the level of the url and the parent route.
    # Get the children routes of the parent. For each child route
    # call map_tree. Stop recursing when the response
    # has no routes. At that point the response will have a child node
    # called data, and filtering info about the data (facets, frequencies, data columns.)
    def map_tree(self, df=pd.DataFrame(columns=['route', 'facet_list', 'freq_list', 'data_cols']),
                 route='', spacing='') :
        """
        Map all of the routes in the EIA API.
        
        Starting from a parent route (top-level is an empty string), recursively map all of the
        children routes. Make a call at the level of the parent. Get the child routes of the parent.
        For each child route call map_tree. Stop recursing when the response has no further routes.
        At that point the resopnse will have a child node called data and filtering information about the data
        (facets, frequencies, data columns).

        Args:
            df (DataFrame, optional): DataFrame to hold the results. Defaults to an empty DF defined as pd.DataFrame(columns=['route', 'facet_list', 'freq_list', 'data_cols']).
            route (str, optional): the parent route. Defaults to '' which is the top level.
            spacing (str, optional): simply used to format command line output. Defaults to ''.

        Returns:
            DataFrame: Pandas DataFrame containing information about each route under the parent.
        """
        
        # For command line output.
        if route != '':
            print(f'{spacing}At route {route}')
        else :
            print('Top level')
        # Make the api call
        r = self.make_api_call(route, params={})
        # If the response dictionary has a routes key, it had children routes.
        # If not, it's a leaf and has data associated with it.
        if 'routes' in r :
            # It has children so recurse.
            for route_table in r['routes'] :
                rte = route + '/' + route_table['id']
                df = self.map_tree(df, route=rte, spacing=spacing+'    ')
        else :
            # It's a leaf so get the data filering information.
            spacing += '    '
            print(f"{spacing}{route}")
            # Get the lists of facets, data columns, and frequencies
            # Add them to the df.
            facet_list = [f_table['id'] for f_table in r['facets']]
            freq_list = [freq_table['id'] for freq_table in r['frequency']]
            data_cols = [k for k in r['data'].keys()]
            df.loc[len(df)] = [route, facet_list, freq_list, data_cols]
        return df
    
    
    def get_data_from_route(self, route, data_cols=None, fcts_dict=None, freq_list = None, start=None, end=None, sort_col='period',
                            sort_direction='desc', offset=0, num_data_rows_per_call=5000, csv_file_name=None) :
        """
        Given a route that represent a leaf node in the EIA API, return a Pandas DataFrame of the data
        associated with it and save a CSV file of the data.

        Before calling this method, use map_tree to retrieve lists of data columns, facets, and frequencies available
        for a particular route. Note also that the arguments offset and num_data_rows serve two functions. 1) The EIA
        is only able to return 5000 rows of data per call. The defaults of offset = 0 and num_data_rows_per_call
        = 5000 enable pagination of the data. If there are more than num_data_rows_per_call available this method will
        retrieve the first num_data_rows_per_call. It will then increment offset by num_data_rows_per_call and make a
        second call to receive the next batch. This behavior repeats until there are no more data rows to return.
        2) It may be the case that you only want a certain number of rows starting at a particular rows. You can set
        offset and num_data_rows to receive only the rows you are interested in.

        Args:
            route (string): route to a leaf node in the API as defined by the EIA API technical document.
            data_cols (list, optional): List of data columns to include in the CSV. Defaults to None.
            fcts_dict (dict, optional): Dictionary containing the facets we want to filter by. Defaults to None.
            freq_list (list, optional): List of frequencies to receive (hourly, monthly, etc). Defaults to None.
            start (string, optional): date after which to return data in the form 2024-01-28. Defaults to None.
            end (string, optional): end date in the form 2024-01-28. Defaults to None.
            sort_col (str, optional): column by which to sort. Defaults to 'period'.
            sort_direction (str, optional): sort direction ascending or descending. Defaults to 'desc'.
            offset (int, optional) : the number of data rows to skip. Defaults to 0.
            num_data_rows_per_call : the maximum number of data rows the API should return per call. Defaults to 5000.
            cvs_file_name (string, optional) : name of the csv file of the data that the method will create. If None, the filename will be based on the route. Defaults to None.
            
         Returns:
            DataFrame: Pandas DataFrame containing the data.
        """
        if num_data_rows_per_call > 5000 :
            print("The number of data rows per call can't be greater than 5,000. Setting it to 5,000.")
            num_data_rows_per_call = 5000
        route_to_data = route+'/data'        
        # Fill in the parameters for the API call.
        params = {}
        # Data columns you want
        if data_cols :
            params['data[]'] = data_cols
        # Facets to filter by
        if fcts_dict :
            for k,v in fcts_dict.items():
                prm_key = f'facets[{k}][]'
                params[prm_key] = v
        # Frequencies you want
        if freq_list :
            params['frequency'] = freq_list
        # Start and End
        if start :
            params['start'] = start
        if end:
            params['end'] = end
        # Sort info.
        params['sort[0][column]'] = sort_col
        params['sort[0][direction]'] = sort_direction
        # Set the max number of rows to receive.
        params['length'] = num_data_rows_per_call
        # DF to hold the results
        complete_df = pd.DataFrame()
        # Loop until there is no more data to retrieve.
        while True :
            # Set the offset here because it will be updated
            # at the end of each iteration.
            params['offset'] = offset
            print(f"Making the API call. offset = {offset}")
            r = self.make_api_call(route_to_data, params)
            # For kicks print the keys of the reponse.
            print("The call returned with a dictionary whose keys are:")
            print(r.keys())
            # If there are any warnings, print them.
            if 'warnings' in r :
                print("If the warning is about an incomplete return, " + 
                      "it's probably nothing to worry about. It just " +
                      "means that the number of rows returned is less " +
                      "than the total available. The code will make as " +
                      "many calls as necessary to retrieve all of the data.")
                print(r['warnings'])
            # Print the total number of results.
            if 'total' in r :
                print(f"The total number of results available = {r['total']}")
            # Get the data from the response and
            # store it in a df.
            data = r['data']        
            df = pd.DataFrame.from_dict(data)
            # If there is data, add it to the full DF.
            # Otherwise break out of the loop.
            if len(df) > 0 :
                # Concat this df with the one we'll return.
                complete_df = pd.concat([complete_df, df])
            else :
                break
            # Check if we've reach the end of the data.
            # Break if we have.
            if 'total' in r and len(complete_df) == int(r['total']) :
                break
                
            # Increment the offset so that we don't get duplicated
            # data.
            offset += num_data_rows_per_call
        # Save the complete_df in an appropriately named file.
        complete_df = complete_df.reset_index(drop=True)
        print(f"The total number of rows of data retrieved is {len(complete_df)}.")
        # Create the file name if it wasn't specified
        if not csv_file_name :
            csv_file_name = ''
            for s in route.split('/'):
                csv_file_name = csv_file_name + s+'-' if s !='' else csv_file_name
            # Get rid of the extraneious hyphen at the end and add .csv
            csv_file_name = csv_file_name[:-1] + '.csv'
        complete_df.to_csv(csv_file_name)
        print(complete_df.head(20))
        return df
    
    
    def map_electric_plants(self, facets={'stateid':['MA']}, start='2023-09-31',
                            mapbox=False, open_street=True,
                            dynamic_fig_title="Map of Electric Plants",
                            static_fig_title="Map of Electric Plants",
                            init_zoom=7,
                            open_street_file_name="open_street_map",
                            mapbox_file_name="mapbox_map",
                            static_width=1000,
                            static_height=650) :
        """
        Map the eletrical plants within a region defined by the facets argument.
        
        Depending on the truth of the mapbox and open_street keywords the method will use
        Plotly Express scatter_mapbox with Mapbox map data or with OpenStreetMap data. If
        using, Mapbox, you will need a Mapbox API token already stored in the api_key.json.
        See README. If are True, it will produce two maps, one with each type of map data.
        
        Saves both static (.png) and dynamic (.html) versions of the maps. 

        Args:
            facets (dict, optional): facets to define the region. Defaults to {'stateid':['MA']}.
            start (str, optional): the earliest date from which to retrieve data. Defaults to '2023-09-31' which is fine because the method just looks for the most period.
            mapbox (bool, optional): If True uses Mapbox . Defaults to False.
            open_street (bool, optional): If True uses OpenStreetMap data with no token necessary. Defaults to True.
            dynamic_fig_title (str, optional): Title for the dynamic html map. Defaults to "Map of Electric Plants".
            static_fig_title (str, optional): Title for the static PNG map. Defaults to "Map of Electric Plants".
            init_zoom (int, optional): Initial zoom level. Defaults to 7.
            open_street_file_name (str, optional): The output file name (without file type suffix) to use for maps made with OpenStreetMap data. Defaults to "open_street_map".
            mapbox_file_name (str, optional): The output file name (without file type suffix) to use for maps made with Mapbox data. Defaults to "mapbox_map".
            static_width (int, optional): The width of the output static map. Defaults to 1000.
            static_height (int, optional): The height of the output static map. Defaults to 650.
        """
        
        # Start by getting the data from EIA.
        df = self.get_data_from_route('electricity/operating-generator-capacity/',
                                      data_cols=['nameplate-capacity-mw', 'net-summer-capacity-mw',
                                                 'net-winter-capacity-mw', 'operating-year-month',
                                                 'planned-retirement-year-month', 'planned-derate-year-month',
                                                 'planned-derate-summer-cap-mw', 'planned-uprate-year-month',
                                                 'planned-uprate-summer-cap-mw',
                                                 'county', 'longitude', 'latitude'],
                                      fcts_dict=facets,
                                      start=start)
        # Do some datatype conversions since the API returns all the data as String.
        df['period'] = pd.to_datetime(df['period']) # Period should be datetime
        df['latitude'] = df['latitude'].astype(float) # lat and long should be floats
        df['longitude'] = df['longitude'].astype(float)
        df['nameplate-capacity-mw'] = df['nameplate-capacity-mw'].astype(float) # So should nameplate capacity.
        # Only look at the plants specified in the most recent report.
        # Otherwise, we'll have lots of duplicates.
        # Get the most recent period in the df and remove all other periods from the df.
        most_recent_period = df.loc[0,'period']
        df = df[df['period'] == most_recent_period]
        
        # Map the sizes from 1 to 25 based on the nameplate capacity.
        cap_min = df['nameplate-capacity-mw'].min()
        cap_max = df['nameplate-capacity-mw'].max()
        target_max = 25
        target_min = 1
        df['marker_sizes'] = ((df['nameplate-capacity-mw'] - cap_min)/(cap_max - cap_min) * (target_max  - target_min)) + target_min
        
        # This is the text I want shown when we hover over a plant in the plotly versions
        df['hover_text'] = (df['plantName'] + "<br>" + df['county'] + ", " + df['stateid'] +
                      "<br>" + df['technology'] + "<br>" +
                      df['energy-source-desc'] + "<br>" +
                      df['nameplate-capacity-mw'].astype(str) + df['nameplate-capacity-mw-units'] +
                      "<br>" + df['statusDescription'])
        
        # Create a dictionary for the columns and set each to False,
        # because all the hover information I want is already
        # in df['hover_text']. This prevents duplicate info from being shown
        # upon hover.
        hover_dict = dict()
        for col in df.columns :
            hover_dict[col] = False
        # Define colors for fuel sources. This is not an exhaustive list.
        # May need to add to this dictionary as I encounter fuel sources not specified.
        fuel_subset_colors = {"Solar":'rgba(251,147,47,1.0)',
                              "Wind":'rgba(133,85,161,1.0)',
                              "Natural Gas":"rgba(200,200,100,0.6)",
                              "Disillate Fuel Oil":'rgba(98,119,127,0.4)',
                              "Residual Fuel Oil":'rgba(108,69,22,0.4)',
                              "Water":'rgba(23,149,210,0.4)',
                              "Landfill Gas":'rgba(64,211,151,1.0)',
                              "Electricity used for energy storage": 'blue',
                              "Municipal Solid Waste (All)":'rgba(132,85,54,1.0)',
                              "Wood Waste Solids":'rgba(191,98,46,1.0)',
                              "Other Biomass Gases":'rgba(177,102,33,0.4)',
                              "Kerosene":'rgba(76,128,20)'}
        # Create a fig using open_street_map
        if open_street :
            os_fig = px.scatter_mapbox(df, lat="latitude", lon="longitude", color="energy-source-desc",
                                       hover_name="hover_text",
                                       hover_data=hover_dict, # Since the values are all fase, we avoid redundant hover info.
                                       size="marker_sizes", # Scaled according to capacity.
                                       zoom=init_zoom,
                                       color_discrete_map=fuel_subset_colors,
                                       color_discrete_sequence=px.colors.qualitative.Alphabet,
                                       title=dynamic_fig_title,
                                       labels={"energy-source-desc":"Energy Source"}
                                       )
            os_fig.update_layout(mapbox_style="open-street-map")
            os_fig.write_html(open_street_file_name+".html", include_plotlyjs='cdn')
            os_fig.update_layout(title=static_fig_title)
            os_fig.write_image(open_street_file_name+".png", width=static_width, height=static_height)
        
        if mapbox :
            px.set_mapbox_access_token(self.mapbox_token)
            mb_fig = px.scatter_mapbox(df, lat="latitude", lon="longitude", color="energy-source-desc",
                                       hover_name="hover_text",
                                       hover_data=hover_dict,
                                       size="marker_sizes",
                                       zoom=7,
                                       color_discrete_map=fuel_subset_colors,
                                       color_discrete_sequence=px.colors.qualitative.Alphabet,
                                       title=dynamic_fig_title,
                                       labels={"energy-source-desc":"Energy Source"}
                                       )
            mb_fig.write_html(mapbox_file_name+".html",  include_plotlyjs='cdn')
            mb_fig.update_layout(title=static_fig_title)
            mb_fig.write_image(mapbox_file_name+".png", width=static_width, height=static_height)
        

    
    