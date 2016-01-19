
# [Setup][1] | [Tutorials][2] | [Buy][3] | [Community][4] | [Nodes][5] | [About][6]


# Receive an SMS from Anyone for Bitcoin 
*Content authored by John Granata  |  Markdown created by PK Rasam* 
  

* [Receive an SMS from Anyone for Bitcoin][7]
  * [Overview][8]
  * [Prerequisites][9]
  * [Step 1: Set up client and server accounts.][10]
  * [Step 2: Sign up for a Twilio API key][11]
  * [Step 3: Set up the SMS server][12]
  * [Step 4: Set up the client who will pay to SMS you][13]
  * [Next Steps][14]
* [< Back To Index][15]

# Receive an SMS from Anyone for Bitcoin

## Overview

In this tutorial we'll show you how to set up your 21 Bitcoin Computer
as a server that will allow anyone to send you an SMS for a small
amount of bitcoin - without revealing your phone number. The example
can be extended to any other form of out-of-network social messaging,
such as an email from someone you haven't met or a Twitter DM from
someone you haven't followed. It's a way to monetize your inbox and
widen the circle of people who can contact you.

## Prerequisites

You will need the following items:

* A 21 Bitcoin Computer, with built-in mining and software
* The latest version of the 21 software, obtained by running `21
update` as described in the [setup][19] process.
* Do the [Introduction to the 21 Bitcoin Computer][20]
tutorial
* Do the [Working with Multiple 21 Users][21] tutorial

If you've got all the prerequisites, you are ready to go. Let's get
started!

## Step 1: Set up client and server accounts.

Follow the instructions in the
[Working With Multiple 21 Users][21] tutorial to set
up the `twenty-client`, `twenty-server`, and `twenty-server-2` users
and install Flask.

## Step 2: Sign up for a Twilio API key

Go to [twilio.com][22] and create an account. Take
note of your
[account SID][23], auth token, and Twilio phone number. Then install the Twilio Python3 package:

    
    sudo pip3 install twilio
    

We'll use this to send the SMS.

## Step 3: Set up the SMS server

Now log into the Bitcoin Computer as the `twenty-server` user:

    
    ssh twenty-server@<BITCOIN_COMPUTER_IP_ADDRESS>
    

Create a folder to house your project:

    
    mkdir bitcoin-sms-server && cd bitcoin-sms-server
    

Use a text editor to create a file called `sms-server.py` in the
`bitcoin-sms-server` directory, and fill it with the following code:

    
    import os
    
    from twilio.rest import TwilioRestClient
    from flask import Flask, request
    
    # import from the 21 Bitcoin Developer Library
    from two1.lib.wallet import Wallet
    from two1.lib.bitserv.flask import Payment
    
    app = Flask(__name__)
    wallet = Wallet()
    payment = Payment(app, wallet)
    
    # create the twilio rest client
    client = TwilioRestClient(
        os.environ.get('TWILIO_ACCOUNT_SID'), os.environ.get('TWILIO_AUTH_TOKEN')
    )
    
    @app.route('/send-sms')
    @payment.required(1000)
    def send_sms():
        """Send an sms for bitcoin"""
        text = request.args.get('text')
        response = client.messages.create(
            to=os.environ.get('MY_PHONE_NUMBER'),
            from_=os.environ.get('TWILIO_PHONE_NUMBER'),
            body=text
        )
        return "Message sent."
    
    # set up and run the server
    if __name__ == '__main__':
        app.run(host='0.0.0.0')
    

Save the file and close it. Set environment variables in your terminal as follows:

    
    export TWILIO_ACCOUNT_SID=<Your Twilio Account SID>
    export TWILIO_AUTH_TOKEN=<Your Twilio Auth Token>
    export TWILIO_PHONE_NUMBER=<Your Twilio Phone Number>
    export MY_PHONE_NUMBER=<Your Phone Number>
    

Start the micropayments server:

    
    python3 sms-server.py
    

Your bitcoin-powered SMS endpoint is up and running! Let's get a
client user set up to test the endpoint.

