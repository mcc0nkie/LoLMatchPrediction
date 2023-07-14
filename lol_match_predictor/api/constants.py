import pwinput

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

_RIOT_API_KEY = "RGAPI-ececaadd-2cde-4cda-af88-f7f3760ae59a"
    