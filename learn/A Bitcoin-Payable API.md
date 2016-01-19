
# [Setup][1] | [Tutorials][2] | [Buy][3] | [Community][4] | [Nodes][5] | [About][6]


# A Bitcoin-Payable API 
*Content authored by David Harding, Saïvann Carignan  |  Markdown created by PK Rasam* 
  
* [A Bitcoin-Payable API][7]
  * [Overview][8]
  * [Prerequisites][9]
  * [Step 1: Set up client and server accounts.][10]
  * [Step 2: Create the micropayments server][11]
  * [Step 3: Create a client to purchase the service][12]
  * [Next Steps][13]
* [< Back To Index][14]

# A Bitcoin-Payable API

## Overview

In this tutorial we'll show you how to build and host a simple
bitcoin-payable API server. In this example, we will convert text to
speech, but you can easily extend it to sell many different kinds of
API calls.

## Prerequisites

You will need the following items:

* A 21 Bitcoin Computer, with built-in mining and software
* The latest version of the 21 software, obtained by running `21
update` as described in the [setup][18] process.
* Do the [Introduction to the 21 Bitcoin Computer][19]
tutorial
* Do the [Working with Multiple 21 Users][20] tutorial

If you've got all the prerequisites, you are ready to go. Let's get
started!

## Step 1: Set up client and server accounts.

Follow the instructions in the
[Working With Multiple 21 Users][20] tutorial to set
up the `twenty-client`, `twenty-server`, and `twenty-server-2` users
and install Flask.

## Step 2: Create the micropayments server

Connect to your 21 Bitcoin Computer as the `twenty-server` user,
create a project directory, and install the `eSpeak` TTS engine and
the Flask library for Python 3\.

    
    cd ~/
    mkdir tts-402-server && cd tts-402-server 
    sudo apt-get install espeak
    sudo pip3 install flask
    

Within this directory, create a file called `bitcoin-api-server.py`
and type in the following code:

    
    #!/usr/bin/env python3
    from subprocess import call
    from uuid import uuid4
    
    from flask import Flask
    from flask import request
    from flask import send_from_directory
    
    # Import from the 21 Bitcoin Developer Library
    from two1.lib.wallet import Wallet
    from two1.lib.bitserv.flask import Payment
    
    # Configure the app and wallet
    app = Flask(__name__)
    wallet = Wallet()
    payment = Payment(app, wallet)
    
    # Charge a fixed fee of 1000 satoshis per request to the
    # /tts endpoint
    @app.route('/tts')
    @payment.required(1000)
    def tts():
        # the text the client sent us
        text = str(request.args.get('text'))
    
        # a file to store the rendered audio file
        file = str(uuid4()) + '.wav'
    
        # run the TTS engine
        call(['espeak', '-w', '/tmp/' + file, text])
    
        # send the rendered audio back to the client
        return send_from_directory(
          '/tmp',
          file,
          as_attachment=True
        )
    
    # Initialize and run the server
    if __name__ == '__main__':
        app.run(host='0.0.0.0')
    

Save and close the file, and then run the following command:

    
    python3 bitcoin-api-server.py
    

## Step 3: Create a client to purchase the service

Open a new terminal and connect to your 21 Bitcoin Computer as the
`twenty-client` user. Create a folder to house the client project:

    
    mkdir tts-402-client && cd tts-402-client
    

Within this directory, open a file called `bitcoin-api-client.py` in a
text editor and type in the following code:

    
    #!/usr/bin/env python3
    
    # Change this to the IP address of your 21 Bitcoin Computer.
    # You can find this with `sudo hostname --ip-address`
    SERVER_IP_ADDRESS='127.0.0.1'
    
    # Import methods from the 21 Bitcoin Library
    from two1.commands.config import Config
    from two1.lib.wallet import Wallet
    from two1.lib.bitrequests import BitTransferRequests
    
    # Configure your Bitcoin wallet. 
    username = Config().username
    wallet = Wallet()
    requests = BitTransferRequests(wallet, username)
    
    # Send text to the endpoint
    def send_text(text):
        # tell the user what text they're sending
        print('You sent {0}'.format(text))
    
        # 402-payable endpoint URL and request
        tts_url = 'http://' + SERVER_IP_ADDRESS + ':5000/tts?text={0}'
        speech = requests.get(url=tts_url.format(text))
    
        # save the received audio file to disk
        speech_output = open('speech.wav', 'wb')
        speech_output.write(speech.content)
        speech_output.close()
    
    # Read the text to speechify from the CLI
    if __name__ == '__main__':
        from sys import argv
        send_text(argv[1])
    

Near the top of the code above, change the value of the
`SERVER_IP_ADDRESS` variable to the IP address of your 21 Bitcoin
Computer. This address should have been printed when you first setup
the 21 Bitcoin Computer, but you can also print it by running `sudo
hostname --ip-address`.

Once you're done editing, save the file, exit your text editor, and
run:

    
    python3 bitcoin-api-client.py "hello world"
    

This should print a line with your phrase, contact the API server, pay
the conversion fee using one of the 21 micropayments methods, convert
your text to speech, send the client the file, and then save the file
in the current directory as `speech.wav`.

You can now copy this file to any computer with speakers using `scp`
or the equivalent and play it in any media player.

## Next Steps

You've learned how to build a very simple API server in which someone
can send a text and get back an audio transcription of that text. Here
are some ideas on what to build next:

