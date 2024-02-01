import pandas as pd
import requests
import time
import json


class Eia :
    """
    This class defines various methods for accessing data from the API at the EIA
    (U.S. Energy Information Administration).
    
    Attributes
    ----------
    api_key : string
        your EIA api key
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
        # Retrieve the api key
        try :
            with open('api_key.json') as json_file:
                self.api_key = json.load(json_file)['api_key']
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
                            sort_direction='desc', offset=0, num_data_rows_per_call=5000) :
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
        file_name = ''
        for s in route.split('/'):
            file_name = file_name + s+'-' if s !='' else file_name
        # Get rid of the extraneious hyphen at the end
        file_name = file_name[:-1]
        complete_df.to_csv(file_name+'.csv')
        print(complete_df.head(20))
        return df

