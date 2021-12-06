from searchtweets import ResultStream, gen_request_parameters, load_credentials
from nltk.sentiment import SentimentIntensityAnalyzer
import json, nltk
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from wordcloud import WordCloud
import re


# currently will print all programming languages from dataset
def GetLanguages():
    file = open("All_Programming_Languages.json","r")
    info = file.read()
    file.close()
    languages = json.loads(info)
    return [lang["ProgrammingLanguage"] for lang in languages["results"]]

def main():

    # create stopword list
    stopwords = nltk.corpus.stopwords.words("english")

    search_args = load_credentials(".twitter_keys.yaml",
                                        yaml_key="search_tweets_v2",
                                        env_overwrite=False)

    query = gen_request_parameters("(favorite programming language) -is:retweet -has:media", granularity=False, results_per_call=10)

    rs = ResultStream(request_parameters=query,
                    max_results=10,
                    max_pages=1,
                    **search_args)

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
            words = [w for w in wrds]
            tweets[t["id"]] = " ".join(words)
            for lang in GetLanguages():
                if lang in wrds or lang.lower() in wrds:
                    all_languages += f" {lang} "
                    if lang not in languages.keys():
                        languages[lang] = " ".join(words)
                    else:
                        languages[lang] += f" {' '.join(words)} "
    sia = SentimentIntensityAnalyzer()
    print("Generating Sentiment Polarity Scores for languages...")
    sia_scores = {}
    for key,value in languages.items():
        sia_scores[key] = sia.polarity_scores(value)
    xValues = []
    yValues = []
    zValues = []
    for lang in languages.values():
        if lang in sia_scores.keys():
            xValues.append(sia_scores[lang]["neg"])
            yValues.append(sia_scores[lang]["neu"])
            zValues.append(sia_scores[lang]["pos"])
    x = np.array(xValues)
    y = np.array(yValues)
    z = np.array(zValues)

    plt.figure(figsize=(8,8))
    ax = plt.axes(projection="3d")
    ax.scatter(x,y,z)
    plt.savefig(f"./polarity_scores.png")
    print(f"Saved as 'polarity_scores.png'\n")

    for data in all_tweets[0:10]:
        for tweet in list(dict(data)["data"]):
            t = dict(tweet)
            wrds = t["text"].replace("“", "")
            wrds = wrds.replace("?", "")
            wrds = re.split('\n |\ |, |\*|\n', wrds)
            words = [w for w in wrds if w.lower() not in stopwords and "http" not in w]
            tweets[t["id"]] = " ".join(words)
            for lang in GetLanguages():
                if lang in wrds or lang.lower() in wrds:
                    all_languages += f" {lang} "
                    if lang not in languages.keys():
                        languages[lang] = " ".join(words)
                    else:
                        languages[lang] += f" {' '.join(words)} "

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
    wordcloud.generate(all_languages)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig("./figures/All_Language_Wordcloud.png")
    print("Saved as 'All_Language_Wordcloud.png'\n")

    # WordCloud for specific languages
    print("Generating wordcloud for individual languages...")
    for lang in GetLanguages():
        if lang in languages.keys():
            words = languages[lang].replace("C++", "Cpp")
            wordcloud.generate(words)
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis("off")
            plt.savefig(f"./figures/{lang}_Wordcloud.png")
            print(f"Saved as '{lang}_Wordcloud.png'\n")


if __name__ == "__main__":
    main()