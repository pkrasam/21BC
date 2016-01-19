[![21.co](https://assets.21.co/shared/img/21logo.png)21 Inc][0]

# [Setup][1] | [Tutorials][2] | [Buy][3] | [Community][4] | [Nodes][5] | [About][6]


# Monetize the Command Line with Bitcoin 
*Content authored by John Granata, Ronak Mehta  |  Markdown created by PK Rasam* 
  

* [Monetize the Command Line with Bitcoin][7]
  * [Overview][8]
  * [Prerequisites][9]
  * [Step 1: Set up client and server accounts.][10]
  * [Step 2: Create a Google Developer account and obtain a key for the Google Maps-Geocode API][11]
  * [Step 3: Create a server that maps addresses to latitude/longitude][12]
  * [Step 4: Wrap the server into a bitcoin-payable command line tool][13]
  * [Next Steps][14]
* [< Back To Index][15]

# Monetize the Command Line with Bitcoin

## Overview

This tutorial illustrates how to build an entirely new class of
applications: command line tools that use a little bit of bitcoin to
pay a remote server for computation.

We illustrate the class of applications by showing you how to build a
simple, bitcoin-payable command line tool called `map21`. The tool
takes in an address string like "1600 Pennsylvania Avenue" as an
argument. Behind the scenes, it then pays a bit of mined bitcoin to a
geocode API server hosted on a 21 Bitcoin Computer to map this string
to a latitude and longitude.

Why is this interesting? It essentially lays the groundwork for a new
kind of Linux distribution, one that bundles dozens or hundreds of
these tools and that is thereby dependent on the presence of bitcoin
as the next fundamental _system resource_ alongside RAM and disk
space. It also means that the developers who build these new
bitcoin-payable command line apps could now actually monetize every
single invocation of their tools, should they become popular.

But let's jump into the example and then return to these points.

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

You will also need to install the Google Maps python library. Do this
with:

    
    sudo pip3 install googlemaps
    

## Step 2: Create a Google Developer account and obtain a key for the Google Maps-Geocode API

Go to the
[Google Developers Console][22] and
create an account. Click on `Dashboard` on the left-hand side of the
window and select `Enable and manage APIs`. From the `Google Maps
APIs` category select `Google Maps Geocoding API`. Select the `Enable
API` button on top and then click on the `Credentials` option on the
left-hand side. Click on `Add credentials` drop down button and
select `API key`. A pop-up window with different key options will show
up. Select `Server key`. In the new window enter the name of your
project that this key will be stored under and click on the `Create`
button. Take note of your API key once it is created.

NOTE: Google requires a user to enter billing information in order for
the API key to work. You will need to add your billing information in
order to use the API key you just created above. Google will not
charge your card if you set up the free account.

In the Google Developers Console window click on the `Products &
Services` menu option that is represented as 3 horizontal white
dashes. Select `Billing` from the options shown in the drop-down menu
and enter your billing information.

You are now ready to use your Google Geocode API key. Let's set up the
21 Bitcoin Computer as a bitcoin-payable micropayments server that our
CLI tool will call in order to access the Google Maps-Geocode REST
API.

## Step 3: Create a server that maps addresses to latitude/longitude

Log in as the `twenty-server` user and create a folder for your
project:

    
    mkdir ~/geocode-server && cd ~/geocode-server
    

Set an environment variable that defines your newly created Google
Maps-Geocode API key:

    
    export GOOGLE_MAPS_API_KEY=<enter your API key here>
    

Now create a file named `geocode-server.py` and add the following code:

    
    import os
    import json
    import googlemaps
    from flask import Flask, request
    
    #import from the 21 Developer Library
    from two1.lib.wallet import Wallet
    from two1.lib.bitserv.flask import Payment
    
    # set up server side wallet
    app = Flask(__name__)
    wallet = Wallet()
    payment = Payment(app, wallet)
    
    # create a developer account on Google and obtain a API key for the maps-geocode app
    gmaps = googlemaps.Client(key=os.environ.get('GOOGLE_MAPS_API_KEY'))
    
    # create a 402 end-point that accepts a user's input address and returns the lat/long
    @app.route('/geocode')
    @payment.required(1000)
    def geo():
        """Map input address given as a string to (latitude, longitude)."""
    
        # Define a dict variable to store latitude & longitude
        coords = {}
    
        # Get user's input address
        address = request.args.get('address')
    
        # Send a request to Google's Map-Geocode REST API using your API credentials defined above 
        geocode_result = gmaps.geocode(address)
    
        # Check to see if the result is valid
        if geocode_result.__len__() == 0:
            return "The input address is invalid."
        else:
            #Obtain Lat & Long from result
            coords['latitude'] = geocode_result[0]['geometry']['location']['lat']
            coords['longitude'] = geocode_result[0]['geometry']['location']['lng']
    
            # Return co-ordinates back to the user
            return json.dumps(coords)
    
    if __name__ == '__main__':
        app.run(host='0.0.0.0', debug=True)
    

Start the server with:

    
    python3 geocode-server.py
    

## Step 4: Wrap the server into a bitcoin-payable command line tool

Open a new terminal and SSH into your Bitcoin Computer as
`twenty-client`. This will be the user identity for the client who
will use the CLI tool to access the bitcoin-payable services that the
`twenty-server` user is hosting.

Create a folder to house the client project:

    
    mkdir ~/geocode-client && cd ~/geocode-client
    

Install the `Click` python package for creating command line interfaces:

    
    sudo pip3 install click
    

Now create a file named `map21.py` in this directory and open it in an
editor. Add the following code:

    
    import sys
    import json
    import click
    
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
    
    
    @click.command()
    @click.argument('address')
    def cli(address):
        """Call the geocode api hosted on the micropayments server"""
    
        sel_url = server_url+'geocode?address={}'
        response = requests.get(url=sel_url.format(address))
        if response.text == "The input address is invalid.":
            click.echo(response.text)
        else:
            coords = json.loads(response.text)
            click.echo(coords)
    

Save this file and close it. Create a file called `setup.py` and open it in your text editor. Add the following code:

    
    from setuptools import setup
    
    setup(
        name='map21',
        version='0.1',
        py_modules=['map21'],
            install_requires=[
                'Click',
        ],
        entry_points='''
            [console_scripts]
            map21=map21:cli
        ''',
    )
    

Save and close the file. Run the following command:

    
    sudo pip3 install --editable .
    

Now you can try out your bitcoin-payable CLI tool!

    
    map21 "<Address to search>"
    

## Next Steps

This is a simple application, but the concept is much bigger. We think
of this as a much more fine-grained way to do Software-as-a-Service
([SAAS][112]). The
success of SAAS web applications over the last decade for everything
from analytics to sales to data analysis to human resources has been
[indisputable][113],
but each new web service requires a credit card signup and isn't
necessarily interoperable.

We think the concept of command-line SAAS with bitcoin changes all
that.

As a developer, once you have a universal way to pay for each command
line invocation, you can (a) sign up for new SAAS services by invoking
a single command and (b) quickly string them together by piping the
JSON output of one SAAS service into another.

As an entrepreneur, the reason we think of this as "fine-grained" SAAS
is that you no longer need to set up a full web app to start getting
SAAS customers. You just need a
[bitcoin-payable API][114] that exposes a single
function and a corresponding command line client. Now anyone with
bitcoin can easily try your API out and integrate it into their
toolchain.

We think the long-term implications of this for independent software
development and the Unix ecosystem could be profound. Developers can
now release free command line tools that have a bitcoin-billable
server-side component. They can choose to set up whatever kind of
billing policy they want, whether simple pay-per-use or more complex
freemium models (eg making the tools free for the first few
invocations and then charging for subsequent uses).

Over time, this leads to a new kind of Bitcoin-focused Linux
distribution: one that has a group of tools with some server side
component that _require_ some bitcoin on the machine to operate. As a
first version of this, as you build new tools of this kind make sure
to post them in our [Slack community][4]. After review,
we'll be bundling user-submitted command line SAAS tools in the next
21 update, to make them accessible to all the 21 Bitcoin Developers.

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
browse and purchase from other bitcoin-enabled servers? Head over to the [21 Developer Community][115] at slack.21.co to join the bitcoin machine-payable marketplace hosted on the 21 peer-to-peer
network.

---

# Next :

## [Build More Bitcoin Apps][2]

[![Next](https://assets.21.co/setup/img/next_app.png)][2]

Check out all the Bitcoin Apps you can build with the 21 Bitcoin Computer.

[See more apps][2]

[![Next](https://assets.21.co/setup/img/next_app.png)][2]


---

*Content authored by John Granata, Ronak Mehta  |  Markdown created by PK Rasam* 

If you have any questions or issues, please drop us a line at [\[email protected\] ][117] or join our [Slack ][4] community.

This content is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License][118].


(c) 2016, 21.co

[Get The 21 Bitcoin Computer][3]


[0]: /
[1]: /setup/
[2]: /learn/
[3]: /buy/
[4]: https://slack.21.co
[5]: /bitnodes/
[6]: /about/
[7]: #monetize-the-command-line-with-bitcoin "Monetize the Command Line with Bitcoin"
[8]: #overview "Overview"
[9]: #prerequisites "Prerequisites"
[10]: #step-1-set-up-client-and-server-accounts "Step 1: Set up client and server accounts."
[11]: #step-2-create-a-google-developer-account-and-obtain-a-key-for-the-google-maps-geocode-api "Step 2: Create a Google Developer account and obtain a key for the Google Maps-Geocode API"
[12]: #step-3-create-a-server-that-maps-addresses-to-latitudelongitude "Step 3: Create a server that maps addresses to latitude/longitude"
[13]: #step-4-wrap-the-server-into-a-bitcoin-payable-command-line-tool "Step 4: Wrap the server into a bitcoin-payable command line tool"
[14]: #next-steps "Next Steps"
[15]: /learn/ "< Back To Index"
[16]: https://twitter.com/intent/tweet?text=Hmm. This looks like a good resource for learning how to build Bitcoin apps:&url=https%3A//21.co/learn/monetize-the-command-line-with-bitcoin/
[17]: https://www.facebook.com/sharer/sharer.php?u=https%3A//21.co/learn/monetize-the-command-line-with-bitcoin/
[18]: /cdn-cgi/l/email-protection#eed1c89d9b8c848b8d9ad3ba86879dce828181859dce8287858bce8fce8981818ace9c8b9d819b9c8d8bce88819cce828b8f9c80878089ce868199ce9a81ce8c9b87Xld Bitcoin apps&body=Here's the URL: https%3A//21.co/learn/monetize-the-command-line-with-bitcoin/
[19]: /setup
[20]: ../introduction-to-the-21-bitcoin-computer/
[21]: ../21-multiple-users
[22]: https://console.developers.google.com
[23]: #code-a2209058627bce4df394e132e0ac87a24d007c41-1
[24]: #code-a2209058627bce4df394e132e0ac87a24d007c41-2
[25]: #code-a2209058627bce4df394e132e0ac87a24d007c41-3
[26]: #code-a2209058627bce4df394e132e0ac87a24d007c41-4
[27]: #code-a2209058627bce4df394e132e0ac87a24d007c41-5
[28]: #code-a2209058627bce4df394e132e0ac87a24d007c41-6
[29]: #code-a2209058627bce4df394e132e0ac87a24d007c41-7
[30]: #code-a2209058627bce4df394e132e0ac87a24d007c41-8
[31]: #code-a2209058627bce4df394e132e0ac87a24d007c41-9
[32]: #code-a2209058627bce4df394e132e0ac87a24d007c41-10
[33]: #code-a2209058627bce4df394e132e0ac87a24d007c41-11
[34]: #code-a2209058627bce4df394e132e0ac87a24d007c41-12
[35]: #code-a2209058627bce4df394e132e0ac87a24d007c41-13
[36]: #code-a2209058627bce4df394e132e0ac87a24d007c41-14
[37]: #code-a2209058627bce4df394e132e0ac87a24d007c41-15
[38]: #code-a2209058627bce4df394e132e0ac87a24d007c41-16
[39]: #code-a2209058627bce4df394e132e0ac87a24d007c41-17
[40]: #code-a2209058627bce4df394e132e0ac87a24d007c41-18
[41]: #code-a2209058627bce4df394e132e0ac87a24d007c41-19
[42]: #code-a2209058627bce4df394e132e0ac87a24d007c41-20
[43]: #code-a2209058627bce4df394e132e0ac87a24d007c41-21
[44]: #code-a2209058627bce4df394e132e0ac87a24d007c41-22
[45]: #code-a2209058627bce4df394e132e0ac87a24d007c41-23
[46]: #code-a2209058627bce4df394e132e0ac87a24d007c41-24
[47]: #code-a2209058627bce4df394e132e0ac87a24d007c41-25
[48]: #code-a2209058627bce4df394e132e0ac87a24d007c41-26
[49]: #code-a2209058627bce4df394e132e0ac87a24d007c41-27
[50]: #code-a2209058627bce4df394e132e0ac87a24d007c41-28
[51]: #code-a2209058627bce4df394e132e0ac87a24d007c41-29
[52]: #code-a2209058627bce4df394e132e0ac87a24d007c41-30
[53]: #code-a2209058627bce4df394e132e0ac87a24d007c41-31
[54]: #code-a2209058627bce4df394e132e0ac87a24d007c41-32
[55]: #code-a2209058627bce4df394e132e0ac87a24d007c41-33
[56]: #code-a2209058627bce4df394e132e0ac87a24d007c41-34
[57]: #code-a2209058627bce4df394e132e0ac87a24d007c41-35
[58]: #code-a2209058627bce4df394e132e0ac87a24d007c41-36
[59]: #code-a2209058627bce4df394e132e0ac87a24d007c41-37
[60]: #code-a2209058627bce4df394e132e0ac87a24d007c41-38
[61]: #code-a2209058627bce4df394e132e0ac87a24d007c41-39
[62]: #code-a2209058627bce4df394e132e0ac87a24d007c41-40
[63]: #code-a2209058627bce4df394e132e0ac87a24d007c41-41
[64]: #code-a2209058627bce4df394e132e0ac87a24d007c41-42
[65]: #code-a2209058627bce4df394e132e0ac87a24d007c41-43
[66]: #code-a2209058627bce4df394e132e0ac87a24d007c41-44
[67]: #code-a2209058627bce4df394e132e0ac87a24d007c41-45
[68]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-1
[69]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-2
[70]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-3
[71]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-4
[72]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-5
[73]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-6
[74]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-7
[75]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-8
[76]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-9
[77]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-10
[78]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-11
[79]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-12
[80]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-13
[81]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-14
[82]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-15
[83]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-16
[84]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-17
[85]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-18
[86]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-19
[87]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-20
[88]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-21
[89]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-22
[90]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-23
[91]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-24
[92]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-25
[93]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-26
[94]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-27
[95]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-28
[96]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-29
[97]: #code-a3ce60fa988ee20d3b0e55ba8d45bcb66865e25d-30
[98]: #code-c0ef0064f2278d500a10a1b66b75d448f83a8332-1
[99]: #code-c0ef0064f2278d500a10a1b66b75d448f83a8332-2
[100]: #code-c0ef0064f2278d500a10a1b66b75d448f83a8332-3
[101]: #code-c0ef0064f2278d500a10a1b66b75d448f83a8332-4
[102]: #code-c0ef0064f2278d500a10a1b66b75d448f83a8332-5
[103]: #code-c0ef0064f2278d500a10a1b66b75d448f83a8332-6
[104]: #code-c0ef0064f2278d500a10a1b66b75d448f83a8332-7
[105]: #code-c0ef0064f2278d500a10a1b66b75d448f83a8332-8
[106]: #code-c0ef0064f2278d500a10a1b66b75d448f83a8332-9
[107]: #code-c0ef0064f2278d500a10a1b66b75d448f83a8332-10
[108]: #code-c0ef0064f2278d500a10a1b66b75d448f83a8332-11
[109]: #code-c0ef0064f2278d500a10a1b66b75d448f83a8332-12
[110]: #code-c0ef0064f2278d500a10a1b66b75d448f83a8332-13
[111]: #code-c0ef0064f2278d500a10a1b66b75d448f83a8332-14
[112]: https://en.wikipedia.org/wiki/Software_as_a_service
[113]: https://www.cbinsights.com/blog/saas-exits-workday-largest/
[114]: ../bitcoin-payable-api
[115]: https://slack.21.co/
[116]: /cdn-cgi/l/email-protection#724d54010710181711064f261a1b01521e1d1d1901521e1b1917521352151d1d16520017011d0700111752141d00521e1713001c1b1c15521a1d0552061d5210071bXld Bitcoin apps&body=Here's the URL: https%3A//21.co/learn/monetize-the-command-line-with-bitcoin/
[117]: /cdn-cgi/l/email-protection#c4b7b1b4b4abb6b084f6f5eaa7ab
[118]: https://creativecommons.org/licenses/by-sa/4.0/
[119]: //twitter.com/21
[120]: //medium.com/@21
