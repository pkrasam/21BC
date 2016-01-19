
# [Setup][1] | [Tutorials][2] | [Buy][3] | [Community][4] | [Nodes][5] | [About][6]


# A Crawler for the Machine-Payable Web 
*Content authored by John Granata  |  Markdown created by PK Rasam* 
  

* [A Crawler for the Machine-Payable Web][7]
  * [Overview][8]
  * [Prerequisites][9]
  * [Step 1: Create the 402 Crawler Script][10]
  * [Step 2: Create a Systemd Service][11]
  * [Step 3: Create a Systemd Timer][12]
  * [Step 4: Enable the Crawler Service][13]
  * [Next Steps][14]
* [< Back To Index][15]

# A Crawler for the Machine-Payable Web

## Overview

In this tutorial, we'll show you how to set up a crawler that checks
the status of bitcoin-payable endpoints as a scheduled job. We call
these
["402 endpoints"][19]
after the famous HTTP Error 402: Payment Required that was built into
web browsers from the beginning - and which we've now implemented on
the 21 Bitcoin Computer in the context of
[bitcoin-payable APIs][20].

This crawler is a useful tool for periodically checking the status of
your own hosted endpoints, or endpoints belonging to others that you
want to keep an eye on. It is also a prerequisite for a more
sophisticated version of the
[Intelligent Agents][21]
tutorial. Finally, as we will discuss at the end, it is a first step
towards how a big chunk of the future World Wide Web might be indexed.

Let's jump in!

## Prerequisites

You will need the following items:

* A 21 Bitcoin Computer, with built-in mining and software
* The latest version of the 21 software, obtained by running `21
update` as described in the [setup][22] process.
* Do the [Introduction to the 21 Bitcoin Computer][23]
tutorial
* Do the [Bitcoin-payable APIs][20] tutorial
* Do the [Intelligent Agents with Bitcoin][21] tutorial

If you've got all the prerequisites, you are ready to go. Let's get
started!

## Step 1: Create the 402 Crawler Script

Log into the Bitcoin Computer:

    ssh twenty@<BITCOIN_COMPUTER_IP_ADDRESS>
    

Create a folder to house the crawler project:

    mkdir ~/402-crawler && cd ~/402-crawler
    

Use a text editor to create a file called `crawl.py` in the
`402-crawler` directory, and fill it with the following code:

    
    """ 402 Crawler
    
        Crawl endpoints, check socket connection, and
        check 402 headers.
    
    """ 
    
    import os
    import json
    import datetime
    import logging
    import socket
    import requests
    
    from two1.commands.config import Config
    from two1.lib.wallet import Wallet
    from two1.lib.bitrequests import BitTransferRequests
    
    
    class Crawler402():
        """ Crawl endpoints to check status.
    
            Check server socket connection and query endpoints for
            price and recipient address.
    
        """
    
    
        def __init__(self, endpoint_list, log_file):
            """Set up logging & member vars"""
    
            # configure logging
            logging.basicConfig(level=logging.INFO,
                                filename=log_file,
                                filemode='a',
                                format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                                datefmt='%m-%d %H:%M')
    
            self.console = logging.StreamHandler()
            self.console.setLevel(logging.INFO)
            logging.getLogger('402-crawler').addHandler(self.console)
            self.logger = logging.getLogger('402-crawler')
            self.endpoint_list = endpoint_list
    
    
        def check_endpoints(self):
            """Crawl 402 endpoints"""
    
            # create 402 client
            self.bitrequests = BitTransferRequests(Wallet(), Config().username)
    
            # crawl endpoints, check headers
            self.logger.info("\nCrawling machine-payable endpoints...")
            for endpoint in self.endpoint_list:
    
                # extract domain name
                name = endpoint.split('/',1)[0].split('.',1)[1]
    
                # get server ip
                server_ip = socket.gethostbyname(name)
    
                # self.logger.info("Checking {0} on port {1}".format(server_ip, port))
                self.logger.info("Checking {}...".format(endpoint))
                # configure socket module
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_state = sock.connect_ex((server_ip, 80))
                sock.close()
    
                if server_state == 0:
                    try:
                        self.logger.info("Server state: {} is up!".format(endpoint))
                        response = self.bitrequests.get_402_info('https://'+endpoint)
                        self.logger.info("Price: {}".format(response['price']))
                        self.logger.info("Address: {}".format(response['bitcoin-address']))
                    except Exception as e:
                        self.logger.info("Could not read 402 payment headers.")
                else:
                    self.logger.info("Server state: {} is down!".format('https://'+endpoint))
                self.logger.info("Timestamp: {}\n".format(datetime.datetime.now()))
    
    
    if __name__=='__main__':
    
        # 402 endpoints to crawl
        endpoint_list = [
            'market.21.co/search/bing',
            'market.21.co/phone/send-sms',
        ]
    
        crawler = Crawler402( endpoint_list, '402-crawler.log')
        crawler.check_endpoints()
    

