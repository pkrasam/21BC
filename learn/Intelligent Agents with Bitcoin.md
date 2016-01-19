[![21.co](https://assets.21.co/shared/img/21logo.png)21 Inc][0]

# [Setup][1] | [Tutorials][2] | [Buy][3] | [Community][4] | [Nodes][5] | [About][6]


# Intelligent Agents with Bitcoin 
*Content authored by John Granata  |  Markdown created by PK Rasam* 


* [Intelligent Agents with Bitcoin][7]
  * [Overview][8]
  * [Prerequisites][9]
  * [Step 1: Set up a bitcoin-accelerated computing endpoint][10]
  * [Step 2: Add a competitor endpoint-provider to the market][11]
  * [Step 3: Create an intelligent agent that searches for the lowest-priced API][12]
  * [Next Steps][13]
* [< Back To Index][14]

# Intelligent Agents with Bitcoin

## Overview

This tutorial will introduce you to the concept of bitcoin-powered
intelligent agents. You'll learn how a client can use bitcoin to
outsource a large computation to a server, and build your first
intelligent agent. Specifically, here are the steps you will follow:

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
* Do the [Bitcoin Accelerated Computing][21] tutorial

If you've got all the prerequisites, you are ready to go. Let's get
started!

## Step 1: Set up a bitcoin-accelerated computing endpoint

You should go through all the steps in the
[Bitcoin Accelerated Computing][21]
tutorial. In particular, you should have the `server1.py` code running
under the `twenty-server` user.

## Step 2: Add a competitor endpoint-provider to the market

Now we will set up a second merchant server to sell the same endpoint
for bitcoin. Connect to your 21 Bitcoin Computer as the
`twenty-server-2` user that you set up in the
[Introduction to the 21 Bitcoin Computer][19]
tutorial.

Create a folder to house the server project:

    
    mkdir bitcoin-aware-computing-server2 && cd bitcoin-aware-computing-server2
    

Then create a new file that we'll call `server2.py` and add the same
code you added earlier to the `server1.py` file for the
[Bitcoin-Accelerated Computing][22]. We
will only change the part that the server is hosting the endpoints on,
and the price the merchant will offer the endpoint for:

    
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
    @payment.required(1000)
    def fast_get_elem():
        arr = get_array_to_sort(request)
        prop = request.form.getlist("property")[0]
        value = int(request.form.getlist("value")[0])
        res = fast_get_element( arr, prop, value )
        return json.dumps({"elem": str(res)})
    
    # set up and run the server
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=9000)
    

Start your second micropayments server:

    
    python3 server2.py
    

## Step 3: Create an intelligent agent that searches for the lowest-priced API

Now that we have two endpoints for this paid API, we have a
market. And so we can write an **intelligent agent** that asks several
merchant servers in the market for the price of the endpoint they are
hosting, and then chooses the cheapest one.

To do this, SSH in as the `twenty-client` user and add the following code to
the `client.py` script that was created when running the [Bitcoin-Accelerated Computing][56] demo:

    
    # Compare prices for two merchant servers hosting the same endpoint,
    # and purchase the cheaper one
    response1 = requests.get_402_info(url='http://localhost:5000/fastfind')
    endpoint_info1 = dict(response1)
    
    response2 = requests.get_402_info(url='http://localhost:9000/fastfind')
    endpoint_info2 = dict(response2)
    
    print("Merchant 1 Price: " + str(endpoint_info1))
    print("Merchant 2 Price: " + str(endpoint_info2))
    

Example Output:

    
    Merchant 1 Price: {'price': '800', 'bitcoin-address': '14nfTDNfmQHTfxtYKwUAa5PbrB7hZqTvHu', 'username': 'testuser1'}
    Merchant 2 Price: {'price': '1000', 'bitcoin-address': '19ZSKGwL21nNo2kTger5ciM1xYrzNJcCRY', 'username': 'testuser2'}
    

It looks like Merchant 1 is currently offering this API call at a
better rate, so we can purchase it:

    
    price1 = endpoint_info1['price']
    price2 = endpoint_info2['price']
    
    body = {
         'array': json.dumps(data),
         'property': 'height',
         'value': 10
    }
    
    if int(price1) < int(price2):
       # purchase from merchant 1
       res = requests.post(url='http://localhost:5000/fastfind', data=body)
    else:
       # purchase from merchant 2
       res = requests.post(url='http://localhost:9000/fastfind', data=body)
    answer = json.loads(res.text)['elem']
    print(answer)
    

Example Output:

    
    {'height': 10}
    

That's it! You just built your first intelligent agent, a program
capable of getting price quotes in BTC from two servers and buying the
lowest priced item.

## Next Steps

Along with micropayments, the technology industry has wanted true
intelligent agents (IAs) since the beginning of the World Wide
Web. One of the things that has hampered the development of IAs is the
extraordinarily wide assortment of different kinds of credit card
forms and payment methods on different websites. Some sites accept
Paypal, others Stripe, and still others Alipay. And all sites have
different checkout flows and lists of accepted currencies.

Bitcoin promises to change that. Certainly not all at once, and not
for all legacy sites. But at least for HTTP-accessible digital goods
and services, it makes sense to make them
[bitcoin-payable][86] given how easy that now is
to do. And once they are bitcoin-payable, then they can be scraped and
purchased by an intelligent agent, as the code shows above.

As a next step, try passing in a function which takes a request
instance and returns a price into the `payment.required` decorator in
lieu of a fixed price. Specifically, try modifying the example such
that each server uses a pricing function where the price oscillates
sinusoidally. Now run your intelligent agent over and over again
and watch it pick the lower of the two prices each time.

Once you've done that, things start to get really interesting if you
have N clients and M servers for the same digital good, with finite or
rate-limited supply. Then you have a digital marketplace. 

If you build anything like this and want to earn some bitcoin for your
efforts, write it up and submit it as a
[bitcoin tutorial][87]. If we decide to publish
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
browse and purchase from other bitcoin-enabled servers? Head over to the [21 Developer Community][88] at slack.21.co to join the bitcoin machine-payable marketplace hosted on the 21 peer-to-peer
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

If you have any questions or issues, please drop us a line at [\[email protected\] ][90] or join our [Slack ][4] community.

This content is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License][91].


