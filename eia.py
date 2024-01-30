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
                
    def get_data_from_route(self, route, data_cols=None, fcts_dict=None, freq_list = None, start=None, end=None, sort_col='period', sort_direction='desc') :
        """
        Given a route that represent a leaf node in the EIA API, create a CSV file of the data associated with it.

        Args:
            route (string): route to a leaf node in the API
            data_cols (list, optional): List of data columns to include in the CSV. Defaults to None.
            fcts_dict (dict, optional): Dictionary containing the facets we want to filter by. Defaults to None.
            freq_list (list, optional): List of frequencies to receive (hourly, monthly, etc). Defaults to None.
            start (string, optional): date after which to return data in the form 2024-01-28. Defaults to None.
            end (string, optional): end data in the form 2024-01-28. Defaults to None.
            sort_col (str, optional): column by which to sort. Defaults to 'period'.
            sort_direction (str, optional): sort direction ascending or descending. Defaults to 'desc'.
        """
        route_to_data = route+'/data'        
        # Fill in the parameters
        params = {}
        if data_cols :
            params['data[]'] = data_cols
        if fcts_dict :
            for k,v in fcts_dict.items():
                prm_key = f'facets[{k}][]'
                params[prm_key] = v
        if freq_list :
            params['frequency'] = freq_list
        if start :
            params['start'] = start
        if end:
            params['end'] = end
        params['sort[0][column]'] = sort_col
        params['sort[0][direction]'] = sort_direction
        r = self.make_api_call(route_to_data, params)
        # For kicks print the keys of the reponse.
        print(r.keys())
        # If there are any warning, print them.
        if 'warnings' in r :
            print(r['warnings'])
        # Print the total number of results.
        if 'total' in r :
            print(r['total'])
        # Get the data from the response and
        # store it in a df.
        data = r['data']        
        df = pd.DataFrame.from_dict(data)
        # Save it in an appropriately named file.
        file_name = ''
        for s in route.split('/'):
            file_name = file_name + s+'-' if s !='' else file_name
        # Get rid of the extraneious hyphen at the end
        file_name = file_name[:-1]
        df.to_csv(file_name+'.csv')
        print(df.head(20))
        return df

