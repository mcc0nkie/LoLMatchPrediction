_API_ENDPOINTS = {
    "SUMMONER-V4": {
        "rsoPUUID": "/fulfillment/v1/summoners/by-puuid/{identifier}",
        "summonerName": "/lol/summoner/v4/summoners/by-name/{identifier}",
        "encryptedSummonerId": "/lol/summoner/v4/summoners/{identifier}"
    },
    "MATCH-V5": {
        "puuid": "/lol/match/v5/matches/by-puuid/{puuid}/ids",
        "matchId": "/lol/match/v5/matches/{matchId}"
    }
}

_RIOT_API_KEY = ""  # Your API key here