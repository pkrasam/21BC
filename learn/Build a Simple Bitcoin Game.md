[![21.co](https://assets.21.co/shared/img/21logo.png)21 Inc][0]

# [Setup][1] | [Tutorials][2] | [Buy][3] | [Community][4] | [Nodes][5] | [About][6]


# Build a Simple Bitcoin Game 
*Content authored by Tyler Julian  |  Markdown created by PK Rasam* 
  
* [Build a Simple Bitcoin Game][7]
  * [Overview][8]
  * [Prerequisites][9]
  * [Step 1: Set up client and server accounts.][10]
  * [Step 2: Create a simple bitcoin-powered game server][11]
  * [Step 3: Create a simple bitcoin game client][12]
  * [Next Steps][13]
* [< Back To Index][14]

# Build a Simple Bitcoin Game

## Overview

In this tutorial we'll show you how to build and host a simple game of
skill on your 21 Bitcoin Computer where users must answer a trivia
question correctly to win bitcoin.

## Prerequisites

You will need the following items:

* A 21 Bitcoin Computer, with built-in mining and software
* The latest version of the 21 software, obtained by running `21
update` as described in the [setup][18] process.
* Do the [Introduction to the 21 Bitcoin Computer][19]
tutorial
* Do the [Working with Multiple 21 Users][20] tutorial

If you've done all that, you are ready to go. Let's get started!

## Step 1: Set up client and server accounts.

Follow the instructions in the
[Working With Multiple 21 Users][20] tutorial to set
up the `twenty-client`, `twenty-server`, and `twenty-server-2` users
and install Flask.

## Step 2: Create a simple bitcoin-powered game server

Now let's set up a folder to house our app:

    
    mkdir trivia-server && cd trivia-server
    

Go to that directory, open a file named `trivia-server.py` in a text editor,
and paste in the following code:

    
    import os
    import json
    import random
    
    # import flask web microframework
    from flask import Flask
    from flask import request
    
    # import from the 21 Developer Library
    from two1.lib.wallet import Wallet
    from two1.lib.bitserv.flask import Payment
    
    app = Flask(__name__)
    wallet = Wallet()
    payment = Payment(app, wallet)
    
    question_bank = {
        'Who is the inventor of Bitcoin': 'Satoshi Nakamoto',
        'How many satoshis are in a bitcoin': '100000000',
        'What is the current coinbase reward (in BTC) for mining a block': '25'
    }
    
    question_list = list(question_bank.keys())
    
    # endpoint to get a question from the server
    @app.route('/question')
    def get_question():
        return question_list[random.randrange(0,len(question_list))]
    
    # machine-payable endpoint that pays user if answer is correct
    @app.route('/play')
    @payment.required(1000)
    def answer_question():
    
        # extract answer from client request
        answer = request.args.get('selection')
    
        # extract payout address from client address
        client_payout_addr = request.args.get('payout_address')
    
        # extract question from client request
        client_question = request.args.get('question')
    
        # check if answer is correct
        if answer.lower() == question_bank[client_question].lower():
            try:
                txid = wallet.send_to(client_payout_addr, 2000)
            except Exception as e:
                return ('Exception : ' + str(e), 500)
            return "Correct!"
        else:
            return "Incorrect response."
    
    if __name__ == '__main__':
        app.run(host='0.0.0.0')
    

We're all set! This microserver includes our bitcoin payment processor
and a flask route with some simple game logic to handle client
requests.

Make sure the server has some bitcoin for payouts by running:

    
    21 mine
    

Now run the following command to start the server:

    
    python3 trivia-server.py
    

## Step 3: Create a simple bitcoin game client

Now open up a new terminal window and connect to your 21 Bitcoin
Computer as `twenty-client`. Create a folder to house the client
project:

    
    mkdir trivia-client && cd trivia-client
    

Let's import our wallet and a `BitTransferRequests` client for making
bitcoin-enabled HTTP requests in a new file called `play.py`. Then
we'll finish out the file with the code to send the request to the
server:

    
    import json
    import os
    
    # import from the 21 Developer Library
    from two1.commands.config import Config
    from two1.lib.wallet import Wallet
    from two1.lib.bitrequests import BitTransferRequests
    
    # set up bitrequest client for BitTransfer requests
    wallet = Wallet()
    username = Config().username
    requests = BitTransferRequests(wallet, username)
    
    # server address
    server_url = 'http://localhost:5000/'
    
    def play():
    
        # get the question from the server
        response = requests.get(url=server_url+'question')
        question = response.text
    
        ans = input("Question: {}?\n".format(question))
        sel_url = server_url + 'play?question={0}&selection={1}&payout_address={2}'
        answer = requests.get(url=sel_url.format(question,ans, wallet.get_payout_address()))
        print(answer.text)
    
    if __name__ == '__main__':
        play()
    

That's it! Run the following code to start the game.

    
    python3 play.py
    

If you get a question right, the `twenty-client` should win some
bitcoin (which will show after they're confirmed on the blockchain)
and the `twenty-server` will see its bitcoin balance decrement.

If you get the following error message, make sure to run `21 mine` and
`21 flush` to get enough on-chain satoshis on the server. The server may
also need to wait for a confirmation before sending a second payment.

    
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
    <title>500 Internal Server Error</title>
    <h1>Internal Server Error</h1>
    <p>The server encountered an internal error and was unable to complete your request.  Either the server is overloaded or there is an error in the application.</p>
    

## Next Steps

You've learned how to build a very simple game in which someone can
win or lose bitcoin. Given these fundamentals, you can extend the code
to build a trivia game or other game of skill. Here are some ideas on
what to build next:

* Write a simple 2-player game of skill, like checkers or chess, with
a prize for the winner. A full list of abstract strategy games for inspiration is
[here][109]
and [here][110].
* 
Learn game theory by implementing one of the famous two-player games. A full
list is
[here][111].
* 
Extend this example by creating a database of trivia questions on
different topics. You can also reuse or modify existing trivia quiz
banks like the ones
[here][112]
or
[here][113], though make
sure that you have the license to these questions!
* 
Make this example high performance by replacing the simple Flask
server with a proper deployment on the underlying hardware. See
[this][114]
and [this][115] for
more information.

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

*Content authored by Tyler Julian  |  Markdown created by PK Rasam* 

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
[7]: #build-a-simple-bitcoin-game "Build a Simple Bitcoin Game"
[8]: #overview "Overview"
[9]: #prerequisites "Prerequisites"
[10]: #step-1-set-up-client-and-server-accounts "Step 1: Set up client and server accounts."
[11]: #step-2-create-a-simple-bitcoin-powered-game-server "Step 2: Create a simple bitcoin-powered game server"
[12]: #step-3-create-a-simple-bitcoin-game-client "Step 3: Create a simple bitcoin game client"
[13]: #next-steps "Next Steps"
[14]: /learn/ "< Back To Index"
[16]: https://www.facebook.com/sharer/sharer.php?u=https%3A//21.co/learn/build-a-simple-bitcoin-game/
[18]: /setup
[19]: ../introduction-to-the-21-bitcoin-computer/
[20]: ../21-multiple-users
[21]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-1
[22]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-2
[23]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-3
[24]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-4
[25]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-5
[26]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-6
[27]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-7
[28]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-8
[29]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-9
[30]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-10
[31]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-11
[32]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-12
[33]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-13
[34]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-14
[35]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-15
[36]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-16
[37]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-17
[38]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-18
[39]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-19
[40]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-20
[41]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-21
[42]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-22
[43]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-23
[44]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-24
[45]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-25
[46]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-26
[47]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-27
[48]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-28
[49]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-29
[50]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-30
[51]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-31
[52]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-32
[53]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-33
[54]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-34
[55]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-35
[56]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-36
[57]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-37
[58]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-38
[59]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-39
[60]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-40
[61]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-41
[62]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-42
[63]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-43
[64]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-44
[65]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-45
[66]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-46
[67]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-47
[68]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-48
[69]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-49
[70]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-50
[71]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-51
[72]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-52
[73]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-53
[74]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-54
[75]: #code-8f1f839c4051347d961acb48cdf37f5b5857fc12-55
[76]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-1
[77]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-2
[78]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-3
[79]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-4
[80]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-5
[81]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-6
[82]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-7
[83]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-8
[84]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-9
[85]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-10
[86]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-11
[87]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-12
[88]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-13
[89]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-14
[90]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-15
[91]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-16
[92]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-17
[93]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-18
[94]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-19
[95]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-20
[96]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-21
[97]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-22
[98]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-23
[99]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-24
[100]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-25
[101]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-26
[102]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-27
[103]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-28
[104]: #code-54f94cb852f31508c5e8f0d94437dd880ce82ffa-29
[105]: #code-76e5f6c2af1836abf0521e2f387cebd900344de1-1
[106]: #code-76e5f6c2af1836abf0521e2f387cebd900344de1-2
[107]: #code-76e5f6c2af1836abf0521e2f387cebd900344de1-3
[108]: #code-76e5f6c2af1836abf0521e2f387cebd900344de1-4
[109]: https://en.wikipedia.org/wiki/List_of_world_championships_in_mind_sports
[110]: https://en.wikipedia.org/wiki/Abstract_strategy_game
[111]: https://en.wikipedia.org/wiki/List_of_games_in_game_theory#List_of_games
[112]: http://ask.metafilter.com/16200/Where-to-download-Public-Domain-general-knowledge-trivia-question-bank
[113]: http://stackoverflow.com/questions/11067191/public-domain-trivia-database-for-game
[114]: http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvii-deployment-on-linux-even-on-the-raspberry-pi
[115]: http://tutos.readthedocs.org/en/latest/source/ndg.html
[116]: /submit-bitcoin-tutorial
[117]: https://slack.21.co/
[119]: mailto:support@21.co
[120]: https://creativecommons.org/licenses/by-sa/4.0/
[121]: //twitter.com/21
[122]: //medium.com/@21
