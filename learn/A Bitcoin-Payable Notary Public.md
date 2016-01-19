[![21.co](https://assets.21.co/shared/img/21logo.png)21 Inc][0]

# [Setup][1] | [Tutorials][2] | [Buy][3] | [Community][4] | [Nodes][5] | [About][6]


# A Bitcoin-Payable Notary Public
*Content authored by Tyler Julian  |  Markdown created by PK Rasam*   


* [A Bitcoin-Payable Notary Public][7]
  * [Overview][8]
  * [Prerequisites][9]
  * [Step 1: Set up client and server accounts.][10]
  * [Step 2: Log in as the server user and start the server][11]
  * [Step 3: Log in as the client user and purchase the endpoint][12]
  * [Next Steps][13]
* [< Back To Index][14]

# A Bitcoin-Payable Notary Public

## Overview

In this tutorial we'll show you how to create a bitcoin-payable notary
public service. Any user can pay bitcoin to a server endpoint that
writes a custom message to the blockchain to be stored forever.

After reading, you should be able to write data to the blockchain and
read it back whenever you'd like. You'll also gain experience using
the various bitcoin classes to build your own transactions.

## Prerequisites

You will need the following items:

* A 21 Bitcoin Computer, with built-in mining and software
* The latest version of the 21 software, obtained by running `21
update` as described in the [setup][18] process.
* Do the [Introduction to the 21 Bitcoin Computer][19]
tutorial
* Do the [Working with Multiple 21 Users][20] tutorial
* Do the [Bitcoin-Payable API][21] tutorial

If you've done all that, you are ready to go. Let's
get started!

## Step 1: Set up client and server accounts.

Follow the instructions in the
[Working With Multiple 21 Users][20] tutorial to set
up the `twenty-client`, `twenty-server`, and `twenty-server-2` users
and install Flask.

**IMPORTANT**: You will need to have a nonzero blockchain balance in
`twenty-client` to do this example. While logged in as
`twenty-client`, run `21 mine` followed by `21 flush` and wait until
`21 status` shows that you have a nonzero blockchain balance. This may
take anywhere from ~20 minutes to more than an hour, depending on the
speed of mining.

## Step 2: Log in as the server user and start the server

Log into the Bitcoin Computer as the `twenty-server`. Create a project
folder to house our app and an empty file as follows:


    
    cd ~/
    mkdir notary-server && cd notary-server
    touch notary-server.py
    

The server is going to need a blockchain balance for this example, so mine some
bitcoin and flush it to your bitcoin wallet:


    
    21 mine
    21 flush
    

The transaction will be broadcast to the blockchain within a 20 minute window
following the flush. You can check to see when this transaction is confirmed by
running:

    
    21 status
    

Now open `notary-server.py` in your text editor and type in the following
code:


    
    #!/usr/bin/env python3
    # import the flask web microframework
    from flask import Flask, request
    
    # import from the 21 Bitcoin Developer Library
    from two1.lib.wallet.two1_wallet import Two1Wallet
    from two1.lib.blockchain.twentyone_provider import TwentyOneProvider
    from two1.lib.bitcoin import utils
    from two1.lib.bitcoin import PublicKey, Script
    from two1.lib.bitcoin import Transaction, TransactionInput, TransactionOutput
    from two1.lib.bitserv.flask import Payment
    
    # Create application objects
    app = Flask(__name__)
    wallet = Two1Wallet(Two1Wallet.DEFAULT_WALLET_PATH, TwentyOneProvider())
    payment = Payment(app, wallet)
    
    @app.route('/write-message')
    @payment.required(1000)
    def write_message():
        """Write a message to the blockchain."""
    
        msg = request.args.get('message')
    
        # Create a bitcoin script object with our message
        max_length = 40
        if (len(msg) > max_length):
            return ('Message contains more than %s characters and may not be accepted.' % str(max_length), 404)
        message_script = Script('OP_RETURN 0x{}'.format(utils.bytes_to_str(msg.encode())))
    
        # Define the fee we're willing to pay for the tx
        tx_fee = 3000
    
        # Get the first UTXO from our set that can cover the fee
        utxo = None
        for utxo_addr, utxos in wallet.get_utxos().items():
            for u in utxos:
                if u.value > tx_fee:
                    utxo = u
                    break
            if utxo:
                break
    
        if not utxo:
            return ('No confirmed UTXOs available to pay for the transaction.', 404)
    
        # Build the transaction inputs (there is only one, but Transaction expects a list)
        inputs = [TransactionInput(outpoint=utxo.transaction_hash,
                                   outpoint_index=utxo.outpoint_index,
                                   script=utxo.script,
                                   sequence_num=0xffffffff)]
    
        outputs = []
        # Build one output with our custom message script
        outputs.append(TransactionOutput(value=0, script=message_script))
        # Build another output to pay the UTXO money back to one of our addresses
        _, change_key_hash = utils.address_to_key_hash(wallet._accounts[0].get_next_address(True))
        outputs.append(TransactionOutput(value=utxo.value - tx_fee,
                                         script=Script.build_p2pkh(change_key_hash)))
    
        # Build an unsigned transaction object
        txn = Transaction(version=Transaction.DEFAULT_TRANSACTION_VERSION,
                          inputs=inputs,
                          outputs=outputs,
                          lock_time=0)
    
        # Sign the transaction with the correct private key
        private_key = wallet.get_private_key(utxo_addr)
        signed = txn.sign_input(input_index=0,
                                hash_type=Transaction.SIG_HASH_ALL,
                                private_key=private_key,
                                sub_script=utxo.script)
    
        # Broadcast the transaction
        tx = wallet.broadcast_transaction(txn.to_hex())
        return tx
    
    if __name__ == '__main__':
        app.run(host='0.0.0.0')
    

As soon as `21 status` shows a nonzero "spendable balance
on the Blockchain", start the micropayments server:

    
    python3 notary-server.py
    

Your bitcoin-enabled notary web-service is up and running! Let's
create a client to purchase your notary service for a bitcoin
micropayment.

## Step 3: Log in as the client user and purchase the endpoint

Leave your `twenty-server` session open, but open a new
terminal on your regular computer/laptop (or PuTTY session on Windows)
and SSH into your 21 Bitcoin Computer, this time as the
`twenty-client` user.

As the `twenty-client` user, create a new directory and a file called
`notary-client.py`:

    
    cd $HOME
    mkdir notary-client
    cd notary-client
    touch notary-client.py
    

Open the `notary-client.py` file in your text editor and type in the
following code:

    
    import sys
    import urllib.parse
    
    # import from the 21 Developer Library
    from two1.commands.config import Config
    from two1.lib.wallet import Wallet
    from two1.lib.bitrequests import BitTransferRequests
    
    wallet = Wallet()
    
    def write_message(raw_msg):
        msg = urllib.parse.quote_plus(raw_msg)
        requests = BitTransferRequests(wallet, Config().username)
    
        # purchase the bitcoin payable endpoint
        response = requests.get('http://localhost:5000/write-message?message={}'.format(msg))
    
        # return error if there's any
        if response.status_code != 200:
            print("The server returned an error")
            print("Status code: {}".format(response.status_code))
            print("Message: {}".format(response.text))
            exit(1)
    
        # print out the transaction
        print("Transaction: {}".format(response.text))
        print("View it live at https://live.blockcypher.com/btc/tx/{}".format(response.text))
    
    if __name__=='__main__':
        write_message(sys.argv[1])
    

Close the file and run the client script:

    
    python3 notary-client.py "Carving my name into the blockchain"
    

Congratulations, you just wrote a message to the blockchain that will
be stored there permanently! Here's an an example transaction visible
on [blockcypher][140].

## Next Steps

It's worth tracing through exactly how this worked:

* First, we wrote a message. Our message was encoded in the script of
an output after an `OP_RETURN` instruction, which tells bitcoin
nodes that this output cannot be used as an input for another
transaction. Note that many nodes will reject a transaction if
there is more than 40 bytes of data after an `OP_RETURN`. This
will be extended to 80 bytes as Bitcoin Core 0.12.0 becomes
standard.
* 
Then, we created inputs. To build an input, we needed an unspent
transaction output (UTXO), which is essentially just spendable
bitcoin that we have in our wallet. We had to include a fee for
miners, so we made sure our UTXO was large enough to cover it.
* 
Next, we created outputs. One of our transaction outputs will be
our message, and another output will send our own money (the
change) back to our wallet.
* 
Next, we built and signed the transaction. We combined the inputs
and outputs into a transaction and signed it.
* 
Broadcasting the transaction. Last but not least, we got the word
out by broadcasting the transaction to the bitcoin network.

This example mixes concepts from the
[Bitcoin Payable API][21] tutorial and the
[Bitcoin Library][141] tutorials, showing how to build
bitcoin-payable APIs that manipulate bitcoin data structures and write
to the blockchain - therefore actually "costing bitcoin" in an
intrinsic sense. As a next step, you might investigate the
[Library and Wallet][141] tutorials.

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
browse and purchase from other bitcoin-enabled servers? Head over to the [21 Developer Community][142] at slack.21.co to join the bitcoin machine-payable marketplace hosted on the 21 peer-to-peer
network.

---

# Next :

## [Build More Bitcoin Apps][2]

[![Next](https://assets.21.co/setup/img/next_app.png)][2]

Check out all the Bitcoin Apps you can build with the 21 Bitcoin Computer.

[See more apps][2]

[![Next](https://assets.21.co/setup/img/next_app.png)][2]


---

*Content authored by Tyler Julian  |  Markdown created by PK Rasam* 

If you have any questions or issues, please drop us a line at [\[email protected\] ][144] or join our [Slack ][4] community.

This content is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License][145].


(c) 2016, 21.co

[Get The 21 Bitcoin Computer][3]


[0]: /
[1]: /setup/
[2]: /learn/
[3]: /buy/
[4]: https://slack.21.co
[5]: /bitnodes/
[6]: /about/
[7]: #a-bitcoin-payable-notary-public "A Bitcoin-Payable Notary Public"
[8]: #overview "Overview"
[9]: #prerequisites "Prerequisites"
[10]: #step-1-set-up-client-and-server-accounts "Step 1: Set up client and server accounts."
[11]: #step-2-log-in-as-the-server-user-and-start-the-server "Step 2: Log in as the server user and start the server"
[12]: #step-3-log-in-as-the-client-user-and-purchase-the-endpoint "Step 3: Log in as the client user and purchase the endpoint"
[13]: #next-steps "Next Steps"
[14]: /learn/ "< Back To Index"
[15]: https://twitter.com/intent/tweet?text=Hmm. This looks like a good resource for learning how to build Bitcoin apps:&url=https%3A//21.co/learn/bitcoin-notary-public/
[16]: https://www.facebook.com/sharer/sharer.php?u=https%3A//21.co/learn/bitcoin-notary-public/
[17]: /cdn-cgi/l/email-protection#a39c85d0d6c1c9c6c0d79ef7cbcad083cfccccc8d083cfcac8c683c283c4ccccc783d1c6d0ccd6d1c0c683c5ccd183cfc6c2d1cdcacdc483cbccd483d7cc83c1d6caXld Bitcoin apps&body=Here's the URL: https%3A//21.co/learn/bitcoin-notary-public/
[18]: /setup
[19]: ../introduction-to-the-21-bitcoin-computer/
[20]: ../21-multiple-users
[21]: ../bitcoin-payable-api
[22]: #code-7f8d93708118edb3fe8f0155cc036ca47c5a0aea-1
[23]: #code-7f8d93708118edb3fe8f0155cc036ca47c5a0aea-2
[24]: #code-7f8d93708118edb3fe8f0155cc036ca47c5a0aea-3
[25]: #code-9600f4a4e2499bfdf066acd4bdb48780864e7da1-1
[26]: #code-9600f4a4e2499bfdf066acd4bdb48780864e7da1-2
[27]: #code-042bf9c12b85f615620927758e7117051f84802f-1
[28]: #code-042bf9c12b85f615620927758e7117051f84802f-2
[29]: #code-042bf9c12b85f615620927758e7117051f84802f-3
[30]: #code-042bf9c12b85f615620927758e7117051f84802f-4
[31]: #code-042bf9c12b85f615620927758e7117051f84802f-5
[32]: #code-042bf9c12b85f615620927758e7117051f84802f-6
[33]: #code-042bf9c12b85f615620927758e7117051f84802f-7
[34]: #code-042bf9c12b85f615620927758e7117051f84802f-8
[35]: #code-042bf9c12b85f615620927758e7117051f84802f-9
[36]: #code-042bf9c12b85f615620927758e7117051f84802f-10
[37]: #code-042bf9c12b85f615620927758e7117051f84802f-11
[38]: #code-042bf9c12b85f615620927758e7117051f84802f-12
[39]: #code-042bf9c12b85f615620927758e7117051f84802f-13
[40]: #code-042bf9c12b85f615620927758e7117051f84802f-14
[41]: #code-042bf9c12b85f615620927758e7117051f84802f-15
[42]: #code-042bf9c12b85f615620927758e7117051f84802f-16
[43]: #code-042bf9c12b85f615620927758e7117051f84802f-17
[44]: #code-042bf9c12b85f615620927758e7117051f84802f-18
[45]: #code-042bf9c12b85f615620927758e7117051f84802f-19
[46]: #code-042bf9c12b85f615620927758e7117051f84802f-20
[47]: #code-042bf9c12b85f615620927758e7117051f84802f-21
[48]: #code-042bf9c12b85f615620927758e7117051f84802f-22
[49]: #code-042bf9c12b85f615620927758e7117051f84802f-23
[50]: #code-042bf9c12b85f615620927758e7117051f84802f-24
[51]: #code-042bf9c12b85f615620927758e7117051f84802f-25
[52]: #code-042bf9c12b85f615620927758e7117051f84802f-26
[53]: #code-042bf9c12b85f615620927758e7117051f84802f-27
[54]: #code-042bf9c12b85f615620927758e7117051f84802f-28
[55]: #code-042bf9c12b85f615620927758e7117051f84802f-29
[56]: #code-042bf9c12b85f615620927758e7117051f84802f-30
[57]: #code-042bf9c12b85f615620927758e7117051f84802f-31
[58]: #code-042bf9c12b85f615620927758e7117051f84802f-32
[59]: #code-042bf9c12b85f615620927758e7117051f84802f-33
[60]: #code-042bf9c12b85f615620927758e7117051f84802f-34
[61]: #code-042bf9c12b85f615620927758e7117051f84802f-35
[62]: #code-042bf9c12b85f615620927758e7117051f84802f-36
[63]: #code-042bf9c12b85f615620927758e7117051f84802f-37
[64]: #code-042bf9c12b85f615620927758e7117051f84802f-38
[65]: #code-042bf9c12b85f615620927758e7117051f84802f-39
[66]: #code-042bf9c12b85f615620927758e7117051f84802f-40
[67]: #code-042bf9c12b85f615620927758e7117051f84802f-41
[68]: #code-042bf9c12b85f615620927758e7117051f84802f-42
[69]: #code-042bf9c12b85f615620927758e7117051f84802f-43
[70]: #code-042bf9c12b85f615620927758e7117051f84802f-44
[71]: #code-042bf9c12b85f615620927758e7117051f84802f-45
[72]: #code-042bf9c12b85f615620927758e7117051f84802f-46
[73]: #code-042bf9c12b85f615620927758e7117051f84802f-47
[74]: #code-042bf9c12b85f615620927758e7117051f84802f-48
[75]: #code-042bf9c12b85f615620927758e7117051f84802f-49
[76]: #code-042bf9c12b85f615620927758e7117051f84802f-50
[77]: #code-042bf9c12b85f615620927758e7117051f84802f-51
[78]: #code-042bf9c12b85f615620927758e7117051f84802f-52
[79]: #code-042bf9c12b85f615620927758e7117051f84802f-53
[80]: #code-042bf9c12b85f615620927758e7117051f84802f-54
[81]: #code-042bf9c12b85f615620927758e7117051f84802f-55
[82]: #code-042bf9c12b85f615620927758e7117051f84802f-56
[83]: #code-042bf9c12b85f615620927758e7117051f84802f-57
[84]: #code-042bf9c12b85f615620927758e7117051f84802f-58
[85]: #code-042bf9c12b85f615620927758e7117051f84802f-59
[86]: #code-042bf9c12b85f615620927758e7117051f84802f-60
[87]: #code-042bf9c12b85f615620927758e7117051f84802f-61
[88]: #code-042bf9c12b85f615620927758e7117051f84802f-62
[89]: #code-042bf9c12b85f615620927758e7117051f84802f-63
[90]: #code-042bf9c12b85f615620927758e7117051f84802f-64
[91]: #code-042bf9c12b85f615620927758e7117051f84802f-65
[92]: #code-042bf9c12b85f615620927758e7117051f84802f-66
[93]: #code-042bf9c12b85f615620927758e7117051f84802f-67
[94]: #code-042bf9c12b85f615620927758e7117051f84802f-68
[95]: #code-042bf9c12b85f615620927758e7117051f84802f-69
[96]: #code-042bf9c12b85f615620927758e7117051f84802f-70
[97]: #code-042bf9c12b85f615620927758e7117051f84802f-71
[98]: #code-042bf9c12b85f615620927758e7117051f84802f-72
[99]: #code-042bf9c12b85f615620927758e7117051f84802f-73
[100]: #code-042bf9c12b85f615620927758e7117051f84802f-74
[101]: #code-042bf9c12b85f615620927758e7117051f84802f-75
[102]: #code-042bf9c12b85f615620927758e7117051f84802f-76
[103]: #code-042bf9c12b85f615620927758e7117051f84802f-77
[104]: #code-042bf9c12b85f615620927758e7117051f84802f-78
[105]: #code-042bf9c12b85f615620927758e7117051f84802f-79
[106]: #code-0ffeffcd7fe62664ccf026317580a7ac2802c6ce-1
[107]: #code-0ffeffcd7fe62664ccf026317580a7ac2802c6ce-2
[108]: #code-0ffeffcd7fe62664ccf026317580a7ac2802c6ce-3
[109]: #code-0ffeffcd7fe62664ccf026317580a7ac2802c6ce-4
[110]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-1
[111]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-2
[112]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-3
[113]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-4
[114]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-5
[115]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-6
[116]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-7
[117]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-8
[118]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-9
[119]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-10
[120]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-11
[121]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-12
[122]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-13
[123]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-14
[124]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-15
[125]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-16
[126]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-17
[127]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-18
[128]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-19
[129]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-20
[130]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-21
[131]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-22
[132]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-23
[133]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-24
[134]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-25
[135]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-26
[136]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-27
[137]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-28
[138]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-29
[139]: #code-b8c2eabef88fb2305f81c7b5884f2fd8ad01a594-30
[140]: https://live.blockcypher.com/btc/tx/654e92898b5b5a0b14db92bf4738de91318b922d159db0030d6b14e42dfb963f/
[141]: /learn/#reference
[142]: https://slack.21.co/
[143]: /cdn-cgi/l/email-protection#4e71683d3b2c242b2d3a731a26273d6e222121253d6e2227252b6e2f6e2921212a6e3c2b3d213b3c2d2b6e28213c6e222b2f3c202720296e2621396e3a216e2c3b27Xld Bitcoin apps&body=Here's the URL: https%3A//21.co/learn/bitcoin-notary-public/
[144]: /cdn-cgi/l/email-protection#e0939590908f9294a0d2d1ce838f
[145]: https://creativecommons.org/licenses/by-sa/4.0/
[146]: //twitter.com/21
[147]: //medium.com/@21
