[![21.co](https://assets.21.co/shared/img/21logo.png)21 Inc][0]

# [Setup][1] | [Tutorials][2] | [Buy][3] | [Community][4] | [Nodes][5] | [About][6]


# Bitcoin-Accelerated Computing
*Content authored by John Granata  |  Markdown created by PK Rasam* 
  

* [Bitcoin-Accelerated Computing][7]
  * [Overview][8]
  * [Prerequisites][9]
  * [Step 1: Set up client and server accounts.][10]
  * [Step 2: Set up a bitcoin-payable API server][11]
  * [Step 3: Use the client's bitcoin to buy API calls from the server][12]
  * [Next Steps][13]
* [< Back To Index][14]

# Bitcoin-Accelerated Computing

## Overview

This tutorial will introduce you to the concept of bitcoin-accelerated
computing. You'll learn how a client can use bitcoin to outsource a
large computation to a server, and build your first intelligent
agent. Specifically, here are the steps you will follow:

* First, you will set up a bitcoin-payable API server
* Then, you will set up a client with some bitcoin
* Your client will then spend bitcoin to buy an API call from the
server, speeding up a local computation
* You will then set up a _second_ bitcoin-payable API server at a
different price, and modify your client to buy from the
lowest-priced bidder in realtime - thus creating an intelligent
agent.

Once you've gone through those steps, you will start to see how
bitcoin can be used as a lubricant for machine-to-machine transactions
and a powerful way to monetize spare computer time.

## Prerequisites

You will need the following first:

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

## Step 2: Set up a bitcoin-payable API server

SSH into your 21 Bitcoin Computer as `twenty-server`:

    
    ssh twenty-server@<IP Address>
    

Then create a folder to house the server project:

    
    mkdir bitcoin-aware-computing-server1 && cd bitcoin-aware-computing-server1
    

Go to this directory and open a file named `server1.py` in your text
editor. Add the following code to it:

    
    import json
    
    from flask import Flask, request
    
    # import from the 21 Bitcoin Developer Library
    from two1.lib.wallet import Wallet
    from two1.lib.bitserv.flask import Payment
    
    app = Flask(__name__)
    wallet = Wallet()
    payment = Payment(app, wallet)
    
    # sort method w/out delay simulates faster computation server
    def fast_get_element(arr, prop, val):
        for elem in arr:
            if elem[prop] == val:
                return elem
    
    def get_array_to_sort(request):
        return json.loads(request.form.getlist("array")[0])
    
    @app.route('/fastfind', methods=['GET','POST'])
    @payment.required(800)
    def fast_get_elem():
        arr = get_array_to_sort(request)
        prop = request.form.getlist("property")[0]
        value = int(request.form.getlist("value")[0])
        res = fast_get_element( arr, prop, value )
        return json.dumps({"elem": str(res)})
    
    # set up and run the server
    if __name__ == '__main__':
        app.run(host='0.0.0.0')
    

Start your micropayments server:

    
    python3 server1.py
    

Your bitcoin-payable API is up and running on your 21 Bitcoin
Computer!

## Step 3: Use the client's bitcoin to buy API calls from the server

Leaving the old session alive, open a new SSH session into your 21
Bitcoin Computer as `twenty-client`:

    
    ssh twenty-client@<IP Address>
    

Create a folder to house the client project:

    
    mkdir bitcoin-aware-computing-client && cd bitcoin-aware-computing-client
    

Open up a file named `client.py` and type in the following code:

    
    import json
    import time
    import subprocess
    
    # import from 21 developer library
    import two1.commands.status
    from two1.lib.server import rest_client
    from two1.commands.config import TWO1_HOST
    from two1.commands.config import Config
    from two1.lib.wallet import Wallet
    from two1.lib.bitrequests import BitTransferRequests
    
    # set up wallet proxy
    wallet = Wallet()
    
    # read local user account data
    config = Config()
    username = Config().username
    
    # initialize rest client to communicate with 21.co API
    client = rest_client.TwentyOneRestClient(TWO1_HOST, config.machine_auth, config.username)
    
    # set up bitrequests client using BitTransfer payment method for managing 402 requests
    requests = BitTransferRequests(wallet, username)
    
    # check the spot price for our api call
    response = requests.get_402_info(url='http://localhost:5000/fastfind')
    endpoint_info = dict(response)
    price = int(endpoint_info['price'])
    print(endpoint_info)
    

If you run this code with `python3 client.py` you will see something
like this (the exact values will be different):

    
    {'bitcoin-address': '14MrUbDsHZmpVUUsN2s8zzy4KzRjy3Hhnp', 'price': '5000', 'username': 'testuser1'}
    

Now let's compute something. First, let's write a program that
accelerates our computation if we have enough bitcoin to
pay for the call. We'll define a local method that returns the first
object with a certain property from an array, and we'll also define a
bitcoin-aware version of this method that sends the data to the cloud
for faster processing. Add the following to `client.py`

    
    # slow local method
    def get_element(arr, prop, val):
        for elem in arr:
            if elem[prop] == val:
                return elem
            time.sleep(1)
    
    # fast bitcoin-aware api NOx
    def fast_get_element(arr, prop, val):
        body = {
            'array': json.dumps(arr),
            'property': prop,
            'value': val
        }
        res = requests.post(url='http://localhost:5000/fastfind', data=body)
        return json.loads(res.text)['elem']
    

Let's define some sample data, and time how long the local method call
takes vs. the machine-payable call. First we'll do the local method
call:

    
    # sample data
    data1 = [
        {'height': 4},
        {'height': 3},
        {'height': 6},
        {'height': 4},
        {'height': 3},
        {'height': 6},
        {'height': 4},
        {'height': 3},
        {'height': 6},
        {'height': 10},
    ]
    
    # first let's try the slow local method
    t0 = time.time()
    a = get_element(data1, 'height', 10)
    t1 = time.time()
    
    # print results of local call
    print(a)
    print("Execution time: " + str(t1-t0))
    

Example Output:

    
    {'height': 10}
    Execution time: 9.02669906616212
    

Now, let's accelerate the computation if we have enough BTC to afford it:

    
    # get user's 21.co balance
    bal = client.get_earnings()
    twentyone_balance = bal["total_earnings"]
    
    t0 = time.time()
    if twentyone_balance > price:
        a = fast_get_element(data1, 'height', 10)  # buy the api call
    else:
        a = get_element(data1, 'height', 10)  # locally execute the method
    
    t1 = time.time()
    print(a)
    print("Execution time: " + str(t1-t0))
    

Example Output:

    
    {'height': 10}
    Execution time: 5.5479278564453125
    

We can check our balance to see if we were debited the amount we paid:

    
    bal = client.get_earnings()
    print(bal["total_earnings"])
    

Let's define a slightly larger dataset:

    
    # larger sample data
    data2 = [
        {'height': 4},
        {'height': 3},
        {'height': 6},
        {'height': 7},
        {'height': 2},
        {'height': 4},
        {'height': 4},
        {'height': 3},
        {'height': 6},
        {'height': 7},
        {'height': 2},
        {'height': 4},
        {'height': 10}
    ]
    

Now, our program will call the local method or the machine-payable
api based on the dataset size. First we'll pass in the smaller
dataset (data1) from earlier.

    
    # accelerate computation as a function of dataset size
    data = data1;
    t0 = time.time()
    if len(data) <= 10:
        a = get_element(data, 'height', 10)
    else:
        a = fast_get_element(data, 'height', 10)
    
    t1 = time.time()
    print(a)
    print("Execution time: " + str(t1-t0))
    

Example Output:

    
    {'height': 10}
    Execution time: 9.02669906616211
    

Now we'll pass in the larger dataset, which will trigger the
bitcoin-powered api call:

    
    data = data2;
    t0 = time.time()
    if len(data) <= 10:
        a = get_element(data, 'height', 10)
    else:
        a = fast_get_element(data, 'height', 10)
    
    t1 = time.time()
    print(a)
    print("Execution time: " + str(t1-t0))
    

Example Output:

    
    {'height': 10}
    Execution time: 5.5479278564453126
    

In this simple example, the bitcoin-aware code saves several
seconds over the local function call.

## Next Steps

To recap, this tutorial explained the concept of bitcoin-accelerated
computing.

As background, one of the key concepts in mobile development is the
concept of
["power-aware computing"][182]. In
a power-constrained environment, power is a scarce resource. You can
spend more power to run an algorithm quickly, or you can spend less
power to run an algorithm more slowly.

In the same way, the 21 Bitcoin Computer introduces the idea of
"bitcoin-accelerated computing". A typical computer has no
bitcoin. But if you do have some bitcoin, you can choose whether to
spend more bitcoin to run an algorithm quickly on a remote server, or
spend less (or 0) bitcoin to run the algorithm more slowly on a local
server.

The key concept is that once you have both a client that generates
bitcoin and a server that accepts bitcoin, the client can send bitcoin
to the server to perform computations remotely, thereby spending
digital currency to save time. We dub this a "cloud call" or
"bitcoin-accelerated computing".

Because this process is fully programmable, you can do it
conditionally. For example, you can choose whether or not to
outsource a particular problem for bitcoin based on the size of the
input data set, your expected future workload, or the spot price of
the remote server.

Perhaps most interestingly, you can do it based on the spot price of
_multiple_ remote servers -- thereby developing a simple intelligent
agent that chooses which endpoint provider to purchase from based on
their current bitcoin price.

And that's the next step. Now that you've finished this tutorial, you
can learn how to build an
[intelligent agent with bitcoin][183].

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
browse and purchase from other bitcoin-enabled servers? Head over to the [21 Developer Community][184] at slack.21.co to join the bitcoin machine-payable marketplace hosted on the 21 peer-to-peer
network.

---

# Next :

## [Build More Bitcoin Apps][2]

[![Next](https://assets.21.co/setup/img/next_app.png)][2]

Check out all the Bitcoin Apps you can build with the 21 Bitcoin Computer.

[See more apps][2]

[![Next](https://assets.21.co/setup/img/next_app.png)][2]


---

*Content authored by John Granata  |  Markdown created by PK Rasam* 

If you have any questions or issues, please drop us a line at [\[email protected\] ][186] or join our [Slack ][4] community.

This content is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License][187].


(c) 2016, 21.co

[Get The 21 Bitcoin Computer][3]


[0]: /
[1]: /setup/
[2]: /learn/
[3]: /buy/
[4]: https://slack.21.co
[5]: /bitnodes/
[6]: /about/
[7]: #bitcoin-accelerated-computing "Bitcoin-Accelerated Computing"
[8]: #overview "Overview"
[9]: #prerequisites "Prerequisites"
[10]: #step-1-set-up-client-and-server-accounts "Step 1: Set up client and server accounts."
[11]: #step-2-set-up-a-bitcoin-payable-api-server "Step 2: Set up a bitcoin-payable API server"
[12]: #step-3-use-the-clients-bitcoin-to-buy-api-calls-from-the-server "Step 3: Use the client's bitcoin to buy API calls from the server"
[13]: #next-steps "Next Steps"
[14]: /learn/ "< Back To Index"
[15]: https://twitter.com/intent/tweet?text=Hmm. This looks like a good resource for learning how to build Bitcoin apps:&url=https%3A//21.co/learn/bitcoin-accelerated-computing/
[16]: https://www.facebook.com/sharer/sharer.php?u=https%3A//21.co/learn/bitcoin-accelerated-computing/
[17]: /cdn-cgi/l/email-protection#211e075254434b4442551c75494852014d4e4e4a52014d484a44014001464e4e45015344524e5453424401474e53014d4440534f484f4601494e5601554e01435448Xld Bitcoin apps&body=Here's the URL: https%3A//21.co/learn/bitcoin-accelerated-computing/
[18]: /setup
[19]: ../introduction-to-the-21-bitcoin-computer/
[20]: ../21-multiple-users
[21]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-1
[22]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-2
[23]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-3
[24]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-4
[25]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-5
[26]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-6
[27]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-7
[28]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-8
[29]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-9
[30]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-10
[31]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-11
[32]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-12
[33]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-13
[34]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-14
[35]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-15
[36]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-16
[37]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-17
[38]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-18
[39]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-19
[40]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-20
[41]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-21
[42]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-22
[43]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-23
[44]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-24
[45]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-25
[46]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-26
[47]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-27
[48]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-28
[49]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-29
[50]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-30
[51]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-31
[52]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-32
[53]: #code-875fcccc39c6c8227104e11c5aa37468ec55c222-33
[54]: #code-94ef744208feeacf45f97e5b28996469e904f856-1
[55]: #code-94ef744208feeacf45f97e5b28996469e904f856-2
[56]: #code-94ef744208feeacf45f97e5b28996469e904f856-3
[57]: #code-94ef744208feeacf45f97e5b28996469e904f856-4
[58]: #code-94ef744208feeacf45f97e5b28996469e904f856-5
[59]: #code-94ef744208feeacf45f97e5b28996469e904f856-6
[60]: #code-94ef744208feeacf45f97e5b28996469e904f856-7
[61]: #code-94ef744208feeacf45f97e5b28996469e904f856-8
[62]: #code-94ef744208feeacf45f97e5b28996469e904f856-9
[63]: #code-94ef744208feeacf45f97e5b28996469e904f856-10
[64]: #code-94ef744208feeacf45f97e5b28996469e904f856-11
[65]: #code-94ef744208feeacf45f97e5b28996469e904f856-12
[66]: #code-94ef744208feeacf45f97e5b28996469e904f856-13
[67]: #code-94ef744208feeacf45f97e5b28996469e904f856-14
[68]: #code-94ef744208feeacf45f97e5b28996469e904f856-15
[69]: #code-94ef744208feeacf45f97e5b28996469e904f856-16
[70]: #code-94ef744208feeacf45f97e5b28996469e904f856-17
[71]: #code-94ef744208feeacf45f97e5b28996469e904f856-18
[72]: #code-94ef744208feeacf45f97e5b28996469e904f856-19
[73]: #code-94ef744208feeacf45f97e5b28996469e904f856-20
[74]: #code-94ef744208feeacf45f97e5b28996469e904f856-21
[75]: #code-94ef744208feeacf45f97e5b28996469e904f856-22
[76]: #code-94ef744208feeacf45f97e5b28996469e904f856-23
[77]: #code-94ef744208feeacf45f97e5b28996469e904f856-24
[78]: #code-94ef744208feeacf45f97e5b28996469e904f856-25
[79]: #code-94ef744208feeacf45f97e5b28996469e904f856-26
[80]: #code-94ef744208feeacf45f97e5b28996469e904f856-27
[81]: #code-94ef744208feeacf45f97e5b28996469e904f856-28
[82]: #code-94ef744208feeacf45f97e5b28996469e904f856-29
[83]: #code-94ef744208feeacf45f97e5b28996469e904f856-30
[84]: #code-0a5890270bb34242fddd67361660725d38adbe58-1
[85]: #code-0a5890270bb34242fddd67361660725d38adbe58-2
[86]: #code-0a5890270bb34242fddd67361660725d38adbe58-3
[87]: #code-0a5890270bb34242fddd67361660725d38adbe58-4
[88]: #code-0a5890270bb34242fddd67361660725d38adbe58-5
[89]: #code-0a5890270bb34242fddd67361660725d38adbe58-6
[90]: #code-0a5890270bb34242fddd67361660725d38adbe58-7
[91]: #code-0a5890270bb34242fddd67361660725d38adbe58-8
[92]: #code-0a5890270bb34242fddd67361660725d38adbe58-9
[93]: #code-0a5890270bb34242fddd67361660725d38adbe58-10
[94]: #code-0a5890270bb34242fddd67361660725d38adbe58-11
[95]: #code-0a5890270bb34242fddd67361660725d38adbe58-12
[96]: #code-0a5890270bb34242fddd67361660725d38adbe58-13
[97]: #code-0a5890270bb34242fddd67361660725d38adbe58-14
[98]: #code-0a5890270bb34242fddd67361660725d38adbe58-15
[99]: #code-0a5890270bb34242fddd67361660725d38adbe58-16
[100]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-1
[101]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-2
[102]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-3
[103]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-4
[104]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-5
[105]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-6
[106]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-7
[107]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-8
[108]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-9
[109]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-10
[110]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-11
[111]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-12
[112]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-13
[113]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-14
[114]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-15
[115]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-16
[116]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-17
[117]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-18
[118]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-19
[119]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-20
[120]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-21
[121]: #code-905eb44ce25e5aa004a37646f2af47b154a4ca51-22
[122]: #code-e35e827c2a7540f0262dbf606e26f18e712c0b96-1
[123]: #code-e35e827c2a7540f0262dbf606e26f18e712c0b96-2
[124]: #code-d00097e010cb2b85313fa87979b1bde9cd591c05-1
[125]: #code-d00097e010cb2b85313fa87979b1bde9cd591c05-2
[126]: #code-d00097e010cb2b85313fa87979b1bde9cd591c05-3
[127]: #code-d00097e010cb2b85313fa87979b1bde9cd591c05-4
[128]: #code-d00097e010cb2b85313fa87979b1bde9cd591c05-5
[129]: #code-d00097e010cb2b85313fa87979b1bde9cd591c05-6
[130]: #code-d00097e010cb2b85313fa87979b1bde9cd591c05-7
[131]: #code-d00097e010cb2b85313fa87979b1bde9cd591c05-8
[132]: #code-d00097e010cb2b85313fa87979b1bde9cd591c05-9
[133]: #code-d00097e010cb2b85313fa87979b1bde9cd591c05-10
[134]: #code-d00097e010cb2b85313fa87979b1bde9cd591c05-11
[135]: #code-d00097e010cb2b85313fa87979b1bde9cd591c05-12
[136]: #code-d00097e010cb2b85313fa87979b1bde9cd591c05-13
[137]: #code-b90dc1a6e6d376e250f90a73a3c2ceac9ba6a3a9-1
[138]: #code-b90dc1a6e6d376e250f90a73a3c2ceac9ba6a3a9-2
[139]: #code-6212a2437333156e59f7cd26d2c8980529e579fa-1
[140]: #code-6212a2437333156e59f7cd26d2c8980529e579fa-2
[141]: #code-0ec96624b6c5eb864ad769b6c20246cb4dcf9d01-1
[142]: #code-0ec96624b6c5eb864ad769b6c20246cb4dcf9d01-2
[143]: #code-0ec96624b6c5eb864ad769b6c20246cb4dcf9d01-3
[144]: #code-0ec96624b6c5eb864ad769b6c20246cb4dcf9d01-4
[145]: #code-0ec96624b6c5eb864ad769b6c20246cb4dcf9d01-5
[146]: #code-0ec96624b6c5eb864ad769b6c20246cb4dcf9d01-6
[147]: #code-0ec96624b6c5eb864ad769b6c20246cb4dcf9d01-7
[148]: #code-0ec96624b6c5eb864ad769b6c20246cb4dcf9d01-8
[149]: #code-0ec96624b6c5eb864ad769b6c20246cb4dcf9d01-9
[150]: #code-0ec96624b6c5eb864ad769b6c20246cb4dcf9d01-10
[151]: #code-0ec96624b6c5eb864ad769b6c20246cb4dcf9d01-11
[152]: #code-0ec96624b6c5eb864ad769b6c20246cb4dcf9d01-12
[153]: #code-0ec96624b6c5eb864ad769b6c20246cb4dcf9d01-13
[154]: #code-0ec96624b6c5eb864ad769b6c20246cb4dcf9d01-14
[155]: #code-0ec96624b6c5eb864ad769b6c20246cb4dcf9d01-15
[156]: #code-0ec96624b6c5eb864ad769b6c20246cb4dcf9d01-16
[157]: #code-6f1663eb539f72efdcee5a9d9a382dc90d35e8db-1
[158]: #code-6f1663eb539f72efdcee5a9d9a382dc90d35e8db-2
[159]: #code-6f1663eb539f72efdcee5a9d9a382dc90d35e8db-3
[160]: #code-6f1663eb539f72efdcee5a9d9a382dc90d35e8db-4
[161]: #code-6f1663eb539f72efdcee5a9d9a382dc90d35e8db-5
[162]: #code-6f1663eb539f72efdcee5a9d9a382dc90d35e8db-6
[163]: #code-6f1663eb539f72efdcee5a9d9a382dc90d35e8db-7
[164]: #code-6f1663eb539f72efdcee5a9d9a382dc90d35e8db-8
[165]: #code-6f1663eb539f72efdcee5a9d9a382dc90d35e8db-9
[166]: #code-6f1663eb539f72efdcee5a9d9a382dc90d35e8db-10
[167]: #code-6f1663eb539f72efdcee5a9d9a382dc90d35e8db-11
[168]: #code-9e53d52641c71093b9cc6844e58b76873563ae49-1
[169]: #code-9e53d52641c71093b9cc6844e58b76873563ae49-2
[170]: #code-81763e117e18812406a1021bc1b3f7c1125aff5c-1
[171]: #code-81763e117e18812406a1021bc1b3f7c1125aff5c-2
[172]: #code-81763e117e18812406a1021bc1b3f7c1125aff5c-3
[173]: #code-81763e117e18812406a1021bc1b3f7c1125aff5c-4
[174]: #code-81763e117e18812406a1021bc1b3f7c1125aff5c-5
[175]: #code-81763e117e18812406a1021bc1b3f7c1125aff5c-6
[176]: #code-81763e117e18812406a1021bc1b3f7c1125aff5c-7
[177]: #code-81763e117e18812406a1021bc1b3f7c1125aff5c-8
[178]: #code-81763e117e18812406a1021bc1b3f7c1125aff5c-9
[179]: #code-81763e117e18812406a1021bc1b3f7c1125aff5c-10
[180]: #code-bf90bb667ab466399e89dc6d0f04bcbee15a2594-1
[181]: #code-bf90bb667ab466399e89dc6d0f04bcbee15a2594-2
[182]: http://www.cs.virginia.edu/~skadron/Papers/power_aware_intro_computer03.pdf
[183]: ../intelligent-agents-with-bitcoin
[184]: https://slack.21.co/
[185]: /cdn-cgi/l/email-protection#6d524b1e180f07080e19503905041e4d010202061e4d010406084d0c4d0a0202094d1f081e02181f0e084d0b021f4d01080c1f0304030a4d05021a4d19024d0f1804Xld Bitcoin apps&body=Here's the URL: https%3A//21.co/learn/bitcoin-accelerated-computing/
[186]: /cdn-cgi/l/email-protection#24575154544b56506416150a474b
[187]: https://creativecommons.org/licenses/by-sa/4.0/
[188]: //twitter.com/21
[189]: //medium.com/@21
