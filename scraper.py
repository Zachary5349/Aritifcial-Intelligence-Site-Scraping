from twikit import Client
import datetime
import pandas as pd
import asyncio
import pypyodbc as odbc

# first we need to initialize the twikit client
client = Client('en-US')


# datefix: a function to convert the dates from the 3 letter abbreviation to a numerical value.
def datefix(date_in):
    month_part = date_in[4:7]

    match month_part:
        case "Jan":
            new_month_part = "01"
        case "Feb":
            new_month_part = "02"
        case "Mar":
            new_month_part = "03"
        case "Apr":
            new_month_part = "04"
        case "May":
            new_month_part = "05"
        case "Jun":
            new_month_part = "06"
        case "Jul":
            new_month_part = "07"
        case "Aug":
            new_month_part = "08"
        case "Sep":
            new_month_part = "09"
        case "Oct":
            new_month_part = "10"
        case "Nov":
            new_month_part = "11"
        case "Dec":
            new_month_part = "12"

    # construct a new date from the parts:
    new_date = date_in[26:] + "-" + new_month_part + "-" + date_in[8:10] + " " + date_in[11:19]

    return(new_date)

def count(elements):
    # check if each word has '.' at its last. If so then ignore '.'
    if elements[-1] == '.':
        elements = elements[0:len(elements) - 1]

    # if there exists a key as "elements" then simply
    # increase its value.
    if elements in dictionary:
        dictionary[elements] += 1

    # if the dictionary does not have the key as "elements"
    # then create a key "elements" and assign its value to 1.
    else:
        dictionary.update({elements: 1})




#run the main asynchronously, so it can wait for twitter to respond with the data
async def main ():
    # run this once to login and get your authorization cookie.  Don't run it too often or you may trip some spamming alerts.
    #await client.login(auth_info_1='GregBowden29661', auth_info_2='gregbowden22@outlook.com', password='B1gmails!')
    #client.save_cookies('cookies.json')


    # load previously saved authorization cookie
    client.load_cookies(path='cookies.json')

    # await asynchronously for response from twitter/X
    user = await client.get_user_by_screen_name('hp')
    tweets = await user.get_tweets('Tweets', count=200)

    # create a list to store our tweets
    tweets_to_store = []

    #check for retweets
    for tweet in tweets:
        if tweet.full_text[0:4] == 'RT @':
            is_a_retweet = "Y"
        else:
            is_a_retweet = "N"

        # get full text of tweet
        punct_string = tweet.full_text
        #create version with punctuation removed
        no_punct_string = "".join(c for c in punct_string if c not in ('!', '.', ':', '?', ',', '"'))

        #split out the individual words
        tweet_list = no_punct_string.split()


        # add the words from each tweet to the count dictionary
        for elements in tweet_list:
            count(elements)

        tweets_to_store.append({
            'tweet_id': tweet.id,
            'created_at': datefix(tweet.created_at),
            'favorite_count': tweet.favorite_count,
            'full_text': tweet.full_text,
            'view_count': tweet.view_count,
            'reply_count': tweet.reply_count,
            'retweet_count': tweet.retweet_count,
            'is_retweet': is_a_retweet

        })


    # request and wait for a second batch of tweets
    more_tweets = await tweets.next()
    for tweet in more_tweets:
        if tweet.full_text[0:4] == 'RT @':
            is_a_retweet = "Y"
        else:
            is_a_retweet = "N"

        tweets_to_store.append({
            'tweet_id': tweet.id,
            'created_at': datefix(tweet.created_at),
            'favorite_count': tweet.favorite_count,
            'full_text': tweet.full_text,
            'view_count': tweet.view_count,
            'reply_count': tweet.reply_count,
            'retweet_count': tweet.retweet_count,
            'is_retweet': is_a_retweet
        })

    # set filename and a timestamp for the output .csv file.
    # we don't really need the csv to create the Tableau, since it pulls from the SQL server,
    # but we'll save a snapshot for debugging and troubleshooting purposes.  Plus an archive just in case.
    filename = "twitter_test_hp"
    now = datetime.datetime.now()
    file_timestamp = now.strftime("%Y%m%d-%H-%M-%S.%f")
    complete_filename = filename + "-" + file_timestamp + ".csv"

    #save the file
    df = pd.DataFrame(tweets_to_store)
    df.to_csv(complete_filename, index=False)

    #set the server and database name of the SQL server (SQL Express instance 1on local PC in this case)
    DRIVER_NAME = 'SQL SERVER'
    SERVER_NAME = 'DESKTOP-8EVQMO6\SQLEXPRESS'
    DATABASE_NAME = 'hp_test'

    # setup the connection string for the SQL server
    connection_string = f"""
            DRIVER={{{DRIVER_NAME}}};
            SERVER={SERVER_NAME};
            DATABASE={DATABASE_NAME};
            Trust_Connection=yes;
        """

    # connect to database via ODBC, using pypyodbc
    conn = odbc.connect(connection_string)

    cursor = conn.cursor()

    # fill dataframe elements with default values, so as to not upset the SQL server with #NAs
    df['tweet_id'] = df['tweet_id'].fillna(0)
    df['created_at'] = df['created_at'].fillna(0)
    df['favorite_count'] = df['favorite_count'].fillna(0)
    df['full_text'] = df['full_text'].fillna("")
    df['view_count'] = df['view_count'].fillna(0)
    df['reply_count'] = df['reply_count'].fillna(0)
    df['retweet_count'] = df['retweet_count'].fillna(0)
    df['is_retweet'] = df['is_retweet'].fillna("N")

    # iterate through the rows, insert into the database table
    for index, row in df.iterrows():
        cursor.execute(
            "INSERT INTO tweets_hp (tweet_id, created_at, favorite_count, full_text, view_count, reply_count, retweet_count, is_retweet) values(?,?,?,?,?,?,?,?)",
            (row.tweet_id, row.created_at, row.favorite_count, row.full_text, row.view_count, row.reply_count,
             row.retweet_count, row.is_retweet))

    # commit the updates to the database and close it
    conn.commit()
    cursor.close()


    # report the frequency of each word in the batch of tweets.
    # first sort the dictionary by the values, in descending order
    sorted_dictionary = {k: v for k, v in sorted(dictionary.items(), key=lambda x: x[1], reverse = True)}

    # now print
    for keys in sorted_dictionary:
        print(f"Frequency of {keys} : {sorted_dictionary[keys]}")

# create empty dictionary for counting the frequency of words
dictionary = {}

#run main asynchronously
asyncio.run(main())
