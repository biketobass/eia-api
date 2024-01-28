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
        # Add the route to the base url.
        # Make the request.
        # Return the response.
        try :
            r = requests.get(self.base_url+route, params=params)
        except requests.exceptions.RequestException as e:
            print("Could not make the API request")
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
        if route != '':
            print(f'{spacing}At route {route}')
        else :
            print('Top level')
        # Make the api call
        r = self.make_api_call(route, params={})
        if 'routes' in r :
            for route_table in r['routes'] :
                rte = route + '/' + route_table['id']
                df = self.map_tree(df, route=rte, spacing=spacing+'    ')
        else :
            spacing += '    '
            print(f"{spacing}{route}")
            # Get the lists of facets, data columns, and frequencies
            facet_list = [f_table['id'] for f_table in r['facets']]
            freq_list = [freq_table['id'] for freq_table in r['frequency']]
            data_cols = [k for k in r['data'].keys()]
            df.loc[len(df)] = [route, facet_list, freq_list, data_cols]
            # Print it to a csv file.
        return df
                
    def get_data_from_route(self, route, data_cols=None, fcts_dict=None, freq_list = None, start=None, end=None, sort_col='period', sort_direction='desc') :
        route_to_data = route+'/data'
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
        print(r.keys())
        if 'warnings' in r :
            print(r['warnings'])
        if 'total' in r :
            print(r['total'])
        data = r['data']        
        df = pd.DataFrame.from_dict(data)
        file_name = ''
        for s in route.split('/'):
            file_name = file_name + s+'-' if s !='' else file_name
        df.to_csv(file_name+'.csv')
        print(df.head(20))

