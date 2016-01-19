[![21.co](https://assets.21.co/shared/img/21logo.png)21 Inc][0]

* [Setup][1]
* [Tutorials][2]
* [Buy][3]
* [Community][4]
* [Nodes][5]
* [About][6]

* [Build a Bitcoin-payable HTTP Proxy][7]
  * [Overview][8]
  * [Prerequisites][9]
  * [Step 1: Set up client and server accounts.][10]
  * [Step 2: Set up the example server for debugging][11]
  * [Step 3: Set up the HTTP Proxy][12]
  * [Step 4: Create a client that pays bitcoin to a proxy to connect to a remote server][13]
  * [Next Steps][14]
* [< Back To Index][15]

# Bitcoin-payable HTTP ProxyPosted by
Corentin Debains
  
* [Build a Bitcoin-payable HTTP Proxy][7]
  * [Overview][8]
  * [Prerequisites][9]
  * [Step 1: Set up client and server accounts.][10]
  * [Step 2: Set up the example server for debugging][11]
  * [Step 3: Set up the HTTP Proxy][12]
  * [Step 4: Create a client that pays bitcoin to a proxy to connect to a remote server][13]
  * [Next Steps][14]
* [< Back To Index][15]

# Build a Bitcoin-payable HTTP Proxy

## Overview

Suppose you are in an area (or a country) behind a firewall, and you
want to access a web page outside that firewall. In theory, a
[proxy][19] would be a simple
solution: just route your requests through the proxy server to make
the website think a user is located wherever the proxy is
located. However, in practice, finding a good proxy with useful
options and good performance can be tricky and often requires a
monthly subscription for access. This requires creating an account
and adding funds to it, usually with a credit card - and this
significantly raises the fixed costs of using a proxy.

One solution is to set up a 21 Bitcoin Computer as a bitcoin-payable
HTTP proxy, with (say) 1 cent in bitcoin charged per request. This
would both compensate the proxy provider and reduce the up-front cost
for the proxy user, as no account setup would be needed. The provider
doesn't manage accounts and the user doesn't have a password to
remember. Moreover, as a portable device with a virtualizable IP,
requests from a 21 Bitcoin Computer are less likely to be blocked -
which is potentially quite useful for a low-volume (<10000 requests
per day) proxy server used by a few of your friends abroad. Let's see
how to set one up.

## Prerequisites

You will need the following first:

* A 21 Bitcoin Computer, with built-in mining and software
* The latest version of the 21 software, obtained by running `21
update` as described in the [setup][20] process.
* Do the [Introduction to the 21 Bitcoin Computer][21]
tutorial
* Do the [Working with Multiple 21 Users][22] tutorial

If you've got all the prerequisites, you are ready to go. Let's get
started!

## Step 1: Set up client and server accounts.

Follow the instructions in the
[Working With Multiple 21 Users][22] tutorial to set
up the `twenty-client`, `twenty-server`, and `twenty-server-2` users
and install Flask.

There are three pieces in this system: an example server for
debugging, a bitcoin-payable proxy, and a client capable of paying
bitcoin. You will also need to install the `requests` library:

    sudo pip3 install requests
    

In what follows, the `twenty-client` will be the user that requests a
page. The `twenty-server` will be the user identity for the example
server we're setting up to test the proxy and the actual proxy itself.

## Step 2: Set up the example server for debugging

First, we will set up a simple example server running on the 21
Bitcoin Computer itself. This will be used to test out the proxy
that you are about to write.

To set up the example server, SSH in as the `twenty-server` user.

    ssh twenty-server@<IP Address>
    

Create a file called `example-server-for-http-proxy.py` in a new
directory.

    nano example-server-for-http-proxy.py
    

Fill it with the following code:

    
    from flask import Flask, request
    
    app = Flask(__name__)
    
    @app.route("/")
    def hello():
        return "Hello, World!\n"
    
    @app.route("/AmIBehindProxy")
    def areyouaproxy():
        if "X-Forwarded-For" in request.headers:
            return "Yes, You are behind a proxy\n"
        else:
            return "I didn't see any evidence of a proxy\n"
    
    if __name__ == "__main__":
        app.run()
    

This `example-server-for-http-proxy.py` has two endpoints (`/` and
`/AmIBehindProxy`). These endpoints will be used to debug your proxy
locally and confirm that it's working as advertised before trying to
connect to a real remote server like `stanford.edu`. Let's start the
server to test it out:

    python3 example-server-for-http-proxy.py
    

Leave the current terminal open and open up another one. SSH into
your 21 Bitcoin computer as the `twenty-client` user with:

    ssh twenty-client@<IP Address>
    

Use the command line `curl` utility to request the URL
`http://127.0.0.1:5000/` from this example server as follows:

    curl http://127.0.0.1:5000/
    

It should display `Hello, World!`. Now, try curling the other endpoint
of this example server:

    curl http://127.0.0.1:5000/AmIBehindProxy
    

It should display `I didn't see any evidence of a proxy`. All the
example server is doing is looking for the standard
[`X-Forwarded-For`][40]
header in the HTTP request to see if it was indeed a proxy that routed
your request. We will use this to debug the proxy server below.

## Step 3: Set up the HTTP Proxy

Leave the current terminal open and open up another one. SSH into
your 21 Bitcoin computer as the `twenty-server` user with:

    ssh twenty-server@<IP Address>
    

Create a file called `proxy.py` in a new directory.

    nano proxy.py
    

Fill it with the following code:

    
    import requests
    
    from flask import Flask, request, Response
    from werkzeug.datastructures import Headers
    
    # import from the 21 Developer Library
    from two1.lib.wallet import Wallet
    from two1.lib.bitserv.flask import Payment
    
    app = Flask(__name__)
    
    wallet = Wallet()
    payment = Payment(app, wallet)
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    @payment.required(1000)
    def catch_all(path):
        try:
            h = Headers(request.headers)
            h.add('X-Forwarded-For', request.remote_addr)
            h.remove('HTTP_BITCOIN_MICROPAYMENT_SERVER')
            h.remove('HTTP_RETURN_WALLET_ADDRESS')
    
            r = requests.request(
                method=request.method,
                url=request.url,
                headers=h,
                files=request.files if request.files else None,
                data=request.data if request.data else None,
                params=request.args if request.args else None,
                timeout=5
            )
        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ReadTimeout):
            return Response(status=504)
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError,
            requests.exceptions.TooManyRedirects):
            return Response(status=502)
        except (
            requests.exceptions.RequestException,
            Exception) as e:
            if app.debug:
                raise e
            return Response(status=500)
    
        headers = list(r.headers.items())
        return Response(
            r.text if r.text else None,
            status=r.status_code,
            headers=headers
        )
    
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=9000)
    

