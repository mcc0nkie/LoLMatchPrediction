import pwinput

_API_ENDPOINTS = {
    "SUMMONER-V4": {
        "rsoPUUID": "https://na1.api.riotgames.com/lol/fulfillment/v1/summoners/by-puuid/{identifier}",
        "summonerName": "https://na1.api.riotgames.com/lol/lol/summoner/v4/summoners/by-name/{identifier}",
        "encryptedSummonerId": "https://na1.api.riotgames.com/lol/lol/summoner/v4/summoners/{identifier}"
    },
    "MATCH-V5": {
        "puuid": "https://americas.api.riotgames.com/lol/lol/match/v5/matches/by-puuid/{puuid}/ids",
        "matchId": "https://americas.api.riotgames.com/lol/lol/match/v5/matches/{matchId}"
    }
}

_RIOT_API_KEY = "RGAPI-055e5419-3b7c-432f-9364-49a0d983ae17"
    