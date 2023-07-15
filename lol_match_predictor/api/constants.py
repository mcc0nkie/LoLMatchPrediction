import os

_API_ENDPOINTS = {
    "SUMMONER-V4": {
        "encryptedPUUID": "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{identifier}",
        "summonerName": "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{identifier}",
        "encryptedSummonerId": "https://na1.api.riotgames.com/lol/summoner/v4/summoners/{identifier}"
    },
    "MATCH-V5": {
        "puuid": "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids",
        "matchId": "https://americas.api.riotgames.com/lol/match/v5/matches/{matchId}"
    }
}

_RIOT_API_KEY = os.getenv('_RIOT_API_KEY')
    