Let's start the proxy:

    python3 proxy.py
    

The proxy is now running on port 9000 of our bitcoin computer, and our
destination server from the earlier step is running on port 5000\.

Note: our proxy looks a lot like our original server, and that's
normal! They are both web (HTTP) servers based on the Flask web
microframework. But the proxy is a little more elaborate.

First, the proxy uses bitcoin. The `Payment` class is a blueprint
designed to makes it very simple to use micropayments with our server
endpoints. It is applied here as a decorator:
`@payment.required(1000)`, which means that every call to this
endpoint will require a payment of 1000 satoshis. The Bitcoin
Computer's wallet is used as the payout address for all the money
collected by the proxy.

Second, the `@app.route` part is slightly different than the
corresponding
[Python decorator][100]
on the example server. It catches requests made to the destination
server and routes them to the destination server if a micropayment has
been embedded in the request. The `catch_all` function performs the
following operations:

1. Insert the `X-Forwarded-For` header, which is a conventional proxy header.
2. Remove the bitcoin micropayment headers to receive the payment.
3. Call the destination website with the same parameters that the user
gave, with some error handling to return common Proxy Error codes.
4. Send the `Response` back with the destination server's reply.

Now we're going to put the pieces together.

## Step 4: Create a client that pays bitcoin to a proxy to connect to a remote server

To set up the client, SSH in as the `twenty-client` user:

    ssh twenty-client@<IP Address>
    

Create a file called `client-for-http-proxy.py` in a new directory.

    nano client-for-http-proxy.py
    

Fill it with the following code:

    
    #!/usr/bin/env python3
    from two1.commands.config import Config
    from two1.lib.wallet import Wallet
    from two1.lib.bitrequests import BitTransferRequests
    
    EXAMPLE_SERVER = "http://127.0.0.1:5000"
    PROXY = "http://127.0.0.1:9000"
    
    proxies = {"http": PROXY}
    
    wallet = Wallet()
    username = Config().username
    requests = BitTransferRequests(wallet, username)
    
    print("Call the example server directly")
    print("The goal here is to confirm that the example server is \
    reachable and can distinguish between a proxied and non-proxied \
    connection.")
    r = requests.get(url=EXAMPLE_SERVER + "/AmIBehindProxy")
    print(r.text)
    
    print("Call the example debug server through the proxy, paying 1000 satoshis per request")
    print("The goal here is to confirm that the example server was hit through a proxy.")
    r = requests.get(url=EXAMPLE_SERVER + "/AmIBehindProxy", proxies=proxies)
    print(r.text)
    
    print("Now call a real server at stanford.edu by paying the proxy some bitcoin")
    r = requests.get(url="https://www.stanford.edu", proxies=proxies)
    print(r.text)
    