## Step 4: Set up the client who will pay to SMS you

Leave your `twenty-server` session open, but open a new terminal on
your regular computer/laptop (or PuTTY session on Windows) and SSH
into your 21 Bitcoin Computer, this time as the `twenty-client`
user. Create a project folder called `bitcoin-sms-client` and a file
called `sms-client.py` with the following code:

    
    import urllib.parse
    
    # import from 21 Bitcoin Developer Library
    from two1.commands.config import Config
    from two1.lib.wallet import Wallet
    from two1.lib.bitrequests import BitTransferRequests
    
    wallet = Wallet()
    username = Config().username
    requests = BitTransferRequests(wallet, username)
    
    # request the bitcoin-enabled endpoint you're hosting on the 21 Bitcoin Computer
    def testendpoint(sms='I just paid you bitcoin to send you this message!'):
        # In a real application you would escape this message to prevent injections
        message=urllib.parse.quote_plus(sms)
        response = requests.get(url='http://localhost:5000/send-sms?text='+message)
        print(response.text)
    
    if __name__ == '__main__':
        import sys
        testendpoint(sys.argv[1])
    

You can run this client script from the command line to test your SMS
endpoint:

    
    python3 sms-client.py 'I am SMSing you for bitcoin!'
    

You should receive a text message at your phone number.
Congratulations, you just set up a way for someone to send you a text
message for bitcoin!

## Next Steps

You've learned how to build a very simple app in which someone outside
your social network can pay you bitcoin to contact you. This is
actually something that people have wanted on the internet for a very
long time, since the development of
[Hashcash][82] and before. Here are
some ideas for what to build next:

* Extend the example to escape the input text message and otherwise be
robust against bad input strings
* 
Add support for paying bitcoin to contact you via
[email][83],
[Facebook][84],
[Twitter][85],
[LinkedIn][86]
, and other forms of social messaging.
* 
Create an inbox viewer which rank orders your received messages
not by the time they were received, but by the amount of bitcoin
sent with them (a new kind of "priority inbox")
* 
Make this example high performance by replacing the simple Flask
server with a proper deployment on the underlying hardware. See
[this][87]
and [this][88] for
more information.

If you build anything like this and want to earn some bitcoin for your
efforts, write it up and submit it as a
[bitcoin tutorial][89]. If we decide to publish
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
browse and purchase from other bitcoin-enabled servers? Head over to the [21 Developer Community][90] at slack.21.co to join the bitcoin machine-payable marketplace hosted on the 21 peer-to-peer
network.

---

# Next :

## [Build More Bitcoin Apps][2]

