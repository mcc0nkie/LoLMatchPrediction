_RIOT_API_KEY = "RGAPI-055e5419-3b7c-432f-9364-49a0d983ae17"
import lol_match_predictor

def main():
    summoner = lol_match_predictor.Summoner("GiveMeDaTaco", "summonerName")
    summoner.get_summoner()
    summoner.get_matches()
    df = summoner.matches_to_df()

if __name__ == "__main__":
    main()
