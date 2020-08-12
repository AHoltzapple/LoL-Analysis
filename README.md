# LoL-Analysis
## Analysis of League of Legends match data

League of Legends is a popular multiplayer online battle area (MOBA) game in which 10 players compete to destroy the other team's base. Players choose (or are assigned) a champion character to play as. They may also choose 2 special abilites and other passive perks that enhance their champion or team's capabilities. In-game, players use gold, earned over time and by achieving kills or assists, to purchase items that further enhnace their abilities.

Check it out here: [League of Legends Homepage](https://na.leagueoflegends.com/en-us/)

With seemingly unending combinations of teammates, champions, abilities, perks, and items, League of Legends matches contain a wealth of interesting statistics regarding a player's performance. The goal of this project is to retrieve my personal match data and explore any trends in my performance across champion types. Ideally this information would help increase my chances of winning a match by understanding which champions I should favor and which I should avoid.

## Files:

* 'lolapi.py' - Python library to collect the match data from the Riot Games API.
* 'full_aram_data.csv' - Result data collected.
* 'aram_analysis.ipynb' - Analysis of match data.

## Data Collection:

The data for this project was collected through the Riot Game API. Riot has provided their API for public use, although with some restrictions, allowing players to access their data. More information about the Riot Games API can be found on their developer website: [Riot Developer Portal](https://developer.riotgames.com/)

I wrote the library `lolapi` with a collection of functions to easily retrieve data from the API. The functions used are described in detail below:

Other libraries used:
* `json`
* `time`
* `requests`
* `pandas`

`retrieve_accountid`:

Inputs: apikey (str), summonername (str)

Output: Encrypted account ID (str)

To retrieve specific match data, Riot requires making calls using an encrypted account ID. This is a different ID than a player's in-game name (also called 'summoner name'). The API has an operation that returns the encrypted account ID based on the public summoner name. This function takes the user's personal API key and desired summoner name, returning their encrypted account ID as a string.

`retrieve_account_matches`:

Inputs: apikey (str), accountid (str), queue (int, default = None)

Output: Dataframe of account matches

Detailed match data cannot be retrieved directly using account ID. Instead, users must retrieve matches associated to their account, then use the resulting match IDs to retrieve detail data on a per-match basis. This function uses the encrypted account ID to collect all matches. The call can be filtered by 'queue' or game mode. Riot's API limits responses to this call to a length of 100 matches. The function 'paginates' the call to collect all matches. Retrieving a large number of matches may result in a long run time. The output is a dataframe of basic match data including the match IDs.

* `retrieve_match_data`:
Inputs: apikey (str), gameids (list or pandas.Series)
Output: List format of detailed data per match

This function makes a call for each 'gameId' in the `gameids` input. The input should be the list or series of the IDs returned by the `retrieve_account_matches` function. The Riot API has a call limit on public accounts of 100 requests every 2 minutes. This limit is quickly reached when retrieving data for over 100 matches. The function accounts for this and will pause for 2 minutes when it receives a resource limit error response from the API, it will then re-try the last call. The call retrieves the full response with all match data provided by the API. The output is a list containing the raw response for each match.

* `parse_match_data`:
Inputs: summonername (str), raw_match_data_list (list)
Output: Dataframe of detailed match data

This function parses the detail match data retrieved from `retrieve_match_data`. It does not output all match data, only some overall information and the available data points for the given summoner name. Further match data can still be parsed from the `retrieve_match_data` output. The output for this function is a dataframe.

* `retrieve_champ_info`:
Inputs: None
Output: Dataframe of champion information

Some champion specific information is not available directly in match data. This function calls the API for champion information to merge into the dataframe created prior. It collects only overall information such as the champion's main role and base ratings for 'attack', 'defense', 'magic', and 'difficulty'. Specific statistics such as damage or health amounts change throughout a match based on items and other enhnacements.
