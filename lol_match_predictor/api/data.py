import numpy as np
import pandas as pd
from lol_match_predictor.api.constants import _API_ENDPOINTS, _RIOT_API_KEY
from lol_match_predictor.api.rate_limiter import RateLimitedAPI
import sqlalchemy as sa
import requests
from pwinput import pwinput

ratelimiter = RateLimitedAPI()

MAX_MATCHES_PER_PLAYER = 1_000 # increments of 100

class SummonerList:
    def __init__(self, matchId, verbose=False):
        self.matchId = matchId
        self._api_endpoint = _API_ENDPOINTS["MATCH-V5"]["matchId"].format(matchId=self.matchId)
        self.summoner_list = None
        self.bad_response = None
        self.summoner_data_list = []
        self.verbose = verbose
    
    def get_summoners_from_match(self):
        params = {
            'api_key': _RIOT_API_KEY
        }
        
        response = None
        
        while response is None or response.status_code != 200:
            response = ratelimiter(self._api_endpoint, name="Retrieving Summoners from Match", total=1, **params)
            if response.status_code != 200:
                self.bad_response = response
                print(f"Received {self.bad_response.status_code} when getting summoner list from matchId {self.matchId}; retrying...")
        self.summoner_list = response.json()['metadata']['participants']
    
    def get_summoner_data(self):
        my_db_pw = pwinput.pwinput("enter db pw: ", mask='*')
        if self.summoner_list is None:
            raise ValueError("You must call get_summoners_from_match() before calling get_summoner_data().")
        for i, summoner in enumerate(self.summoner_list):
            
            if self.verbose:
               print(f'Getting summoner {i}') 
            
            summoner_obj = Summoner(summoner, "encryptedPUUID")
            summoner_fetch_status = summoner_obj.get_summoner()
            summoner_obj.get_matches()
            summoner_obj.save_to_postgres("match_data", "LoL_Stats", "taco", my_db_pw, "192.168.0.201")
            self.summoner_data_list.append(summoner_obj)


class Summoner:
    def __init__(self, identifier, id_type):
        self.identifier = identifier
        self.id_type = id_type

        possible_id_types = ["encryptedPUUID", "summonerName", "encryptedSummonerId"]
        if self.id_type not in possible_id_types:
            raise ValueError(f"id_type must be one of {possible_id_types}")
        
        self._api_endpoint = _API_ENDPOINTS["SUMMONER-V4"][self.id_type].format(identifier=self.identifier)

        self.id = None
        self.accountId = None
        self.puuid = None
        self.name = None
        self.profileIconId = None
        self.revisionDate = None
        self.summonerLevel = None

        self.bad_response = None

        self.match_list = None

    def get_summoner(self):
        params={'api_key': _RIOT_API_KEY}
        
        response = None

        while True:
            response = ratelimiter(self._api_endpoint, name="Retrieving Summoner", **params)
            if isinstance(response, str):
                return False
            elif isinstance(response, requests.models.Response) and response.status_code == 200:
                response_json = response.json()
                # parse the response
                self.id = response_json.get("id", None)
                self.accountId = response_json.get("accountId", None)
                self.puuid = response_json.get("puuid", None)
                self.name = response_json.get("name", None)
                self.profileIconId = response_json.get("profileIconId", None)
                self.revisionDate = response_json.get("revisionDate", None)
                self.summonerLevel = response_json.get("summonerLevel", None)
                return True
    
    def get_matches(self):
        match_list = MatchList(self.puuid)
        match_list.get_match_list()
        match_list.get_match_data()
        self.match_list = match_list
        return match_list
    
    def matches_to_df(self):
        if self.match_list is None:
            raise ValueError("You must call get_matches() before calling matches_to_df().")
        return pd.DataFrame(self.match_list.matches_to_dict())
    
    def save_to_postgres(self, table_name, database_name, user, password, host, port=5432, if_exists='append'):
        engine = sa.create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database_name}')
        df = self.matches_to_df()
        df.to_parquet(f"{self.name}.parquet")
        df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    

