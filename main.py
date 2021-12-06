from nltk import collocations
from searchtweets import ResultStream, gen_request_parameters, load_credentials
import json, nltk
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re

# currently will print all programming languages from dataset
def GenQuery():
    file = open("All_Programming_Languages.json","r")
    info = file.read()
    languages = json.loads(info)
    #for language in languages["results"]:
        #print(language["ProgrammingLanguage"])
    return [lang["ProgrammingLanguage"] for lang in languages["results"]]

def main():

    # create stopword list
    stopwords = nltk.corpus.stopwords.words("english")

    search_args = load_credentials(".twitter_keys.yaml",
                                        yaml_key="search_tweets_v2",
                                        env_overwrite=False)

    query = gen_request_parameters("(favorite programming language) -is:retweet -has:media", granularity=False, results_per_call=10)
    #print(f"Query:\n{query}\n\n")

    rs = ResultStream(request_parameters=query,
                    max_results=10,
                    max_pages=1,
                    **search_args)

    #print(f"\n{rs}\n")

    #print("Tweets:\n")
    all_tweets = list(rs.stream())

    # using unidecode to prevent emoji/accents printing
    tweets = {}

    languages = {}

    all_languages = ""

    for data in all_tweets[0:10]:
        for tweet in list(dict(data)["data"]):
            t = dict(tweet)
            wrds = t["text"].replace("“", "")
            wrds = wrds.replace("?", "")
            wrds = re.split('\n |\ |, |\*|\n', wrds)
            #print(wrds)
            words = [w for w in wrds if w.lower() not in stopwords and "http" not in w]
            tweets[t["id"]] = " ".join(words)
            #print(t["id"])
            #print(t["text"], " ".join(words), "\n")
            for lang in GenQuery():
                if lang in wrds or lang.lower() in wrds:
                    all_languages += f" {lang} "
                    if lang not in languages.keys():
                        languages[lang] = " ".join(words)
                    else:
                        languages[lang] += f" {' '.join(words)} "

    #print(len(tweets))
    all_words = " ".join([tweets[t] for t in tweets.keys()])
    
    wordcloud = WordCloud()

    # Wordcloud for all tweets
    print("Generating wordcloud for all tweets...")
    wordcloud.generate(all_words)
    plt.figure(figsize= (8, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig("./figures/All_Tweets_Wordcloud.png")
    print("Saved as 'All_Tweets_Wordcloud.png'\n")

    # WordCloud for only language references
    print("Generating wordcloud for only language references...")
    all_languages = all_languages.replace("C++", "Cpp")
    #print(all_languages)
    wordcloud.generate(all_languages)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig("./figures/All_Language_Wordcloud.png")
    print("Saved as 'All_Language_Wordcloud.png'\n")

    # WordCloud for specific languages
    print("Generating wordcloud for individual languages...")
    for lang in GenQuery():
        if lang in languages.keys():
            words = languages[lang].replace("C++", "Cpp")
            wordcloud.generate(words)
            #print(lang, "\n", words, "\n\n")
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis("off")
            plt.savefig(f"./figures/{lang}_Wordcloud.png")
            print(f"Saved as '{lang}_Wordcloud.png'\n")


if __name__ == "__main__":
    #GenQuery()
    main()