Save the file and close it. Now let's create a scheduled job that executes the crawler code at periodic intervals.

## Step 2: Create a Systemd Service

Change to your user's systemd config directory:

    
    mkdir -p ~/.config/systemd/user
    cd ~/.config/systemd/user
    

Create a file called `402-crawler.service` and open it in your text editor. Enter the following code:

    
    [Unit]
    Description=Crawl 402 endpoints
    
    [Service]
    Type=oneshot
    WorkingDirectory=/home/twenty/402-crawler
    ExecStart=/usr/bin/python3 /home/twenty/402-crawler/crawl.py
    

Save and close the file. Now let's create a systemd timer to periodically execute this service.

## Step 3: Create a Systemd Timer

Create a file called `402-crawler.timer` and open it in your text editor. Enter the following code:

    
    [Unit]
    Description=Periodically trigger the 402 crawler
    
    [Timer]
    OnBootSec=1min
    OnUnitActiveSec=20m
    
    [Install]
    WantedBy=timers.target
    

This timer will run the crawl.py script at 20 minute intervals. Save and close the file.

## Step 4: Enable the Crawler Service

All that's left is to enable the service. Execute the following commands in a terminal:

    
    systemctl --user enable 402-crawler.timer
    systemctl --user start 402-crawler.timer
    systemctl --user start 402-crawler.service
    systemctl --user daemon-reload
    

That's it! You now have a crawler service enabled that will check the status of endpoints at a desired time interval. You can disable the timer at any time with:

    
    systemctl --user stop 402-crawler.timer
    systemctl --user disable 402-crawler.timer
    systemctl --user stop 402-crawler.service
    

## Next Steps

Though they are sometimes used interchangeably in conversation, the
Internet is not the same as the World Wide Web (WWW). All kinds of protocols
run over the Internet - SMTP, FTP, SCP, and of course HTTP and
HTTPS. The World Wide Web roughly corresponds to the set of resources coded
in HTML and accessible via URLs over HTTP and HTTPS (and newer
protocols like SPDY).

The implementation of HTTP Error Code 402 means that we can now bill
for HTTP-accessible resources in bitcoin. Analogs of 402 will need to
be developed for other protocols that don't precisely fit the
request/response paradigm of HTTP.

But even just in the context of the WWW, a working implementation of
402-aware servers and clients means that we have the basic tools to
build a third wing of the Web. First there was just the World Wide
Web, indexed by Google. Then there was the Social Web, indexed and
hosted by Facebook, Twitter, and company. And now there will be the
Machine-Payable Web. 

While the Social Web is gated behind logins and therefore
[opaque][140]
to Google, the early Machine-Payable Web poses a different
challenge. A crawler like the one in this example can list the prices,
but to actually access the URLs will require a small amount of bitcoin
per request.

This has the long-term potential to change the balance of power
between search engines (especially Google) and content
providers. Right now, Google's search engine crawls news websites like
the Wall Street Journal and indexes them, which displeases many
newspaper editors. The Wall Street Journal has
[wanted][141]
Google to compensate their organization for each page request for many
years. Google currently counters by noting that should they desire to
be dropped from Google's index, the Wall Street Journal or any other
news organization need only modify their
[robots.txt][142]
file to block the Google crawler. Needless to say, few news
organizations want to lose the traffic that Google drives their way,
and so few have taken that option of self-delisting.