class MatchList:
    def __init__(self, puuid):
        self.puuid = puuid

        self._api_endpoint = _API_ENDPOINTS["MATCH-V5"]["puuid"].format(puuid=self.puuid)

        self.all_ranked_matches = []
        self.all_ranked_matches_collection = []

        self.bad_response = None
    
    def get_match_list(self):
        params = {
            'queue': 420,
            'count': 100,
            'start': -1,
            'api_key': _RIOT_API_KEY
        }

        self.all_ranked_matches = []

        continue_next = False
        while True:  
            if params['start'] >= MAX_MATCHES_PER_PLAYER:
                break
            if params['start'] == len(self.all_ranked_matches):
                params['start'] = len(self.all_ranked_matches) + int(params['count'])
            else:
                params['start'] = len(self.all_ranked_matches) 

            response = None
            while True:
                response = ratelimiter(self._api_endpoint, name="Querying Match List", **params)
                if isinstance(response, str):
                    continue_next = True
                    break
                elif isinstance(response, requests.models.Response) and response.status_code == 200:
                    break
            
            if continue_next:
                continue_next = False
                continue

            response_json = response.json()

            if not response_json or len(response_json) == 0:
                break

            self.all_ranked_matches.extend(response_json)

                    

        self.all_ranked_matches = np.unique(self.all_ranked_matches)
        print(f"Found {len(self.all_ranked_matches)} matches.")
        return self.all_ranked_matches
    
    def get_match_data(self):
        self.all_ranked_matches_collection = []

        for matchId in self.all_ranked_matches:
            match = Match(matchId, self.puuid, len(self.all_ranked_matches))
            get_match_status = match.get_match()
            if get_match_status == True: # if it failed to get the match data, it will skip this match
                self.all_ranked_matches_collection.append(match)
            else:
                continue

        print(f"Retrieved data for {len(self.all_ranked_matches_collection)} matches.")
        return self.all_ranked_matches_collection
    
    def matches_to_dict(self):
        # create one dictionary from each match in self.all_ranked_matches_collection
        data = []
        for match in self.all_ranked_matches_collection:
            data.append(match.__dict__())
        return data
    

class Match:
    def __init__(self, matchId, puuid_of_reference, num_of_matches_in_batch=None):
        self.matchId = matchId
        self._api_endpoint = _API_ENDPOINTS["MATCH-V5"]["matchId"].format(matchId=self.matchId)
        self.bad_response = None
        self.puuid_of_reference = puuid_of_reference    
        self.puuid_of_reference_individual_position = None
        self.puuid_of_reference_team_position = None
        self.puuid_of_reference_won = None
        self.game_length = None
        self.game_start_time = None
        self.gameType = None
        self.mapId = None
        self.championId = None 
        self.num_of_matches_in_batch = num_of_matches_in_batch   
    
    def get_match(self):  
        params = {
            'api_key': _RIOT_API_KEY
        }
        
        response = None
        while True:
            response = ratelimiter(self._api_endpoint, name="Downloading Match Data", total=self.num_of_matches_in_batch, **params)  
            if isinstance(response, str):
                return False
            elif isinstance(response, requests.models.Response) and response.status_code == 200:    
                response_json = response.json()

                for participant in response_json["info"]["participants"]:
                    if participant["puuid"] == self.puuid_of_reference:
                        self.puuid_of_reference_individual_position = participant.get('individualPosition', None)
                        self.puuid_of_reference_team_position = participant.get('teamPosition', None)
                        self.puuid_of_reference_won = participant.get('win', None)
                        self.game_length = response_json["info"].get('gameDuration', None)
                        self.game_start_time = response_json["info"].get('gameStartTimestamp', None)
                        self.gameType = response_json["info"].get('gameType', None)
                        self.mapId = response_json["info"].get('mapId', None)
                        self.championId = participant.get('championId', None)
                        self.teamEarlySurrendered = participant.get('teamEarlySurrendered', None)
                        return True  # Stop the loop as soon as we find the participant
        
        
    
    def __dict__(self):
        return {
            "matchId": self.matchId,
            "puuid_of_reference": self.puuid_of_reference,
            "won": self.puuid_of_reference_won,
            "individual_position": self.puuid_of_reference_individual_position,
            "team_position": self.puuid_of_reference_team_position,
            "game_length": self.game_length,
            "game_start_time": self.game_start_time,
            "gameType": self.gameType,
            "mapId": self.mapId,
            "championId": self.championId
        }