import lol_match_predictor

def main():
    summoner = None
    try:
        summoner = lol_match_predictor.Summoner("GiveMeDaTaco", "summonerName")
        summoner.get_summoner()
        summoner.get_matches()
        df = summoner.matches_to_df()
    except Exception as e:
        print(e)
        return summoner

if __name__ == "__main__":
    main()
