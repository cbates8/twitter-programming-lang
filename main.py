from searchtweets import ResultStream, gen_request_parameters, load_credentials
import json

# currently will print all programming languages from dataset
def GenQuery():
    file = open("All_Programming_Languages.json","r")
    info = file.read()
    languages = json.loads(info)
    for language in languages["results"]:
        print(language["ProgrammingLanguage"])

def main():
    search_args = load_credentials(".twitter_keys.yaml",
                                        yaml_key="search_tweets_v2",
                                        env_overwrite=False)

    query = gen_request_parameters("(favorite programming language) -is:retweet", granularity=False, results_per_call=10)
    print(query)

    rs = ResultStream(request_parameters=query,
                    max_results=10,
                    max_pages=1,
                    **search_args)

    print(rs)

    tweets = list(rs.stream())
    # using unidecode to prevent emoji/accents printing
    [print(tweet) for tweet in tweets[0:10]]

if __name__ == "__main__":
    GenQuery()