[![21.co](https://assets.21.co/shared/img/21logo.png)21 Inc][0]

# [Setup][1] | [Tutorials][2] | [Buy][3] | [Community][4] | [Nodes][5] | [About][6]


# Translate English to Chinese for Bitcoin 
*Content authored by Ronak Mehta  |  Markdown created by PK Rasam* 
  

* [Translate English Text To Chinese for Bitcoin][7]
  * [Overview][8]
  * [Prerequisites][9]
  * [Step 1: Set up client and server accounts.][10]
  * [Step 2: Get a Google Translate API Key][11]
  * [Step 3: Create a server that translates a user's input from English to Chinese][12]
  * [Step 4: Create a client that accepts English text and returns the Chinese translation][13]
  * [Next Steps][14]
* [< Back To Index][15]

# Translate English Text To Chinese for Bitcoin

## Overview

In this tutorial we'll show you how to become an API reseller by
setting up a bitcoin-payable translation endpoint on your 21 Bitcoin
Computer.

## Prerequisites

You will need the following items:

* A 21 Bitcoin Computer, with built-in mining and software
* The latest version of the 21 software, obtained by running `21
update` as described in the [setup][19] process.
* Do the [Introduction to the 21 Bitcoin Computer][20]
tutorial
* Do the [Working with Multiple 21 Users][21] tutorial

If you've got all the prerequisites, you are ready to go. Let's get started!

## Step 1: Set up client and server accounts.

Follow the instructions in the
[Working With Multiple 21 Users][21] tutorial to set
up the `twenty-client` and `twenty-server` users and install Flask.

## Step 2: Get a Google Translate API Key

Go to the
[Google Developers Console][22] and
create an account. Click on `Dashboard` on the left-hand side of the
window and select `Enable and manage APIs`. From the `Other popular
APIs` category select `Translate API`. Select the `Enable API` button
on top and then click on the `Credentials` option on the left-hand
side. Click on `Add credentials` drop down button and select `API
key`. A pop-up window with different key options will show up. Select
`Server key`. In the new window enter the name of your project that
this key will be stored under and click on the `Create` button. Take
note of your API key once it is created.

NOTE: Google requires a user to enter their billing information in
order for the API key to work. You will need to add your billing
information in order to use the API key you just created above. As
noted on their
[pricing page][23], any
usage above the courtesy limits will trigger billing. You won't
encounter that limit in small-scale testing, but beyond that point you
will probably want to set your bitcoin-payable API's price above the
corresponding Google API price to at least break even. You can even
set it to a higher amount, as a user's fixed cost to buy the endpoint
is in theory eliminated if they already have bitcoin (so they may
experience net savings).

In the Google Developers Console window, click on the `Products &
Services` menu option that is represented as 3 horizontal white
dashes. Select `Billing` from the options shown in the drop-down menu
and enter your billing information.

With this step complete you are ready to use your Google Translate API
key. Let's create the server that will send the request to the Google
Translate REST API.

## Step 3: Create a server that translates a user's input from English to Chinese

Log in as the `twenty-server` user and create a folder for your
project:

    
    mkdir ~/translate-server && cd ~/translate-server
    

Set an environment variable that defines your newly created Google Translate API key.

    
    export GOOGLE_TRANSLATE_API_KEY=<enter your API key here>
    

You will also need to install the google api client python
library. Type the following command in your terminal:

    
    sudo pip3 install google-api-python-client
    

Now start editing a file named `translate-server.py` in this directory
with the following code:

    
    import os
    import json
    from flask import Flask, request
    from apiclient.discovery import build
    
    #import from the 21 Developer Library
    from two1.lib.wallet import Wallet
    from two1.lib.bitserv.flask import Payment
    
    # set up server side wallet
    app = Flask(__name__)
    wallet = Wallet()
    payment = Payment(app, wallet)
    
    # create a developer account on Google and obtain a API key for the translation app
    service = build('translate', 'v2', developerKey=os.environ.get('GOOGLE_TRANSLATE_API_KEY'))
    
    # create a 402 end-point that accepts a user's input and translates it to Chinese and returns it
    @app.route('/translate')
    @payment.required(1000)
    def trans():
        """Translate from English to Chinese"""
        # Get user's input text
        text = request.args.get('text')
    
        # Send a request to Google's Translate REST API using your API credentials defined above 
        ans = service.translations().list(source='en', target='zh-CN', q=text).execute()
    
        # Return translated text back to user
        return ans['translations'][0]['translatedText']
    
    if __name__ == '__main__':
        app.run(host='0.0.0.0', debug=True)
    

Start the server with:

    
    python3 translate-server.py
    

## Step 4: Create a client that accepts English text and returns the Chinese translation

Open a new terminal and SSH into your Bitcoin Computer as `twenty-client`.
This will be the user identity for the client who will buy the translation service
that the `twenty-server` user is hosting.

Create a folder to house the client project:

    
    mkdir ~/translate-client && cd ~/translate-client
    

Now start editing a file named `translate-client.py` in this directory and type in
the following code:

    
    import sys
    
    #import from the 21 Developer Library
    from two1.commands.config import Config
    from two1.lib.wallet import Wallet
    from two1.lib.bitrequests import BitTransferRequests
    
    #set up bitrequest client for BitTransfer requests
    wallet = Wallet()
    username = Config().username
    requests = BitTransferRequests(wallet, username)
    
    #server address
    server_url = 'http://localhost:5000/'
    
    def buy_translation():
    
        # Ask user to input text in english
        print("Welcome to English-to-Chinese Translation.\n")
        inp_text = input("Enter the English text that you would like translated into Chinese:\n")
    
        # Send request to server with user input text and user's wallet address for payment
        sel_url = server_url+'translate?text={0}&payout_address={1}'
        response = requests.get(url=sel_url.format(inp_text, wallet.get_payout_address()))
    
        # Print the translated text out to the terminal
        print("The following is the translation of the text you input.\n")
        print(response.text)
    
    if __name__ == '__main__':
        buy_translation()
    

Save this file and close it. Now run your client script with the following command:

    
    python3 translate-client.py
    

If all goes well, you should see a prompt for the input text you wish
to translate. A purchase is executed returning the translated
text. You should see the `twenty-client` balance decrease and the
`twenty-server` balance increase. You can confirm this by running `21
log` as the `twenty-client` and the `twenty-server` user respectively.
And as the `twenty-server` user, you can flush your winnings to the
blockchain by doing `21 flush`.

## Next Steps

This is an example of how to resell a paid API for Bitcoin. An
interesting extension of this would be to add a second, higher-priced
endpoint that involved some human labor, giving higher quality human
translation at the expense of a higher price and significantly
increased translation latency. One way to do this would be to have
human translators standing by in a Slack forum, and set up a
machine-payable translation API backed by a
[Slack integration][88] that would return
the results.

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
browse and purchase from other bitcoin-enabled servers? Head over to the [21 Developer Community][89] at slack.21.co to join the bitcoin machine-payable marketplace hosted on the 21 peer-to-peer
network.

---

# Next :

## [Build More Bitcoin Apps][2]

[![Next](https://assets.21.co/setup/img/next_app.png)][2]

Check out all the Bitcoin Apps you can build with the 21 Bitcoin Computer.


---

*Content authored by Ronak Mehta  |  Markdown created by PK Rasam* 

If you have any questions or issues, please drop us a line at [\[email protected\] ][91] or join our [Slack ][4] community.

This content is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License][92].


(c) 2016, 21.co

[Get The 21 Bitcoin Computer][3]


[0]: /
[1]: /setup/
[2]: /learn/
[3]: /buy/
[4]: https://slack.21.co
[5]: /bitnodes/
[6]: /about/
[7]: #translate-english-text-to-chinese-for-bitcoin "Translate English Text To Chinese for Bitcoin"
[8]: #overview "Overview"
[9]: #prerequisites "Prerequisites"
[10]: #step-1-set-up-client-and-server-accounts "Step 1: Set up client and server accounts."
[11]: #step-2-get-a-google-translate-api-key "Step 2: Get a Google Translate API Key"
[12]: #step-3-create-a-server-that-translates-a-users-input-from-english-to-chinese "Step 3: Create a server that translates a user's input from English to Chinese"
[13]: #step-4-create-a-client-that-accepts-english-text-and-returns-the-chinese-translation "Step 4: Create a client that accepts English text and returns the Chinese translation"
[14]: #next-steps "Next Steps"
[15]: /learn/ "< Back To Index"
[16]: https://twitter.com/intent/tweet?text=Hmm. This looks like a good resource for learning how to build Bitcoin apps:&url=https%3A//21.co/learn/bitcoin-translation/
[17]: https://www.facebook.com/sharer/sharer.php?u=https%3A//21.co/learn/bitcoin-translation/
[18]: /cdn-cgi/l/email-protection#9ca3baefe9fef6f9ffe8a1c8f4f5efbcf0f3f3f7efbcf0f5f7f9bcfdbcfbf3f3f8bceef9eff3e9eefff9bcfaf3eebcf0f9fdeef2f5f2fbbcf4f3ebbce8f3bcfee9f5Xld Bitcoin apps&body=Here's the URL: https%3A//21.co/learn/bitcoin-translation/
[19]: /setup
[20]: ../introduction-to-the-21-bitcoin-computer/
[21]: ../21-multiple-users
[22]: https://console.developers.google.com
[23]: https://cloud.google.com/translate/v2/pricing
[24]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-1
[25]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-2
[26]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-3
[27]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-4
[28]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-5
[29]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-6
[30]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-7
[31]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-8
[32]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-9
[33]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-10
[34]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-11
[35]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-12
[36]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-13
[37]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-14
[38]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-15
[39]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-16
[40]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-17
[41]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-18
[42]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-19
[43]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-20
[44]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-21
[45]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-22
[46]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-23
[47]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-24
[48]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-25
[49]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-26
[50]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-27
[51]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-28
[52]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-29
[53]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-30
[54]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-31
[55]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-32
[56]: #code-0e8e0983f95763db28e3785e24ee58f132ffce2e-33
[57]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-1
[58]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-2
[59]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-3
[60]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-4
[61]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-5
[62]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-6
[63]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-7
[64]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-8
[65]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-9
[66]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-10
[67]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-11
[68]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-12
[69]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-13
[70]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-14
[71]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-15
[72]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-16
[73]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-17
[74]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-18
[75]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-19
[76]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-20
[77]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-21
[78]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-22
[79]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-23
[80]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-24
[81]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-25
[82]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-26
[83]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-27
[84]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-28
[85]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-29
[86]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-30
[87]: #code-ef932fb6f229067df6cb4f46e9653b1919d466c8-31
[88]: https://slack.com/integrations
[89]: https://slack.21.co/
[90]: /cdn-cgi/l/email-protection#e1dec79294838b848295dcb5898892c18d8e8e8a92c18d888a84c180c1868e8e85c19384928e94938284c1878e93c18d8480938f888f86c1898e96c1958ec1839488Xld Bitcoin apps&body=Here's the URL: https%3A//21.co/learn/bitcoin-translation/
[91]: /cdn-cgi/l/email-protection#ff8c8a8f8f908d8bbfcdced19c90
[92]: https://creativecommons.org/licenses/by-sa/4.0/
[93]: //twitter.com/21
[94]: //medium.com/@21
