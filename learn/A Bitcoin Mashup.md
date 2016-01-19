[![21.co](https://assets.21.co/shared/img/21logo.png)21 Inc][0]

* [Setup][1]
* [Tutorials][2]
* [Buy][3]
* [Community][4]
* [Nodes][5]
* [About][6]

* [A Bitcoin Mashup as a Digital Supply Chain][7]
  * [Overview][8]
  * [Prerequisites][9]
  * [Step 1: Set up client, server, and server-2 accounts][10]
  * [Step 2: Set up the first server in the digital supply chain][11]
    * [Imgur][12]
    * [Twitter][13]
    * [Twilio][14]
  * [Step 3: Set up the second server in the digital supply chain][15]
  * [Step 4: Set up the client][16]
  * [Next Steps][17]
* [< Back To Index][18]

# A Bitcoin MashupPosted by
John Granata
  

* [A Bitcoin Mashup as a Digital Supply Chain][7]
  * [Overview][8]
  * [Prerequisites][9]
  * [Step 1: Set up client, server, and server-2 accounts][10]
  * [Step 2: Set up the first server in the digital supply chain][11]
    * [Imgur][12]
    * [Twitter][13]
    * [Twilio][14]
  * [Step 3: Set up the second server in the digital supply chain][15]
  * [Step 4: Set up the client][16]
  * [Next Steps][17]
* [< Back To Index][18]

# A Bitcoin Mashup as a Digital Supply Chain

## Overview

In this tutorial, you will compose _two_ bitcoin-payable APIs set up
by _different_ users to get a sense for what a machine-payable digital
supply chain might look like. The overall result for your customer
will be a service that accepts bitcoin to create unique,
location-based digital artwork and then sends this artwork to the
customer as an MMS message. We will build this in pieces.

* First, you will set up a micropayments server that turns a date
and location-specific search query into unique WordCloud art
composed of words from the most popular tweets that fit the search
parameters. The server will perform this service in exchange for a
small amount of bitcoin.
* 
Then, you'll set up a _second_ server under a _different user_
that charges bitcoin to send an MMS message to a provided phone
number.
* 
You will then compose these services to create a single
bitcoin-payable service for the end user. The end user doesn't care
about the implementation, but by using bitcoin in this fashion you
have suddenly built a digital supply chain.
* 
Specifically, the customer will send a request to the first server
to generate the WordCloud artwork in exchange for bitcoin, and then
this server will _subcontract_ the MMS task out to another server by
paying it some bitcoin to perform it's task, which is to send an MMS
with the artwork back to the customer.

This example illustrates how it is possible to build _digital supply
chains_ by composing bitcoin-payable APIs hosted by different users.

## Prerequisites

You will need the following first:

* A 21 Bitcoin Computer, with built-in mining and software
* The latest version of the 21 software, obtained by running `21
update` as described in the [setup][22] process.
* Do the [Introduction to the 21 Bitcoin Computer][23]
tutorial
* Do the [Working with Multiple 21 Users][24] tutorial
* Do the [Bitcoin-Payable API][25] tutorial
* Do the [Bitcoin SMS][26] tutorial

If you've done all that, you are ready to go. Let's get started!

## Step 1: Set up client, server, and server-2 accounts

Follow the instructions in the
[Working With Multiple 21 Users][24] tutorial to set
up the `twenty-client`, `twenty-server`, and `twenty-server-2` users
and install Flask.

## Step 2: Set up the first server in the digital supply chain

Log into the 21 Bitcoin Computer as the `twenty-server` user.

Install the packages we'll need for the demo:


    
    sudo apt-get -y install libjpeg-dev
    sudo apt-get -y install libfreetype6-dev
    sudo pip3 install geopy
    sudo pip3 install wordcloud
    sudo pip3 install numpy
    sudo pip3 install pillow
    sudo pip3 install imgurpython
    sudo pip3 install flask
    

In order to successfully run this demo, you will need API keys from the following services: imgur, twitter & twilio.
Before you proceed with the demo, please take a moment to go through this section to ensure you have all the necessary API keys. While the basic API signup procedure is similar across the 3 web services, the information below may help to reduce confusion when you register for your keys.

### Imgur

Go to [**Imgur**][35] and sign into your imgur account. Select `Register an Application` from the left-hand side menu. Ignore the `ERROR: Invalid Captcha` message when you first come to this page. It will disappear upon form submission provided the correct captcha is entered. Enter a name in the `Application Name` field, and for `Authorization Type`, select option 2 - **OAuth 2 authorization without a callback URL**. Upon completion of the signup, take note of your client ID and client secret.

### Twitter

Go to [**Twitter**][36] and sign in to your twitter account. Click on the **Create a new app** button to register your app. Enter a name and description for your app, and put `https://www.google.com` into the `Website` field for now. Upon completion of the signup, take note of your consumer key and consumer secret.

### Twilio

Go to [**Twilio**][37] to register your app and create a new API key. Click on the **Create an API Key** button. Enter the name of your app. Take note of the `Sid` and `Secret` on the next page. Select the check-box below `Secret` and click **Done**.

Click on **PHONE NUMBERS** at the top of the page and then select **Buy a number**. In the **Capabilities** field, make sure to select MMS. Click on **Search** to get a list of available numbers. Note the number you purchase along with the `Sid` and `Secret`.

Now you are ready to build the server side code for this demo. Create a project directory and a file called `supply-chain-server-1.py`:

    
    cd ~/
    mkdir twitter-wordcloud-server && cd twitter-wordcloud-server
    touch supply-chain-server-1.py
    

Edit the file in a text editor and add the following code:

    
    import base64
    import requests
    import urllib.parse
    
    from wordcloud import WordCloud
    from imgurpython import ImgurClient
    from geopy.geocoders import Nominatim
    from flask import Flask, request
    
    from two1.lib.wallet import Wallet
    from two1.commands.config import Config
    from two1.lib.bitserv.flask import Payment
    from two1.lib.bitrequests import BitTransferRequests
    
    # ---------------------------------- Setup ---------------------------------- #
    
    # Create application objects
    app = Flask(__name__)
    wallet = Wallet()
    payment = Payment(app, wallet)
    bit_requests = BitTransferRequests(wallet, Config().username)
    geolocator = Nominatim()
    
    # Create the Imgur API Client
    imgur_client = ImgurClient('<Your Imgur Client ID>', '<Your Imgur Client Secret>')
    
    # Create credentials for Twitter Search API
    concat = '<Twitter Consumer Key>' + ':' + '<Twitter Consumer Secret>'
    encoded = base64.b64encode(concat.encode('ascii'))
    
    # Obtain a Authorization Bearer token from Twitter
    headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
               'Authorization': 'Basic ' + encoded.decode()}
    response = requests.post('https://api.twitter.com/oauth2/token',
                             headers=headers, data='grant_type=client_credentials')
    bearer = response.json().get('access_token')
    
    # Define the API url and authentication headers for making calls later
    twitter_url = 'https://api.twitter.com/1.1/search/tweets.json?'
    twitter_headers = {'Authorization': 'Bearer ' + str(bearer)}
    
    # Define the 402-payable API url for sending multimedia text messages
    txt_msg_url = 'http://localhost:9000/send-mms?'
    
    # ------------------------------- API Routing ------------------------------- #
    
    
    @app.route('/wordcloud')
    @payment.required(1000)
    def get_word_cloud():
    
        # Extract and process query parameters from GET request
        zipcode = request.args.get('zipcode')
        query = request.args.get('query')
        date = request.args.get('date')
        phone = request.args.get('phone')
        radius = request.args.get('radius') or '5mi'
        location = geolocator.geocode(zipcode)
    
        # Twitter search query parameters
        params = dict(
            query=query,
            count=100,
            until=date,  # Format: YYYY-MM-DD (e.g. 2015-11-14)
            result_type='popular',  # Choices: (mixed | recent | popular)
            geocode=','.join([str(location.latitude), str(location.longitude), radius])
        )
    
        # Make a GET request to the Twitter API with the search parameters
        response = requests.get(twitter_url+'q={}&count={}&geocode={}'.format(
            params['query'], params['count'], params['geocode']), headers=twitter_headers)
        search_results = response.json()
    
        # Combine the all the status text into one variable
        all_text = ''
        for status in search_results['statuses']:
            all_text = all_text + status['text'][0:status['text'].find('http')] + ' '
    
        # Generate and save the word cloud
        wordcloud = WordCloud(max_words=150).generate(all_text)
        image = wordcloud.to_image()
        image.save('wordcloud_img.png')
    
        # Upload using the Imgur API
        print('Uploading image...')
        config = dict(title='Bitcoin-powered artwork!')
        img_url = imgur_client.upload_from_path('wordcloud_img.png', config=config)
        print('Uploaded to: {}'.format(img_url['link']))
    
        # Text the image to the user using a 402-payable API
        print('Call next link in digital supply chain: send text message')
        bit_requests.get(txt_msg_url + 'media={0}&phone={1}'.format(urllib.parse.quote_plus(img_url['link']), phone))
    
        return 'Text message sent.\n'
    
    if __name__ == '__main__':
        app.run(host='0.0.0.0')
    

Start the micropayments server:

    
    python3 supply-chain-server-1.py
    

The first server in our digital supply chain is up and running. Let's
set up another bitcoin-payable server to serve as the second link in
the chain.

## Step 3: Set up the second server in the digital supply chain

Open a new terminal and log into the Bitcoin Computer as the
`twenty-server-2` user. Then install the packages we'll need for the
second server:

    
    sudo pip3 install twilio
    sudo pip3 install flask
    

Next, create a project folder in the home directory to house our app
and create a file called `supply-chain-server-2.py`:

    
    cd ~/
    mkdir send-mms-server && cd send-mms-server
    touch supply-chain-server-2.py
    

Now open this file in a text editor and type in the following code:

    
    from twilio.rest import TwilioRestClient
    
    from flask import Flask
    from flask import request
    
    from two1.lib.wallet import Wallet
    from two1.lib.bitserv.flask import Payment
    
    app = Flask(__name__)
    wallet = Wallet()
    payment = Payment(app, wallet)
    
    # create the twilio rest client
    client = TwilioRestClient(
        '<Your Twilio Account SID>', '<Your Twilio Auth Token>'
    )
    
    @app.route('/send-mms')
    @payment.required(1000)
    def send_mms():
    
        phone = request.args.get('phone')
        media_link = request.args.get('media')
    
        print('Sending text message...')
        resp = client.messages.create(to='+'+str(phone),
                                      from_='<Your Twilio Account Phone Number>',
                                      body='Bitcoin-powered artwork from 21.co!',
                                      media_url=media_link
        )
    
        return "OK"
    
    if __name__ == '__main__':
        app.run(host='0.0.0.0',port=9000)
    

Replace `<Your Twilio Account Phone Number>` with your Twilio phone number, replace
`<Your Twilio Account SID>` with your Twilio account SID, and replace
`<Your Twilio Auth Token>` with your Twilio auth token.

Then start the micropayments server:

    
    python3 supply-chain-server-2.py
    

Now that both links in our digital supply chain are up, let's create a
client script to request the full service.

## Step 4: Set up the client

Finally, log into the 21 Bitcoin Computer as the `twenty-client` user.

We'll run a client script which prompts the user for some input and
sends this to our first server, effectively _piping_ it into the
machine-payable digital supply chain.

Create a folder in your home directory to house the client project:

    
    cd ~/
    mkdir bitcoin-mashup-client && cd bitcoin-mashup-client
    

In this directory, create a file called `client.py` and open it in
your editor. Add the following code to this file:

    
    import json
    import urllib.parse
    import os
    
    # import from the 21 Developer Library
    from two1.commands.config import Config
    from two1.lib.wallet import Wallet
    from two1.lib.bitrequests import BitTransferRequests
    
    wallet = Wallet()
    username = Config().username
    requests = BitTransferRequests(wallet, username)
    
    # merchant server address
    server_url = 'http://localhost:5000/'
    
    def get_art():
    
        print("--Generate bitcoin-powered digital artwork--")
    
        sel_url = server_url+'wordcloud?query={0}&zipcode={1}&date={2}&phone={3}'
    
        query = input("Please enter search term(s): ")
        zipcode = input("Please enter a zipcode: ")
        date = input("Please enter a date (YYYY-MM-DD): ")
        phone = input("Please enter your cell number (1XXXXXXXXXX): ")
    
        # call the machine-payable endpoint
        response = requests.get(url=sel_url.format(urllib.parse.quote_plus(query), zipcode, date, phone))
    
        print('Congratulations, you just generated a unique piece of digital art for bitcoin!')
        print('It has been sent to you as an MMS, enjoy!')
    
    if __name__ == '__main__':
        get_art()
    

Save and close this file. Then run the client side script to test our
digital supply chain:

    python3 client.py
    

Congratulations, you just purchased unique digital artwork with
bitcoin and received it on your phone!

## Next Steps

You've learned how to compose _multiple_ bitcoin-payable APIs from
_different_ users to form a digital supply chain. This is actually a
concept of major importance for the Bitcoin price, whose significance
we'll try to tease out here.

* First, if you are a company like Dell, it doesn't actually help
the Bitcoin USD/price in the long run if you accept bitcoin for a
laptop. The reason is that Dell liquidates any bitcoin received
for USD upon receipt. This means a sell order is still placed on
an exchange - it is just delayed in time from the original
purchase.
* 
Why does Dell liquidate the bitcoin immediately? Because its
suppliers only accept USD (or, more generally, fiat currencies). A
massive global physical supply chain that already runs on dollars
is not going to get entirely rewired to use bitcoin. The costs in
infrastructure and volatility are large, and the benefits for
physical vendors as of 2015 are not large enough to trigger a
system-wide change.
* 
However, when it comes to the digital realm, we have a completely
different story. Now we have a data structure - the
[call graph][215] which is
conceptually similar to the supply chain.
* 
Typically, however, most of the nodes in the call graph for a
given program are executed locally, with each function using the
same computational resources as the owner of the `main` function.
* 
The few exceptions are calls to very high value remote paid APIs
like Twilio and Stripe; these API calls need to be extremely high
value because the fixed costs of getting API keys and setting up
a new API are quite high.
* 
However, with the advent of bitcoin-payable APIs, suddenly we
can think about doing _many more_ remote API calls, as the fixed
costs of doing these calls will rapidly decline now that we have
bitcoin as a common international digital currency.
* 
These bitcoin-payable API calls in turn allow us to build up
complex _digital supply chains_ like the one seen in this example.
* 
Over time, a large number of interconnected bitcoin-payable APIs
help us build up _closed loops_: sectors of the bitcoin economy
where bitcoin is constantly recycled into new uses and never sold
for fiat.
* 
Systematically taking sell orders off exchanges in this way - by
building the closed loops - is the long-term way to increase the
bitcoin price and build the cloud economy.

This gives you a sense of the conceptual importance of this
example. As a next step, you might think about other bitcoin-payable
APIs you might connect together. Additionally, while we don't support
Haskell right now, some of the concepts in
[Hoogle][216] (a type signature-based
search engine) could potentially be used in Python 3 using
[function annotations][217]
to help systematize the search for composable functions.

If you build anything related to this and want to earn some bitcoin
for your efforts, write it up and submit it as a
[bitcoin tutorial][218]. If we decide to publish
it on our site, you'll win $200 in BTC!

You can also come to our Slack channel at [slack.21.co][4] to find other
folks with 21 Bitcoin Computers to post your endpoints and give
feedback. We look forward to seeing you there!

---

## How to send your Bitcoin to the Blockchain

Just as a reminder, you can send bitcoin mined or earned in your
21.co balance to the blockchain at any time by running `21
flush` . A transaction will be created within 10 minutes,
and you can view the transaction id with `21 log`.
Once the transaction has been confirmed, you can check the
balance in your bitcoin wallet from the command line with
`wallet balance`, and you can send bitcoin from your
wallet to another address with `wallet sendto
$BITCOIN_ADDRESS $BTC_AMOUNT --use-unconfirmed`. Make sure
to use the amount in BTC, not in Satoshi; the
`--use-unconfirmed` flag ensures that you can send even if you
have unconfirmed transactions in your wallet.

---

## Ready to sell your endpoint? Go to slack.21.co

Ready to try out your bitcoin-payable server in the wild? Or simply want to
browse and purchase from other bitcoin-enabled servers? Head over to the [21 Developer Community][219] at slack.21.co to join the bitcoin machine-payable marketplace hosted on the 21 peer-to-peer
network.

---

# Next :

## [Build More Bitcoin Apps][2]

[![Next](https://assets.21.co/setup/img/next_app.png)][2]

Check out all the Bitcoin Apps you can build with the 21 Bitcoin Computer.

[See more apps][2]

[![Next](https://assets.21.co/setup/img/next_app.png)][2]


---

Authors  
John Granata

If you have any questions or issues, please drop us a line at [\[email protected\] ][221] or join our [Slack ][4] community.

This content is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License][222].


(c) 2016, 21.co

[Get The 21 Bitcoin Computer][3]


[0]: /
[1]: /setup/
[2]: /learn/
[3]: /buy/
[4]: https://slack.21.co
[5]: /bitnodes/
[6]: /about/
[7]: #a-bitcoin-mashup-as-a-digital-supply-chain "A Bitcoin Mashup as a Digital Supply Chain"
[8]: #overview "Overview"
[9]: #prerequisites "Prerequisites"
[10]: #step-1-set-up-client-server-and-server-2-accounts "Step 1: Set up client, server, and server-2 accounts"
[11]: #step-2-set-up-the-first-server-in-the-digital-supply-chain "Step 2: Set up the first server in the digital supply chain"
[12]: #imgur "Imgur"
[13]: #twitter "Twitter"
[14]: #twilio "Twilio"
[15]: #step-3-set-up-the-second-server-in-the-digital-supply-chain "Step 3: Set up the second server in the digital supply chain"
[16]: #step-4-set-up-the-client "Step 4: Set up the client"
[17]: #next-steps "Next Steps"
[18]: /learn/ "< Back To Index"
[19]: https://twitter.com/intent/tweet?text=Hmm. This looks like a good resource for learning how to build Bitcoin apps:&url=https%3A//21.co/learn/bitcoin-mashup/
[20]: https://www.facebook.com/sharer/sharer.php?u=https%3A//21.co/learn/bitcoin-mashup/
[21]: /cdn-cgi/l/email-protection#28170e5b5d4a424d4b5c157c40415b08444747435b084441434d0849084f47474c085a4d5b475d5a4b4d084e475a08444d495a4641464f0840475f085c47084a5d41Xld Bitcoin apps&body=Here's the URL: https%3A//21.co/learn/bitcoin-mashup/
[22]: /setup
[23]: ../introduction-to-the-21-bitcoin-computer/
[24]: ../21-multiple-users
[25]: ../bitcoin-payable-api
[26]: ../bitcoin-sms-contact
[27]: #code-70646e9dc87560a4675a387ed09645dcd12e6fac-1
[28]: #code-70646e9dc87560a4675a387ed09645dcd12e6fac-2
[29]: #code-70646e9dc87560a4675a387ed09645dcd12e6fac-3
[30]: #code-70646e9dc87560a4675a387ed09645dcd12e6fac-4
[31]: #code-70646e9dc87560a4675a387ed09645dcd12e6fac-5
[32]: #code-70646e9dc87560a4675a387ed09645dcd12e6fac-6
[33]: #code-70646e9dc87560a4675a387ed09645dcd12e6fac-7
[34]: #code-70646e9dc87560a4675a387ed09645dcd12e6fac-8
[35]: https://api.imgur.com
[36]: https://dev.twitter.com/apps
[37]: https://www.twilio.com/user/account/phone-numbers/dev-tools/api-keys
[38]: #code-66a4db1944e78a47de749378267ab80e41342cac-1
[39]: #code-66a4db1944e78a47de749378267ab80e41342cac-2
[40]: #code-66a4db1944e78a47de749378267ab80e41342cac-3
[41]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-1
[42]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-2
[43]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-3
[44]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-4
[45]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-5
[46]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-6
[47]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-7
[48]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-8
[49]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-9
[50]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-10
[51]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-11
[52]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-12
[53]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-13
[54]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-14
[55]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-15
[56]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-16
[57]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-17
[58]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-18
[59]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-19
[60]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-20
[61]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-21
[62]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-22
[63]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-23
[64]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-24
[65]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-25
[66]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-26
[67]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-27
[68]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-28
[69]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-29
[70]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-30
[71]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-31
[72]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-32
[73]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-33
[74]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-34
[75]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-35
[76]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-36
[77]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-37
[78]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-38
[79]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-39
[80]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-40
[81]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-41
[82]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-42
[83]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-43
[84]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-44
[85]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-45
[86]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-46
[87]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-47
[88]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-48
[89]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-49
[90]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-50
[91]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-51
[92]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-52
[93]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-53
[94]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-54
[95]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-55
[96]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-56
[97]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-57
[98]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-58
[99]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-59
[100]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-60
[101]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-61
[102]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-62
[103]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-63
[104]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-64
[105]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-65
[106]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-66
[107]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-67
[108]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-68
[109]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-69
[110]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-70
[111]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-71
[112]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-72
[113]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-73
[114]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-74
[115]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-75
[116]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-76
[117]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-77
[118]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-78
[119]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-79
[120]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-80
[121]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-81
[122]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-82
[123]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-83
[124]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-84
[125]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-85
[126]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-86
[127]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-87
[128]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-88
[129]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-89
[130]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-90
[131]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-91
[132]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-92
[133]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-93
[134]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-94
[135]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-95
[136]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-96
[137]: #code-9dad1b72601261f529dd3adfa52a796f47c3c9c5-97
[138]: #code-14abf3d8f96acceb772da091de3f75aeb43b96aa-1
[139]: #code-14abf3d8f96acceb772da091de3f75aeb43b96aa-2
[140]: #code-608bbb32776ca86abdef29c9a4a93e7acd6f6552-1
[141]: #code-608bbb32776ca86abdef29c9a4a93e7acd6f6552-2
[142]: #code-608bbb32776ca86abdef29c9a4a93e7acd6f6552-3
[143]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-1
[144]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-2
[145]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-3
[146]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-4
[147]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-5
[148]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-6
[149]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-7
[150]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-8
[151]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-9
[152]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-10
[153]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-11
[154]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-12
[155]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-13
[156]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-14
[157]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-15
[158]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-16
[159]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-17
[160]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-18
[161]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-19
[162]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-20
[163]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-21
[164]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-22
[165]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-23
[166]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-24
[167]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-25
[168]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-26
[169]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-27
[170]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-28
[171]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-29
[172]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-30
[173]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-31
[174]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-32
[175]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-33
[176]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-34
[177]: #code-551b71cf6df6d9e0bc392f02bec0e008fc2a05e2-35
[178]: #code-a8bdd8839c06e4fd6e6cccf3f2aee46ec95a8363-1
[179]: #code-a8bdd8839c06e4fd6e6cccf3f2aee46ec95a8363-2
[180]: #code-539096d5e673816b921257d4ac49fa3d16366c26-1
[181]: #code-539096d5e673816b921257d4ac49fa3d16366c26-2
[182]: #code-539096d5e673816b921257d4ac49fa3d16366c26-3
[183]: #code-539096d5e673816b921257d4ac49fa3d16366c26-4
[184]: #code-539096d5e673816b921257d4ac49fa3d16366c26-5
[185]: #code-539096d5e673816b921257d4ac49fa3d16366c26-6
[186]: #code-539096d5e673816b921257d4ac49fa3d16366c26-7
[187]: #code-539096d5e673816b921257d4ac49fa3d16366c26-8
[188]: #code-539096d5e673816b921257d4ac49fa3d16366c26-9
[189]: #code-539096d5e673816b921257d4ac49fa3d16366c26-10
[190]: #code-539096d5e673816b921257d4ac49fa3d16366c26-11
[191]: #code-539096d5e673816b921257d4ac49fa3d16366c26-12
[192]: #code-539096d5e673816b921257d4ac49fa3d16366c26-13
[193]: #code-539096d5e673816b921257d4ac49fa3d16366c26-14
[194]: #code-539096d5e673816b921257d4ac49fa3d16366c26-15
[195]: #code-539096d5e673816b921257d4ac49fa3d16366c26-16
[196]: #code-539096d5e673816b921257d4ac49fa3d16366c26-17
[197]: #code-539096d5e673816b921257d4ac49fa3d16366c26-18
[198]: #code-539096d5e673816b921257d4ac49fa3d16366c26-19
[199]: #code-539096d5e673816b921257d4ac49fa3d16366c26-20
[200]: #code-539096d5e673816b921257d4ac49fa3d16366c26-21
[201]: #code-539096d5e673816b921257d4ac49fa3d16366c26-22
[202]: #code-539096d5e673816b921257d4ac49fa3d16366c26-23
[203]: #code-539096d5e673816b921257d4ac49fa3d16366c26-24
[204]: #code-539096d5e673816b921257d4ac49fa3d16366c26-25
[205]: #code-539096d5e673816b921257d4ac49fa3d16366c26-26
[206]: #code-539096d5e673816b921257d4ac49fa3d16366c26-27
[207]: #code-539096d5e673816b921257d4ac49fa3d16366c26-28
[208]: #code-539096d5e673816b921257d4ac49fa3d16366c26-29
[209]: #code-539096d5e673816b921257d4ac49fa3d16366c26-30
[210]: #code-539096d5e673816b921257d4ac49fa3d16366c26-31
[211]: #code-539096d5e673816b921257d4ac49fa3d16366c26-32
[212]: #code-539096d5e673816b921257d4ac49fa3d16366c26-33
[213]: #code-539096d5e673816b921257d4ac49fa3d16366c26-34
[214]: #code-539096d5e673816b921257d4ac49fa3d16366c26-35
[215]: https://en.wikipedia.org/wiki/Call_graph
[216]: https://www.haskell.org/hoogle/
[217]: http://ceronman.com/2013/03/12/a-powerful-unused-feature-of-python-function-annotations/
[218]: /submit-bitcoin-tutorial
[219]: https://slack.21.co/
[220]: /cdn-cgi/l/email-protection#d2edf4a1a7b0b8b7b1a6ef86babba1f2bebdbdb9a1f2bebbb9b7f2b3f2b5bdbdb6f2a0b7a1bda7a0b1b7f2b4bda0f2beb7b3a0bcbbbcb5f2babda5f2a6bdf2b0a7bbXld Bitcoin apps&body=Here's the URL: https%3A//21.co/learn/bitcoin-mashup/
[221]: /cdn-cgi/l/email-protection#12616762627d60665220233c717d
[222]: https://creativecommons.org/licenses/by-sa/4.0/
[223]: //twitter.com/21
[224]: //medium.com/@21
