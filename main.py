from searchtweets import ResultStream, gen_request_parameters, load_credentials
import json, nltk
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# currently will print all programming languages from dataset
def GenQuery():
    file = open("All_Programming_Languages.json","r")
    info = file.read()
    languages = json.loads(info)
    for language in languages["results"]:
        print(language["ProgrammingLanguage"])

def main():

    # create stopword list
    stopwords = nltk.corpus.stopwords.words("english")

    search_args = load_credentials(".twitter_keys.yaml",
                                        yaml_key="search_tweets_v2",
                                        env_overwrite=False)

    query = gen_request_parameters("(favorite programming language) -is:retweet", granularity=False, results_per_call=10)
    print(f"Query:\n{query}\n\n")

    rs = ResultStream(request_parameters=query,
                    max_results=10,
                    max_pages=1,
                    **search_args)

    print(f"\n{rs}\n")

    print("Tweets:\n")
    all_tweets = list(rs.stream())

    # using unidecode to prevent emoji/accents printing
    tweets = {}

    for data in all_tweets[0:10]:
        for tweet in list(dict(data)["data"]):
            t = dict(tweet)
            words = [w for w in t["text"].split() if w.lower() not in stopwords]
            tweets[t["id"]] = " ".join(words)
            print(t["id"])
            print(t["text"], " ".join(words), "\n")
    
    wordcloud = WordCloud()
    wordcloud.generate(tweets["1465246272399499267"])
    
    plt.figure(figsize= (8, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()

if __name__ == "__main__":
    #GenQuery()
    main()