Finally, let's run the client:

    python3 client-for-http-proxy.py
    

To recap, what we did here was:

* set up an example server locally
* set up a proxy
* used the example server to test out whether the proxy worked properly
* then made a request to a real remote server (stanford.edu) through the proxy

The bitcoin portion of this is based on the 21 Bitcoin Library's
[`BitTransferRequests`][130] class, essentially a
bitcoin-powered wrapper around the standard Python3 requests
library. Thus, when the proxy returns a `402 Payment Required` error,
the library automatically handles the micropayment and passes through
the full HTTP response object unscathed. In the sample code above we
only used `r.text`, but you could try `r.headers` and
`r.status_code`. They would be the same between the proxied and direct
connection.

After you've done this, you should see the `twenty-client` balance
decrease and the `twenty-server` balance increase. You can confirm
this by running `21 log` as the `twenty-client` and the
`twenty-server` user to see each proxy purchase. And as the
`twenty-server` user, you can flush your earnings to the blockchain by
doing `21 flush`.

## Next Steps

This proxy is fairly limited in what in can do and highly insecure!
However, it's a great experiment to explore the power of bitcoin
micropayments with existing tools and protocols. Here are some ideas
on what to build next:

* Make this example high performance by replacing the simple Flask
proxy server with a proper deployment on the underlying hardware. See
[this][131]
and [this][132]
for some first steps.
* 
Many websites that are behind services like
[Cloudflare][133] will reject requests from
proxies. For educational purposes, see if you can increase the
number of websites you can connect to via the proxy by removing the
"X-Forwarded-For" headers, changing the "User-Agent" strings, and
doing similar things to the outbound request.
* 
Modify this code to create a paying proxy which would pay for
bitcoin-payable resources on your behalf when you request them.
* 
Modify this code to create a reverse proxy, which you can put in
front of any existing HTTP-accessible resource to create a bitcoin
paywall.
* 
Integrate this example with a Chrome-based bitcoin wallet to create
a simple example of what a machine-payable internet might look like.
* 
Modify this example to route requests through a production proxy
service like [Hola][134].

If you build anything like this and want to earn some bitcoin for your
efforts, write it up and submit it as a
[bitcoin tutorial][135]. If we decide to publish
it on our site, you'll win $200 in BTC! You can also come to our Slack
channel at slack.21.co to find other folks with 21 Bitcoin Computers
to give feedback. We look forward to seeing you there!

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
browse and purchase from other bitcoin-enabled servers? Head over to the [21 Developer Community][136] at slack.21.co to join the bitcoin machine-payable marketplace hosted on the 21 peer-to-peer
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
Corentin Debains

If you have any questions or issues, please drop us a line at [\[email protected\] ][138] or join our [Slack ][4] community.

This content is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License][139].

(c) 2016, 21.co

[Get The 21 Bitcoin Computer][3]