* Check out the [Bitcoin Mashup][100] example to get a
sense of how a digital supply chain can emerge from the
composition of _multiple_ bitcoin-payable APIs hosted by different
users.
* 
Make this example high performance by replacing the simple Flask
server with a proper deployment on the underlying hardware. See
[this][101]
and [this][102] for
more information.
* 
Use [Let's Encrypt][103] to add HTTPS support.
* 
Set up frontends to resell paid APIs like
[Bing Search][104],
[Yahoo Boss and YQL][105],
[Google Maps][106],
[Google Translate][107],
[Google Predict API][108],
[Moz Backlinks][109],
[Twilio][110],
[Wolfram Alpha][111],
and [Amazon Web Services][112]
* 
Integrate with an API aggregator like
[Mashape][113],
[Algorithmia][114], or (probably the
best) [Blockspring][115] to offer many API
services to your customers

If you build anything like this and want to earn some bitcoin for your
efforts, write it up and submit it as a
[bitcoin tutorial][116]. If we decide to publish
it on our site, you'll win $200 in BTC!

You can also come to our Slack channel at [slack.21.co][4] to find other
folks with 21 Bitcoin Computers to play your game and give
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
browse and purchase from other bitcoin-enabled servers? Head over to the [21 Developer Community][117] at slack.21.co to join the bitcoin machine-payable marketplace hosted on the 21 peer-to-peer
network.

---

# Next :

## [Build More Bitcoin Apps][2]

[![Next](https://assets.21.co/setup/img/next_app.png)][2]

Check out all the Bitcoin Apps you can build with the 21 Bitcoin Computer.


---

*Content authored by David Harding, Saïvann Carignan  |  Markdown created by PK Rasam* 

If you have any questions or issues, please drop us a line at [Email ][119] or join our [Slack ][4] community.

This content is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License][120].


(c) 2016, 21.co

[Get The 21 Bitcoin Computer][3]


[0]: /
[1]: /setup/
[2]: /learn/
[3]: /buy/
[4]: https://slack.21.co
[5]: /bitnodes/
[6]: /about/
[7]: #a-bitcoin-payable-api "A Bitcoin-Payable API"
[8]: #overview "Overview"
[9]: #prerequisites "Prerequisites"
[10]: #step-1-set-up-client-and-server-accounts "Step 1: Set up client and server accounts."
[11]: #step-2-create-the-micropayments-server "Step 2: Create the micropayments server"
[12]: #step-3-create-a-client-to-purchase-the-service "Step 3: Create a client to purchase the service"
[13]: #next-steps "Next Steps"
[14]: /learn/ "< Back To Index"
[16]: https://www.facebook.com/sharer/sharer.php?u=https%3A//21.co/learn/bitcoin-payable-api/
[18]: /setup
[19]: ../introduction-to-the-21-bitcoin-computer/
[20]: ../21-multiple-users
[21]: #code-8972e07c10e8db10cf4bab53ae3ecedb9e383355-1
[22]: #code-8972e07c10e8db10cf4bab53ae3ecedb9e383355-2
[23]: #code-8972e07c10e8db10cf4bab53ae3ecedb9e383355-3
[24]: #code-8972e07c10e8db10cf4bab53ae3ecedb9e383355-4
[25]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-1
[26]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-2
[27]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-3
[28]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-4
[29]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-5
[30]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-6
[31]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-7
[32]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-8
[33]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-9
[34]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-10
[35]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-11
[36]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-12
[37]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-13
[38]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-14
[39]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-15
[40]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-16
[41]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-17
[42]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-18
[43]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-19
[44]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-20
[45]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-21
[46]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-22
[47]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-23
[48]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-24
[49]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-25
[50]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-26
[51]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-27
[52]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-28
[53]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-29
[54]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-30
[55]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-31
[56]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-32
[57]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-33
[58]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-34
[59]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-35
[60]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-36
[61]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-37
[62]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-38
[63]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-39
[64]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-40
[65]: #code-723cfb9dec8f365627bc57e592a15cc127bd9e24-41
[66]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-1
[67]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-2
[68]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-3
[69]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-4
[70]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-5
[71]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-6
[72]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-7
[73]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-8
[74]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-9
[75]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-10
[76]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-11
[77]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-12
[78]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-13
[79]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-14
[80]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-15
[81]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-16
[82]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-17
[83]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-18
[84]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-19
[85]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-20
[86]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-21
[87]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-22
[88]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-23
[89]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-24
[90]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-25
[91]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-26
[92]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-27
[93]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-28
[94]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-29
[95]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-30
[96]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-31
[97]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-32
[98]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-33
[99]: #code-dfd80f325fac81902be86ca0bccf277511eadbef-34
[100]: ../bitcoin-mashup
[101]: http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvii-deployment-on-linux-even-on-the-raspberry-pi
[102]: http://tutos.readthedocs.org/en/latest/source/ndg.html
[103]: https://letsencrypt.org/
[104]: https://datamarket.azure.com/dataset/bing/search
[105]: https://developer.yahoo.com/everything.html
[106]: https://developers.google.com/maps/pricing-and-plans/
[107]: https://cloud.google.com/translate/v2/pricing
[108]: https://cloud.google.com/prediction/#pricing
[109]: https://moz.com/products/api/pricing
[110]: https://www.twilio.com/sms/pricing
[111]: http://products.wolframalpha.com/api/faqs.html
[112]: http://aws.amazon.com/awis/
[113]: https://www.mashape.com/
[114]: https://algorithmia.com/pricing
[115]: https://open.blockspring.com/browse
[116]: /submit-bitcoin-tutorial
[117]: https://slack.21.co/
[119]: mailto:support@21.co
[120]: https://creativecommons.org/licenses/by-sa/4.0/
[121]: //twitter.com/21
[122]: //medium.com/@21
