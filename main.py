'''
Casey Bates and Luke Manzitto
CSCI 182
'''
from searchtweets import ResultStream, gen_request_parameters, load_credentials
from nltk.sentiment import SentimentIntensityAnalyzer
import json, nltk
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

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

    query = gen_request_parameters("(favorite programming language) -is:retweet lang:en", granularity=False, results_per_call=100)
    all_tweets = []
    rs = ResultStream(request_parameters=query,
                    max_results=100,
                    max_pages=10,
                    **search_args)
    all_tweets = list(rs.stream())
    query = gen_request_parameters("(worst programming language) -is:retweet lang:en", granularity=False, results_per_call=100)
    rs = ResultStream(request_parameters=query,
                    max_results=100,
                    max_pages=10,
                    **search_args)
    all_tweets = all_tweets + list(rs.stream())
    tweets = {}

    languages = {}

    all_languages = ""

    for data in all_tweets[0:100]:
        for tweet in list(dict(data)["data"]):
            t = dict(tweet)
            words = nltk.word_tokenize(t["text"])
            tweets[t["id"]] = " ".join(words)
            for lang in GetLanguages():
                if lang in words or lang.lower() in words:
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
    df = pd.DataFrame.from_dict(sia_scores)
    print("Creating polarity score csv...")
    df.to_csv("./polarity_scores.csv")

    vals = []
    for lang in languages.keys():
        if lang in sia_scores.keys():
            vals.append(sia_scores[lang]["compound"])

    plt.figure(figsize=(20,8))
    ax = plt.axes()
    ax.bar(sia_scores.keys(),vals,width=0.6)
    plt.tight_layout()
    plt.savefig(f"./polarity_scores.png")
    print(f"Saved as 'polarity_scores.png'\n")

    for data in all_tweets[0:10]:
        for tweet in list(dict(data)["data"]):
            t = dict(tweet)
            wrds = nltk.word_tokenize(t["text"])
            words = [w for w in wrds if (w.isalpha() or 'C++' in w or 'C#' in w) and w.lower() not in stopwords and "http" not in w]
            tweets[t["id"]] = words
            for lang in GetLanguages():
                if lang in words or lang.lower() in words:
                    all_languages += f" {lang} "
                    if lang not in languages.keys():
                        languages[lang] = " ".join(words)
                    else:
                        languages[lang] += f" {' '.join(words)} "

    all_words = []
    for t in tweets.keys():
        for w in tweets[t]:
            all_words.append(w)

    wordcloud = WordCloud(collocations=False)

    # Wordcloud for all tweets
    print("Generating wordcloud for all tweets...")
    all_words = " ".join(all_words)
    all_words = all_words.replace("C++", "Cpp")
    all_words = all_words.replace("C#", "Csharp")
    wordcloud.generate(all_words)
    plt.figure(figsize= (8, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig("./figures/All_Tweets_Wordcloud.png")
    print("Saved as 'All_Tweets_Wordcloud.png'\n")

    # WordCloud for only language references
    print("Generating wordcloud for only language references...")
    all_languages = all_languages.replace("C++", "Cpp")
    all_words = all_words.replace("C#", "Csharp")
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