However, the introduction of 402-payable URLs and 402-aware web
crawlers may change the balance of power. In the not-too-distant
future, content providers - starting with individual blogs and then
scaling up to larger websites - can set up 402 paywalls to charge a
tiny amount of bitcoin to each individual visitor. This would be a
negligible toll for the casual consumer of news content. However,
industrial scale scraping of the internet on the scale of the
GoogleBot could become very expensive indeed, as it would require that
Google procure Bitcoin as a kind of digital commodity to power its
search engine, much like Apple must scour the planet for
[rare earth elements][143]
to build its iPhones.

If you're interested in this kind of thing, here are a few possible
next steps:

* Modify an open source blogging platform like Wordpress to create a
bitcoin-payable blog, and host it on a 21 Bitcoin Computer.
* Take the example of selling files for bitcoin and modify it to
sell PDFs for bitcoin, thereby allowing the monetization of
news archives
* Set up N machine payable endpoints with time-varying prices and
turn the output of this crawler into the input for a
bitcoin-payable intelligent agent to make decisions about.

As always, if you build anything like this please come to the 21
Developer Community at [slack.21.co][4] to buy and
sell from other developers!

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
browse and purchase from other bitcoin-enabled servers? Head over to the [21 Developer Community][144] at slack.21.co to join the bitcoin machine-payable marketplace hosted on the 21 peer-to-peer
network.

---

# Next :

## [Build More Bitcoin Apps][2]

