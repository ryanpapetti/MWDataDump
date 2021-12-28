'''
MWDataDump

Code to run a periodic data dump of Modern Warfare data
'''

import requests, os, boto3, json, time


class Contacter:
    def __init__(self,gamer_tag:str, platform:str, api_key:str):
        """
        initializes Contacter instance with given variables

        Args:
            gamer_tag (str): specific gamer tag to retrieve data
            platform (str): platform where gamer tag is present
            api_key (str): api key from rapidapi app
        """
        self._gamer_tag = gamer_tag
        self._session = requests.session()
        self._api_key = api_key
        self._platform = platform #can change to any platform
        self.api_host = 'call-of-duty-modern-warfare.p.rapidapi.com'
        self.base_url = f'https://{self.api_host}'
        self._auth_header = {'x-rapidapi-host':self.api_host, 'x-rapidapi-key':self._api_key}


    
    def make_query(self,endpoint:str):
        """
        makes query to endpoint to retrieve data

        Args:
            endpoint (str): specificed endpoint to tack onto base url

        Returns:
            dict: JSON of response
        """
        final_url = self.base_url + endpoint
        response = self._session.get(final_url, headers = self._auth_header)
        print(response.json())
        try:
            assert response.status_code // 100 == 2
            assert 'matches' in response.json()
            return response.json()
        except AssertionError:
            raise AssertionError('RESPONSE IS NOT VALID')

    


    def get_recent_match_summaries(self):
        """
        gets the array of the user's most recent matches. Believe it is 20 matches

        Returns:
            array: JSON array of most recent matches
        """
        # assert self.is_primed()
        response = self.make_query(f'/multiplayer-matches/{self._gamer_tag}/{self._platform}')
        #I just want the actual most recent matches
        return response['matches']

    
    def upload_data_to_bucket(self,uploadable_data:list,desired_name:str):
        """
        upload entire array to bucket as a JSON obj

        Args:
            uploadable_data (list)
            desired_name (str): key for bucket
        """
        
        s3 = boto3.client('s3')
        s3_args = {'Body':bytes(json.dumps(uploadable_data),'utf-8'), 'Bucket':os.environ.get('MWBucketARN').split(':')[-1], 'Key':desired_name, 'ContentType':'application/json'}
        s3.put_object(**s3_args)
        print('successful upload to bucket')

        
    def upload_to_dynamodb_table(self,uploadable_data:list,table_name:str):
        """
        
        upload relevant data to the specific dynamodb table name

        Args:
            uploadable_data (list)
            table_name (str)
        """
        dynamodb = boto3.resource('dynamodb')
        active_table = dynamodb.Table(table_name)
        for item in uploadable_data:
            playerstats = item.pop('playerStats')
            #we only care about playerstats really so update data with those values if relevant
            item.update(playerstats)

            #pop out irrelevant data for us
            _ = item.pop('weaponStats')
            _ = item.pop('player')

            #prepare data to add to table
            new_item = {key:str(val) if type(val) in [float] else val for key,val in item.items()}
            
            #add to table
            active_table.put_item(Item = new_item)

        print('successfully uploaded data to table')
    


    
def lambda_handler(event,context):
    """
    
    DEFAULT MAIN FUNCTION FOR LAMBDAD ON AWS. ARGS ARE IRRELEVANT AS OF NOW
    """
    chosen_gamertag = 'StonedTensor%235316760'
    chosen_platform = 'acti'
    chosen_api_key = os.environ.get('API_KEY')

    ry_contacter = Contacter(platform = chosen_platform, api_key = chosen_api_key, gamer_tag = chosen_gamertag)
    most_recent_matches = ry_contacter.get_recent_match_summaries()
    ry_contacter.upload_data_to_bucket(most_recent_matches,str(int(time.time())))
    ry_contacter.upload_to_dynamodb_table(most_recent_matches,os.environ.get('MWDynamoTable'))
    print('SUCCESS')
    return {'status_code':200, 'body':json.dumps('SUCCESS')}