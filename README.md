# README

## Objective

The objective is to calculate the win rate on multiple levels for a summoner in League of Legends game. Riot has repeated over and over again that they pair up players in a way that *only* considers their winrate; thus, they should have an equal win rate. We're going to test that. 


## Metrics to Measure
For every summoner in a single ranked game, we are going to calculate the following metrics:
- overall ranked win rate
- overall champion win rate
- overall position win rate

These calculations will be done for the following periods:
- Lifetime
- Current season
- Last 50 games

We will use this criteria to filter the matches:
- Only use ranked and draft games on Summoner's Rift
- No remakes

## Predicting Wins and Losses
Riot may use additional criteria when filtering for win rates (i.e. dropping games with AFKs, etc.), but we don't want to risk tapering down the data too much. 

For our intents and purposes, we'll attempt to predict which team will win, solely based on win rate. If Riot solely balances on win rate, we expect to have around 50% accuracy in predicting the outcome of a match. 

If we find our accuracy too far below 50%, there are two possible conclusions:
1. There are more factors at play than just win rate.
2. Our method for measuring win rate does not reflect Riot's method (although, we can't imagine it would look much different than what we've alreaady done above)

If we find our accuracy too far above 50%, there are 3 possible conclusions:
1. Riot is purposefully fixing matches
2. Riot's method for measuring win rate is simpler than ours, and therefore a less accurate way to guaruntee a fair match
3. Riot uses a completely different method for matchmaking, which would be a low-quality method, since we can accurately predict match outcomes with just win rates (this is an unlikely conclusion, since Riot has stated over and over that matchmaking is based on win rate)