(c) 2016, 21.co

[Get The 21 Bitcoin Computer][3]


[0]: /
[1]: /setup/
[2]: /learn/
[3]: /buy/
[4]: https://slack.21.co
[5]: /bitnodes/
[6]: /about/
[7]: #intelligent-agents-with-bitcoin "Intelligent Agents with Bitcoin"
[8]: #overview "Overview"
[9]: #prerequisites "Prerequisites"
[10]: #step-1-set-up-a-bitcoin-accelerated-computing-endpoint "Step 1: Set up a bitcoin-accelerated computing endpoint"
[11]: #step-2-add-a-competitor-endpoint-provider-to-the-market "Step 2: Add a competitor endpoint-provider to the market"
[12]: #step-3-create-an-intelligent-agent-that-searches-for-the-lowest-priced-api "Step 3: Create an intelligent agent that searches for the lowest-priced API"
[13]: #next-steps "Next Steps"
[14]: /learn/ "< Back To Index"
[15]: https://twitter.com/intent/tweet?text=Hmm. This looks like a good resource for learning how to build Bitcoin apps:&url=https%3A//21.co/learn/intelligent-agents-with-bitcoin/
[16]: https://www.facebook.com/sharer/sharer.php?u=https%3A//21.co/learn/intelligent-agents-with-bitcoin/
[17]: /cdn-cgi/l/email-protection#90afb6e3e5f2faf5f3e4adc4f8f9e3b0fcfffffbe3b0fcf9fbf5b0f1b0f7fffff4b0e2f5e3ffe5e2f3f5b0f6ffe2b0fcf5f1e2fef9fef7b0f8ffe7b0e4ffb0f2e5f9Xld Bitcoin apps&body=Here's the URL: https%3A//21.co/learn/intelligent-agents-with-bitcoin/
[18]: /setup
[19]: ../introduction-to-the-21-bitcoin-computer/
[20]: ../21-multiple-users
[21]: ../bitcoin-accelerated-computing
[22]: ../bitcoin-accelerated-computing/#step-2-set-up-a-bitcoin-payable-api-server
[23]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-1
[24]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-2
[25]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-3
[26]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-4
[27]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-5
[28]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-6
[29]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-7
[30]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-8
[31]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-9
[32]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-10
[33]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-11
[34]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-12
[35]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-13
[36]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-14
[37]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-15
[38]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-16
[39]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-17
[40]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-18
[41]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-19
[42]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-20
[43]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-21
[44]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-22
[45]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-23
[46]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-24
[47]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-25
[48]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-26
[49]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-27
[50]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-28
[51]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-29
[52]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-30
[53]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-31
[54]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-32
[55]: #code-7bb8c7e5be55b78f4cfaec0be6abda1d11411e89-33
[56]: ../bitcoin-accelerated-computing/#step-3-use-the-clients-bitcoin-to-buy-api-calls-from-the-server
[57]: #code-401dcb5e6ebdce0b206bd65e740eeaa0e296f2d5-1
[58]: #code-401dcb5e6ebdce0b206bd65e740eeaa0e296f2d5-2
[59]: #code-401dcb5e6ebdce0b206bd65e740eeaa0e296f2d5-3
[60]: #code-401dcb5e6ebdce0b206bd65e740eeaa0e296f2d5-4
[61]: #code-401dcb5e6ebdce0b206bd65e740eeaa0e296f2d5-5
[62]: #code-401dcb5e6ebdce0b206bd65e740eeaa0e296f2d5-6
[63]: #code-401dcb5e6ebdce0b206bd65e740eeaa0e296f2d5-7
[64]: #code-401dcb5e6ebdce0b206bd65e740eeaa0e296f2d5-8
[65]: #code-401dcb5e6ebdce0b206bd65e740eeaa0e296f2d5-9
[66]: #code-401dcb5e6ebdce0b206bd65e740eeaa0e296f2d5-10
[67]: #code-ec3a32a61bd3d24694d42799b7eff6327e0fa9e7-1
[68]: #code-ec3a32a61bd3d24694d42799b7eff6327e0fa9e7-2
[69]: #code-1f7244b2f718be0dea8a211296758191e2f81a7e-1
[70]: #code-1f7244b2f718be0dea8a211296758191e2f81a7e-2
[71]: #code-1f7244b2f718be0dea8a211296758191e2f81a7e-3
[72]: #code-1f7244b2f718be0dea8a211296758191e2f81a7e-4
[73]: #code-1f7244b2f718be0dea8a211296758191e2f81a7e-5
[74]: #code-1f7244b2f718be0dea8a211296758191e2f81a7e-6
[75]: #code-1f7244b2f718be0dea8a211296758191e2f81a7e-7
[76]: #code-1f7244b2f718be0dea8a211296758191e2f81a7e-8
[77]: #code-1f7244b2f718be0dea8a211296758191e2f81a7e-9
[78]: #code-1f7244b2f718be0dea8a211296758191e2f81a7e-10
[79]: #code-1f7244b2f718be0dea8a211296758191e2f81a7e-11
[80]: #code-1f7244b2f718be0dea8a211296758191e2f81a7e-12
[81]: #code-1f7244b2f718be0dea8a211296758191e2f81a7e-13
[82]: #code-1f7244b2f718be0dea8a211296758191e2f81a7e-14
[83]: #code-1f7244b2f718be0dea8a211296758191e2f81a7e-15
[84]: #code-1f7244b2f718be0dea8a211296758191e2f81a7e-16
[85]: #code-1f7244b2f718be0dea8a211296758191e2f81a7e-17
[86]: ../bitcoin-payable-api
[87]: /submit-bitcoin-tutorial
[88]: https://slack.21.co/
[89]: /cdn-cgi/l/email-protection#7748510402151d1214034a231f1e04571b18181c04571b1e1c125716571018181357051204180205141257111805571b121605191e1910571f18005703185715021eXld Bitcoin apps&body=Here's the URL: https%3A//21.co/learn/intelligent-agents-with-bitcoin/
[90]: /cdn-cgi/l/email-protection#33404643435c41477301021d505c
[91]: https://creativecommons.org/licenses/by-sa/4.0/
[92]: //twitter.com/21
[93]: //medium.com/@21