[0]: /
[1]: /setup/
[2]: /learn/
[3]: /buy/
[4]: https://slack.21.co
[5]: /bitnodes/
[6]: /about/
[7]: #build-a-bitcoin-payable-http-proxy "Build a Bitcoin-payable HTTP Proxy"
[8]: #overview "Overview"
[9]: #prerequisites "Prerequisites"
[10]: #step-1-set-up-client-and-server-accounts "Step 1: Set up client and server accounts."
[11]: #step-2-set-up-the-example-server-for-debugging "Step 2: Set up the example server for debugging"
[12]: #step-3-set-up-the-http-proxy "Step 3: Set up the HTTP Proxy"
[13]: #step-4-create-a-client-that-pays-bitcoin-to-a-proxy-to-connect-to-a-remote-server "Step 4: Create a client that pays bitcoin to a proxy to connect to a remote server"
[14]: #next-steps "Next Steps"
[15]: /learn/ "< Back To Index"
[16]: https://twitter.com/intent/tweet?text=Hmm. This looks like a good resource for learning how to build Bitcoin apps:&url=https%3A//21.co/learn/bitcoin-payable-http-proxy/
[17]: https://www.facebook.com/sharer/sharer.php?u=https%3A//21.co/learn/bitcoin-payable-http-proxy/
[18]: /cdn-cgi/l/email-protection#9da2bbeee8fff7f8fee9a0c9f5f4eebdf1f2f2f6eebdf1f4f6f8bdfcbdfaf2f2f9bdeff8eef2e8effef8bdfbf2efbdf1f8fceff3f4f3fabdf5f2eabde9f2bdffe8f4Xld Bitcoin apps&body=Here's the URL: https%3A//21.co/learn/bitcoin-payable-http-proxy/
[19]: https://en.wikipedia.org/wiki/Proxy_server
[20]: /setup
[21]: ../introduction-to-the-21-bitcoin-computer/
[22]: ../21-multiple-users
[23]: #code-0dc3ffbdcc33f54f4fbe3250bea537537c714321-1
[24]: #code-0dc3ffbdcc33f54f4fbe3250bea537537c714321-2
[25]: #code-0dc3ffbdcc33f54f4fbe3250bea537537c714321-3
[26]: #code-0dc3ffbdcc33f54f4fbe3250bea537537c714321-4
[27]: #code-0dc3ffbdcc33f54f4fbe3250bea537537c714321-5
[28]: #code-0dc3ffbdcc33f54f4fbe3250bea537537c714321-6
[29]: #code-0dc3ffbdcc33f54f4fbe3250bea537537c714321-7
[30]: #code-0dc3ffbdcc33f54f4fbe3250bea537537c714321-8
[31]: #code-0dc3ffbdcc33f54f4fbe3250bea537537c714321-9
[32]: #code-0dc3ffbdcc33f54f4fbe3250bea537537c714321-10
[33]: #code-0dc3ffbdcc33f54f4fbe3250bea537537c714321-11
[34]: #code-0dc3ffbdcc33f54f4fbe3250bea537537c714321-12
[35]: #code-0dc3ffbdcc33f54f4fbe3250bea537537c714321-13
[36]: #code-0dc3ffbdcc33f54f4fbe3250bea537537c714321-14
[37]: #code-0dc3ffbdcc33f54f4fbe3250bea537537c714321-15
[38]: #code-0dc3ffbdcc33f54f4fbe3250bea537537c714321-16
[39]: #code-0dc3ffbdcc33f54f4fbe3250bea537537c714321-17
[40]: https://en.wikipedia.org/wiki/X-Forwarded-For
[41]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-1
[42]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-2
[43]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-3
[44]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-4
[45]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-5
[46]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-6
[47]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-7
[48]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-8
[49]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-9
[50]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-10
[51]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-11
[52]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-12
[53]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-13
[54]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-14
[55]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-15
[56]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-16
[57]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-17
[58]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-18
[59]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-19
[60]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-20
[61]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-21
[62]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-22
[63]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-23
[64]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-24
[65]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-25
[66]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-26
[67]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-27
[68]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-28
[69]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-29
[70]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-30
[71]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-31
[72]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-32
[73]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-33
[74]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-34
[75]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-35
[76]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-36
[77]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-37
[78]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-38
[79]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-39
[80]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-40
[81]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-41
[82]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-42
[83]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-43
[84]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-44
[85]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-45
[86]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-46
[87]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-47
[88]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-48
[89]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-49
[90]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-50
[91]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-51
[92]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-52
[93]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-53
[94]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-54
[95]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-55
[96]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-56
[97]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-57
[98]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-58
[99]: #code-4656b9f8bc57f215ab2c28a1a9af7acec7d5a6dd-59
[100]: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
[101]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-1
[102]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-2
[103]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-3
[104]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-4
[105]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-5
[106]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-6
[107]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-7
[108]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-8
[109]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-9
[110]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-10
[111]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-11
[112]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-12
[113]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-13
[114]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-14
[115]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-15
[116]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-16
[117]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-17
[118]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-18
[119]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-19
[120]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-20
[121]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-21
[122]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-22
[123]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-23
[124]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-24
[125]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-25
[126]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-26
[127]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-27
[128]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-28
[129]: #code-a4fd6db33e16035404c4733ef277bc76830f3530-29
[130]: ../21-micropayments
[131]: http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvii-deployment-on-linux-even-on-the-raspberry-pi
[132]: http://tutos.readthedocs.org/en/latest/source/ndg.html
[133]: http://cloudflare.com
[134]: http://hola.org
[135]: /submit-bitcoin-tutorial
[136]: https://slack.21.co/
[137]: /cdn-cgi/l/email-protection#112e376264737b7472652c45797862317d7e7e7a62317d787a74317031767e7e75316374627e6463727431777e63317d7470637f787f7631797e6631657e31736478Xld Bitcoin apps&body=Here's the URL: https%3A//21.co/learn/bitcoin-payable-http-proxy/
[138]: /cdn-cgi/l/email-protection#33404643435c41477301021d505c
[139]: https://creativecommons.org/licenses/by-sa/4.0/
[140]: //twitter.com/21
[141]: //medium.com/@21