[![Next](https://assets.21.co/setup/img/next_app.png)][2]

Check out all the Bitcoin Apps you can build with the 21 Bitcoin Computer.


---

*Content authored by John Granata  |  Markdown created by PK Rasam* 

If you have any questions or issues, please drop us a line at [Email ][146] or join our [Slack ][4] community.

This content is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License][147].


(c) 2016, 21.co

[Get The 21 Bitcoin Computer][3]


[0]: /
[1]: /setup/
[2]: /learn/
[3]: /buy/
[4]: https://slack.21.co
[5]: /bitnodes/
[6]: /about/
[7]: #a-crawler-for-the-machine-payable-web "A Crawler for the Machine-Payable Web"
[8]: #overview "Overview"
[9]: #prerequisites "Prerequisites"
[10]: #step-1-create-the-402-crawler-script "Step 1: Create the 402 Crawler Script"
[11]: #step-2-create-a-systemd-service "Step 2: Create a Systemd Service"
[12]: #step-3-create-a-systemd-timer "Step 3: Create a Systemd Timer"
[13]: #step-4-enable-the-crawler-service "Step 4: Enable the Crawler Service"
[14]: #next-steps "Next Steps"
[15]: /learn/ "< Back To Index"
[17]: https://www.facebook.com/sharer/sharer.php?u=https%3A//21.co/learn/crawl-the-machine-payable-web/
[19]: https://21.co/learn/21-micropayments/#http-402-payment-required
[20]: ../bitcoin-payable-api
[21]: ../intelligent-agents-with-bitcoin
[22]: /setup
[23]: ../introduction-to-the-21-bitcoin-computer/
[24]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-1
[25]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-2
[26]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-3
[27]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-4
[28]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-5
[29]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-6
[30]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-7
[31]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-8
[32]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-9
[33]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-10
[34]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-11
[35]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-12
[36]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-13
[37]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-14
[38]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-15
[39]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-16
[40]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-17
[41]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-18
[42]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-19
[43]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-20
[44]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-21
[45]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-22
[46]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-23
[47]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-24
[48]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-25
[49]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-26
[50]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-27
[51]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-28
[52]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-29
[53]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-30
[54]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-31
[55]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-32
[56]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-33
[57]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-34
[58]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-35
[59]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-36
[60]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-37
[61]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-38
[62]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-39
[63]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-40
[64]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-41
[65]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-42
[66]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-43
[67]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-44
[68]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-45
[69]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-46
[70]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-47
[71]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-48
[72]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-49
[73]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-50
[74]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-51
[75]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-52
[76]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-53
[77]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-54
[78]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-55
[79]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-56
[80]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-57
[81]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-58
[82]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-59
[83]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-60
[84]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-61
[85]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-62
[86]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-63
[87]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-64
[88]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-65
[89]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-66
[90]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-67
[91]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-68
[92]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-69
[93]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-70
[94]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-71
[95]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-72
[96]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-73
[97]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-74
[98]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-75
[99]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-76
[100]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-77
[101]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-78
[102]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-79
[103]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-80
[104]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-81
[105]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-82
[106]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-83
[107]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-84
[108]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-85
[109]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-86
[110]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-87
[111]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-88
[112]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-89
[113]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-90
[114]: #code-7beee6b0a3fda3b40e17fab238b8e52bd45c9620-91
[115]: #code-6ed75affcd1d962846a0bf15ac7ea3dc058f91c5-1
[116]: #code-6ed75affcd1d962846a0bf15ac7ea3dc058f91c5-2
[117]: #code-7e8d35ec99073c171f6e8f6231ee2a02c1f3dd28-1
[118]: #code-7e8d35ec99073c171f6e8f6231ee2a02c1f3dd28-2
[119]: #code-7e8d35ec99073c171f6e8f6231ee2a02c1f3dd28-3
[120]: #code-7e8d35ec99073c171f6e8f6231ee2a02c1f3dd28-4
[121]: #code-7e8d35ec99073c171f6e8f6231ee2a02c1f3dd28-5
[122]: #code-7e8d35ec99073c171f6e8f6231ee2a02c1f3dd28-6
[123]: #code-7e8d35ec99073c171f6e8f6231ee2a02c1f3dd28-7
[124]: #code-5b7b05739f306742e7f500c1b06ff6f816fe2566-1
[125]: #code-5b7b05739f306742e7f500c1b06ff6f816fe2566-2
[126]: #code-5b7b05739f306742e7f500c1b06ff6f816fe2566-3
[127]: #code-5b7b05739f306742e7f500c1b06ff6f816fe2566-4
[128]: #code-5b7b05739f306742e7f500c1b06ff6f816fe2566-5
[129]: #code-5b7b05739f306742e7f500c1b06ff6f816fe2566-6
[130]: #code-5b7b05739f306742e7f500c1b06ff6f816fe2566-7
[131]: #code-5b7b05739f306742e7f500c1b06ff6f816fe2566-8
[132]: #code-5b7b05739f306742e7f500c1b06ff6f816fe2566-9
[133]: #code-c2199c6a022169c5b0a2b04ac86896af2c5d7a38-1
[134]: #code-c2199c6a022169c5b0a2b04ac86896af2c5d7a38-2
[135]: #code-c2199c6a022169c5b0a2b04ac86896af2c5d7a38-3
[136]: #code-c2199c6a022169c5b0a2b04ac86896af2c5d7a38-4
[137]: #code-19db70d840414fab66be536c180a84113b720ae8-1
[138]: #code-19db70d840414fab66be536c180a84113b720ae8-2
[139]: #code-19db70d840414fab66be536c180a84113b720ae8-3
[140]: http://searchenginewatch.com/sew/news/2325343/matt-cutts-facebook-twitter-social-signals-not-part-of-google-search-ranking-algorithms
[141]: http://www.cnet.com/news/wall-street-journal-ap-take-aim-at-google/
[142]: http://searchengineland.com/google-to-newspapers-robotstxt-you-22477
[143]: http://www.bloomberg.com/news/articles/2015-06-02/chileans-betting-apple-to-go-green-in-china-led-rare-earths-rout
[144]: https://slack.21.co/
[146]: mailto:support@21.co
[147]: https://creativecommons.org/licenses/by-sa/4.0/
[148]: //twitter.com/21
[149]: //medium.com/@21
