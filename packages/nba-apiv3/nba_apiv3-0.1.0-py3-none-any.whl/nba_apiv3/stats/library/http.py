import json
from nba_apiv3.library import http
from nba_apiv3.stats.library.parser import (NBAStatsBoxscoreParserV3,
                                            NBAStatsBoxscoreTraditionalParserV3,
                                            NBAStatsBoxscoreMatchupsParserV3,
                                            NBAStatsPlayByPlayParserV3)

PARSER_DICT = {
    'boxscoreadvancedv3': NBAStatsBoxscoreParserV3,
    'boxscoredefensivev2': NBAStatsBoxscoreParserV3,
    'boxscorefourfactorsv3': NBAStatsBoxscoreParserV3,
    'boxscorehustlev2': NBAStatsBoxscoreParserV3,
    'boxscorematchupsv3': NBAStatsBoxscoreMatchupsParserV3,
    'boxscoremiscv3': NBAStatsBoxscoreParserV3,
    'boxscoreplayertrackv3': NBAStatsBoxscoreParserV3,
    'boxscorescoringv3': NBAStatsBoxscoreParserV3,
    'boxscoretraditionalv3': NBAStatsBoxscoreTraditionalParserV3,
    'boxscoreusagev3': NBAStatsBoxscoreParserV3,
    'playbyplayv3': NBAStatsPlayByPlayParserV3
}

try:
    from nba_apiv3.library.debug.debug import STATS_HEADERS
except ImportError:
    STATS_HEADERS = {
        'Host': 'stats.nba.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'x-nba-stats-origin': 'stats',
        'x-nba-stats-token': 'true',
        'Connection': 'keep-alive',
        'Referer': 'https://stats.nba.com/',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }


class NBAStatsParser:

    def __init__(self, nba_dict):
        self.nba_dict = nba_dict

    def change_parser(self, endpoint):
        return PARSER_DICT[endpoint](self.nba_dict)


class NBAStatsResponse(http.NBAResponse):

    def __init__(self, response, status_code, url):
        super().__init__(response, status_code, url)
        self.parser = NBAStatsParser(nba_dict=self.get_dict())

    def get_normalized_dict(self):
        pass

    def get_normalized_json(self):
        pass

    def get_parameters(self):
        if not self.valid_json() or 'parameters' not in self.get_dict():
            return None

        parameters = self.get_dict()['parameters']
        if isinstance(parameters, dict):
            return parameters

        parameters = {}
        for parameter in self.get_dict()['parameters']:
            for key, value in parameter.items():
                parameters.update({key: value})
        return parameters

    def get_headers_from_data_sets(self):
        raw_dict = self.get_dict()
        if 'resultSets' in raw_dict:
            results = raw_dict['resultSets']
        else:
            results = raw_dict['resultSet']
        if isinstance(results, dict):
            if 'name' not in results:
                return {}
            return {results['name']: results['headers']}
        return {result_set['name']: result_set['headers'] for result_set in results}

    def get_data_sets(self, endpoint):
        data = self.parser.change_parser(endpoint)
        return data.get_data_sets()


class NBAStatsHTTP(http.NBAHTTP):

    nba_response = NBAStatsResponse

    base_url = 'https://stats.nba.com/stats/{endpoint}'

    headers = STATS_HEADERS

    def clean_contents(self, contents):
        if '{"Message":"An error has occurred."}' in contents:
            return '<Error><Message>An error has occurred.</Message></Error>'
        return contents
