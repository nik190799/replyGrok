# Importing Modules/Libraries
import tweepy
import time
import os
import re
import requests
import json
import openai
from datetime import datetime

# Credentials (Insert your keys and tokens below)
api_key = ""
api_secret = ""
bearer_token = ""
access_token = ""
access_token_secret = ""

def xApi():
    client = tweepy.Client(
        bearer_token,
        api_key,
        api_secret,
        access_token,
        access_token_secret,
        wait_on_rate_limit=True,
    )
    return client

def extractTextAndUrl(text):
    url_pattern = r'https?://\S+'
    urls = re.findall(url_pattern, text)
    for url in urls:
        text = text.replace(url, '')
    return text, urls

def get_quote_tweet_id(shortened_url):
    try:
        response = requests.head(shortened_url, allow_redirects=True)
        final_url = response.url
        return final_url.split('/')[-1]
    except requests.RequestException as e:
        print(f"Error expanding URL: {e}")
        return None
    
def get_entire_quoted_tweets(tweet_text):
    api = xApi()
    observed_ids = set()
    texts = []
    text, urls = extractTextAndUrl(tweet_text)
    texts.append(text)
    # for url in urls:
    #     print(text, url)
    #     while url != "":
    #         tweet_id = get_quote_tweet_id(url)
    #         if tweet_id in observed_ids:
    #             continue
    #         inner_text, inner_urls = extractTextAndUrl(api.get_tweet(tweet_id).data.text)
    #         texts.append(inner_text)
    #         observed_ids.add(tweet_id)
    #         print(text, url)
    print(texts)

def gptModifyer(news_text: str):
    messages = ""
    path = "C:/Users/16823/Documents/X/replyGrok/response.json"
    if os.path.exists(path):
        with open(path, 'r', encoding="utf8") as f:
            messages = json.load(f)
    response = openai.ChatCompletion.create(model="gpt-4",messages = messages + [{"role": "user", "content": news_text}]).choices[0].message.content
    print("Response: " + response)
    return response


def reply():
    api = xApi()
    client_id = api.get_me().data.id
    mentions = api.get_users_mentions(id = client_id, max_results = 5)

    for mention in mentions.data:
        if mention.text.count('@') <= 2:
            text, urls = extractTextAndUrl(mention.text)
            reply_text = gptModifyer(text + " /ego_50 /sarcasm_100")
            api.create_tweet(text = reply_text, in_reply_to_tweet_id = mention.id)
            break

def lambda_handler(event, context):
    reply()
    return {
        'statusCode': 200,
        'body': json.dumps("Done")
    }