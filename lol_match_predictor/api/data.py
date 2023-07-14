import numpy as np
import pandas as pd
from lol_match_predictor.api.constants import _API_ENDPOINTS, _RIOT_API_KEY
from lol_match_predictor.api.rate_limiter import RateLimitedAPI

ratelimiter = RateLimitedAPI()

class SummonerList:
    def __init__(self, matchId):
        self.matchId = matchId
        self._api_endpoint = _API_ENDPOINTS["MATCH-V5"]["matchId"].format(matchId=self.matchId)
        self.summoner_list = None
        self.bad_response = None
        self.summoner_data_list = []
    
    def get_summoners_from_match(self):
        params = {
            'api_key': _RIOT_API_KEY
        }
        response = ratelimiter(self._api_endpoint, params=params, name="Retrieving Summoners from Match", total=10)
        if response.status_code != 200:
            self.bad_response = response
            raise ValueError(f"Error code {response.status_code} returned from Riot API; you may look the .bad_response attribute of this object for more information.")
        self.summoner_list = response.json()['metadata']['participants']
    
    def get_summoner_data(self):
        if self.summoner_list is None:
            raise ValueError("You must call get_summoners_from_match() before calling get_summoner_data().")
        for summoner in self.summoner_list:
            summoner_obj = Summoner(summoner['puuid'], "encryptedPUUID")
            summoner_obj.get_summoner()
            summoner_obj.get_matches()
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
        response = ratelimiter(self._api_endpoint, params=params, name="Retrieving Summoner")
        if response.status_code == 200:
            response_json = response.json()
            # parse the response
            self.id = response_json.get("id", None)
            self.accountId = response_json.get("accountId", None)
            self.puuid = response_json.get("puuid", None)
            self.name = response_json.get("name", None)
            self.profileIconId = response_json.get("profileIconId", None)
            self.revisionDate = response_json.get("revisionDate", None)
            self.summonerLevel = response_json.get("summonerLevel", None)
        else:
            self.bad_response = response
            raise ValueError(f"Error code {response.status_code} returned from Riot API; you may look at the .bad_response attribute of this object for more information.")
        
        return response.json()
    
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
            'start': 0,
            'api_key': _RIOT_API_KEY
        }

        self.all_ranked_matches = []

        while True:  
            params['start'] = len(self.all_ranked_matches) 
            response = ratelimiter(self._api_endpoint, params=params, name="Querying Match List") 

            if response.status_code != 200:
                self.bad_response = response
                raise ValueError(f"Error code {response.status_code} returned from Riot API; you may look the .bad_response attribute of this object for more information.")

            response_json = response.json()

            if not response_json:
                break

            self.all_ranked_matches.extend(response_json)

        self.all_ranked_matches = np.unique(self.all_ranked_matches)
        print(f"Found {len(self.all_ranked_matches)} matches.")
        return self.all_ranked_matches
    
    def get_match_data(self):
        self.all_ranked_matches_collection = []

        for matchId in self.all_ranked_matches:
            match = Match(matchId, self.puuid, len(self.all_ranked_matches))
            match.get_match()
            self.all_ranked_matches_collection.append(match)

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
        self.match_data = None
        self.bad_response = None
        self.puuid_of_reference = puuid_of_reference    
        self.puuid_of_reference_role = None
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
        response = ratelimiter(self._api_endpoint,  params=params, name="Downloading Match Data", total=self.num_of_matches_in_batch)      

        if response.status_code != 200:
            self.bad_response = response
            raise ValueError(f"Error code {response.status_code} returned from Riot API; you may look the .bad_response attribute of this object for more information.")
        
        response_json = response.json()

        for participant in response_json["info"]["participants"]:
            if participant["puuid"] == self.puuid_of_reference:
                self.puuid_of_reference_role = participant['individualPosition']
                self.puuid_of_reference_won = participant['win']
                self.game_length = response_json["info"]["gameDuration"]
                self.game_start_time = response_json["info"]["gameStartTimestamp"]
                self.gameType = response_json["info"]["gameType"]
                self.mapId = response_json["info"]["mapId"]
                self.championId = participant["championId"]
                break  # Stop the loop as soon as we find the participant

        
        # winning_team = next(team for team in response_json['teams'] if team['win'])

        # player = next(participant for participant in response_json['participants'] if participant['puuid'] == self.puuid_of_reference)

        # if winning_team == player['teamId']:
        #     self.puuid_of_reference_won = True 
        # else:
        #     self.puuid_of_reference_won = False

        # self.puuid_of_reference_role = player['individualPosition']
        
        return self.match_data
    
    def __dict__(self):
        return {
            "matchId": self.matchId,
            "puuid_of_reference": self.puuid_of_reference,
            "won": self.puuid_of_reference_won,
            "role": self.puuid_of_reference_role,
            "game_length": self.game_length,
            "game_start_time": self.game_start_time,
            "gameType": self.gameType,
            "mapId": self.mapId,
            "championId": self.championId
        }