[![Next](https://assets.21.co/setup/img/next_app.png)][2]

Check out all the Bitcoin Apps you can build with the 21 Bitcoin Computer.


---

*Content authored by John Granata  |  Markdown created by PK Rasam* 

If you have any questions or issues, please drop us a line at [Email ][92] or join our [Slack ][4] community.

This content is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License][93].


(c) 2016, 21.co

[Get The 21 Bitcoin Computer][3]


[0]: /
[1]: /setup/
[2]: /learn/
[3]: /buy/
[4]: https://slack.21.co
[5]: /bitnodes/
[6]: /about/
[7]: #receive-an-sms-from-anyone-for-bitcoin "Receive an SMS from Anyone for Bitcoin"
[8]: #overview "Overview"
[9]: #prerequisites "Prerequisites"
[10]: #step-1-set-up-client-and-server-accounts "Step 1: Set up client and server accounts."
[11]: #step-2-sign-up-for-a-twilio-api-key "Step 2: Sign up for a Twilio API key"
[12]: #step-3-set-up-the-sms-server "Step 3: Set up the SMS server"
[13]: #step-4-set-up-the-client-who-will-pay-to-sms-you "Step 4: Set up the client who will pay to SMS you"
[14]: #next-steps "Next Steps"
[15]: /learn/ "< Back To Index"
[17]: https://www.facebook.com/sharer/sharer.php?u=https%3A//21.co/learn/bitcoin-sms-contact/
[19]: /setup
[20]: ../introduction-to-the-21-bitcoin-computer/
[21]: ../21-multiple-users
[22]: https://twilio.com
[23]: https://www.twilio.com/help/faq/twilio-basics/what-is-an-application-sid
[24]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-1
[25]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-2
[26]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-3
[27]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-4
[28]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-5
[29]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-6
[30]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-7
[31]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-8
[32]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-9
[33]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-10
[34]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-11
[35]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-12
[36]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-13
[37]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-14
[38]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-15
[39]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-16
[40]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-17
[41]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-18
[42]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-19
[43]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-20
[44]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-21
[45]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-22
[46]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-23
[47]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-24
[48]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-25
[49]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-26
[50]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-27
[51]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-28
[52]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-29
[53]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-30
[54]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-31
[55]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-32
[56]: #code-067cc7d36c0ca7fc44fd25cb98db7b8790030b6a-33
[57]: #code-ba201be562e04c349160b0169dd99f463a591407-1
[58]: #code-ba201be562e04c349160b0169dd99f463a591407-2
[59]: #code-ba201be562e04c349160b0169dd99f463a591407-3
[60]: #code-ba201be562e04c349160b0169dd99f463a591407-4
[61]: #code-44f6015af139da5e563ae2a5713f2f2b5c490d3b-1
[62]: #code-44f6015af139da5e563ae2a5713f2f2b5c490d3b-2
[63]: #code-44f6015af139da5e563ae2a5713f2f2b5c490d3b-3
[64]: #code-44f6015af139da5e563ae2a5713f2f2b5c490d3b-4
[65]: #code-44f6015af139da5e563ae2a5713f2f2b5c490d3b-5
[66]: #code-44f6015af139da5e563ae2a5713f2f2b5c490d3b-6
[67]: #code-44f6015af139da5e563ae2a5713f2f2b5c490d3b-7
[68]: #code-44f6015af139da5e563ae2a5713f2f2b5c490d3b-8
[69]: #code-44f6015af139da5e563ae2a5713f2f2b5c490d3b-9
[70]: #code-44f6015af139da5e563ae2a5713f2f2b5c490d3b-10
[71]: #code-44f6015af139da5e563ae2a5713f2f2b5c490d3b-11
[72]: #code-44f6015af139da5e563ae2a5713f2f2b5c490d3b-12
[73]: #code-44f6015af139da5e563ae2a5713f2f2b5c490d3b-13
[74]: #code-44f6015af139da5e563ae2a5713f2f2b5c490d3b-14
[75]: #code-44f6015af139da5e563ae2a5713f2f2b5c490d3b-15
[76]: #code-44f6015af139da5e563ae2a5713f2f2b5c490d3b-16
[77]: #code-44f6015af139da5e563ae2a5713f2f2b5c490d3b-17
[78]: #code-44f6015af139da5e563ae2a5713f2f2b5c490d3b-18
[79]: #code-44f6015af139da5e563ae2a5713f2f2b5c490d3b-19
[80]: #code-44f6015af139da5e563ae2a5713f2f2b5c490d3b-20
[81]: #code-44f6015af139da5e563ae2a5713f2f2b5c490d3b-21
[82]: http://www.hashcash.org/papers/hashcash.pdf
[83]: https://docs.python.org/3/library/email-examples.html
[84]: https://developers.facebook.com/docs/messenger
[85]: https://dev.twitter.com/rest/reference/post/direct_messages/new
[86]: https://developer-programs.linkedin.com/documents/messaging-between-connections-api
[87]: http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvii-deployment-on-linux-even-on-the-raspberry-pi
[88]: http://tutos.readthedocs.org/en/latest/source/ndg.html
[89]: /submit-bitcoin-tutorial
[90]: https://slack.21.co/
[92]: mailto:support@21.co
[93]: https://creativecommons.org/licenses/by-sa/4.0/
[94]: //twitter.com/21
[95]: //medium.com/@21
