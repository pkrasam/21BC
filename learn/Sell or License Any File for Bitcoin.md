[![21.co](https://assets.21.co/shared/img/21logo.png)21 Inc][0]

* [Setup][1]
* [Tutorials][2]
* [Buy][3]
* [Community][4]
* [Nodes][5]
* [About][6]

* [Sell or License Any File for Bitcoin][7]
  * [Overview][8]
  * [Prerequisites][9]
  * [Step 1: Set up client and server accounts.][10]
  * [Step 2: Create a server to sell digital goods for bitcoin][11]
  * [Step 3: Create a client to buy digital goods for bitcoin][12]
  * [Next Steps][13]
* [< Back To Index][14]

# Sell or License Any File for BitcoinPosted by
Ronak Mehta
  

* [Sell or License Any File for Bitcoin][7]
  * [Overview][8]
  * [Prerequisites][9]
  * [Step 1: Set up client and server accounts.][10]
  * [Step 2: Create a server to sell digital goods for bitcoin][11]
  * [Step 3: Create a client to buy digital goods for bitcoin][12]
  * [Next Steps][13]
* [< Back To Index][14]

# Sell or License Any File for Bitcoin

## Overview

In this tutorial we'll discuss the script that you went through in the
[Introduction to the 21 Bitcoin Computer][18]
tutorial in more detail, to show how to set up a simple static
file server that hosts files you can sell for bitcoin. By extending
this example you can run your very own iTunes-like digital media store.

## Prerequisites

You will need the following items:

* A 21 Bitcoin Computer, with built-in mining and software
* The latest version of the 21 software, obtained by running `21
update` as described in the [setup][19] process.
* Do the [Introduction to the 21 Bitcoin Computer][18]
tutorial
* Do the [Working with Multiple 21 Users][20] tutorial

If you've got all the prerequisites, you are ready to go. Let's get
started!

## Step 1: Set up client and server accounts.

Follow the instructions in the
[Working With Multiple 21 Users][20] tutorial to set
up the `twenty-client`, `twenty-server`, and `twenty-server-2` users
and install Flask.

## Step 2: Create a server to sell digital goods for bitcoin

Log in as the `twenty-server` user and create a folder for your
project:

    
    mkdir fileserver && cd fileserver
    

Now start editing a file named `server.py` in this directory with the
following code:

    
    #!/usr/bin/env python3
    import os
    import json
    import random
    
    from flask import Flask
    from flask import request
    from flask import send_from_directory
    
    # import from the 21 Developer Library
    from two1.lib.wallet import Wallet
    from two1.lib.bitserv.flask import Payment
    
    app = Flask(__name__)
    wallet = Wallet()
    payment = Payment(app, wallet)
    
    # directory of the digital content we'd like to sell
    dir_path = '/home/twenty-server/sellfiles'
    
    # get a list of the files in the directory
    file_list = os.listdir(dir_path)
    
    # simple content model: dictionary of files w/ prices
    files = {}
    for file_id in range(len(file_list)):
        files[file_id+1] = file_list[file_id], random.randrange(1000,3000)
    
    # endpoint to look up files to buy
    @app.route('/files')
    def file_lookup():
        return json.dumps(files)
    
    # return the price of the selected file
    def get_price_from_request(request):
        id = int(request.args.get('selection'))
        return files[id][1]
    
    # machine-payable endpoint that returns selected file if payment made
    @app.route('/buy')
    @payment.required(get_price_from_request)
    def buy_file():
    
        # extract selection from client request
        sel = int(request.args.get('selection'))
    
        # check if selection is valid
        if(sel < 1 or sel > len(file_list)):
            return 'Invalid selection.'
        else:
            return send_from_directory(dir_path,file_list[int(sel)-1])
    
    if __name__ == '__main__':
        app.run(host='0.0.0.0')
    

Before you start the server, we will need to create the `dir_path` and
load it up with some files to sell. Execute the following at the
command line:

    
    cd $HOME
    mkdir sellfiles
    cd sellfiles
    wget https://bitcoin.org/bitcoin.pdf
    wget https://en.bitcoin.it/w/images/en/2/29/BC_Logo_.png
    cd $HOME
    

If you are connected to the 21 Bitcoin Computer from a Linux or Mac
machine, you can also transfer more content from your laptop to your
Bitcoin Computer with the `scp` command. For example:

    
    scp file.txt [[email protected]][81]:~/sellfiles/
    

The above command copies `file.txt` from your PC or Mac to the
location `/home/twenty-server/sellfiles/` on the Bitcoin
Computer. Once you have some content in there, go ahead and start the
server with:

    
    python3 fileserver/server.py
    

## Step 3: Create a client to buy digital goods for bitcoin

Open a new terminal and SSH into your Bitcoin Computer as `twenty-client`.
This will be the user identity for the client who will buy the file
that the `twenty-server` user is hosting.

Create a folder to house the client project:

    
    mkdir fileclient && cd fileclient
    

Now start editing a file named `client.py` in this directory and type in
the following code:

    
    #!/usr/bin/env python3
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
    
    def buy_file():
    
        # get the file listing from the server
        response = requests.get(url=server_url+'files')
        file_list = json.loads(response.text)
    
        # print the file list to the console
        for file in range(len(file_list)):
            print("{}. {}\t{}".format(file+1, file_list[str(file+1)][0], file_list[str(file+1)][1]))
    
        try:
            # prompt the user to input the index number of the file to be purchased
            sel = input("Please enter the index of the file that you would like to purchase:")
    
            # check if the input index is valid key in file_list dict
            if sel in file_list:
                print('You selected {} in our database'.format(file_list[sel][0]))
    
                #create a 402-payable request with the server payout address
                sel_url = server_url+'buy?selection={0}&payout_address={1}'
                answer = requests.get(url=sel_url.format(int(sel), wallet.get_payout_address()), stream=True)
    
                if answer.status_code != 200:
                   print("Could not make an offchain payment. Please check that you have sufficient balance.")
                else:
    
                   # open a file with the same name as the file being purchased and stream the data into it.
                   filename = file_list[str(sel)][0]
                   with open(filename,'wb') as fd:
                      for chunk in answer.iter_content(4096):
                        fd.write(chunk)
                   fd.close()
                   print('Congratulations, you just purchased a file for bitcoin!')     
    
            else:
                print("That is an invalid selection.")
    
        except ValueError:
            print("That is an invalid input. Only numerical inputs are accepted.")
    
    if __name__ == '__main__':
        buy_file()
    

Save this file and close it. Now run your client script with the following command:

    
    python3 client.py
    

If all goes well, you should see a prompt for the files you can buy on
the server, along with the price of those files. Execute a purchase
and you should see the `twenty-client` balance decrease and the
`twenty-server` balance increase. You can confirm this by running `21
log` as the `twenty-client` and the `twenty-server` user
respectively. And as the `twenty-server` user, you can flush your
winnings to the blockchain by doing `21 flush`.

## Next Steps

Now that you have the basic loop working, if you want to add more
files you can get inspiration from some of the following resources:

* [Project Gutenberg: free ebooks][141] (pdfs)
* [Creative Commons music][142] (mp3s)
* [Creative Commons videos][143] (mp4s)
* [Free icons][144] (pngs)
* [BSD-licensed code][145] (software)

These are for inspiration only, to get a sense of what kinds of
digital goods people value on the internet. It is your responsibility
to make sure that you have the license to sell or resell these items!
Not all public domain or Creative Commons material is licensed for
resale, and some of it is only licensed outside the US.

Subject to that proviso, there are an essentially infinite list of
things you can sell in this fashion - books, tutorials, music, movies,
icons, photos, artwork, podcasts, code, Excel templates, PSD files,
recordings, and the like. One of the most interesting applications
would be re-selling bundles of your Instagram photos, Youtube videos,
or Soundcloud recordings - anything that you've curated or assembled
on social media where you created it and possess the license. We
already know these items
[have some value][146],
but we have only begun in terms of the peer-to-peer social monetization of digital
goods with bitcoin!

One other note: please also know that if you want to set this up as a
production-grade server to sell files for bitcoin, you'll want to do
something more robust than the simple `server.py` script. For now,
take a look at
[this][147]
and [this][148]
article; we'll be integrating these instructions into the application
code in the near future.

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
browse and purchase from other bitcoin-enabled servers? Head over to the [21 Developer Community][149] at slack.21.co to join the bitcoin machine-payable marketplace hosted on the 21 peer-to-peer
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
Ronak Mehta

If you have any questions or issues, please drop us a line at [\[email protected\] ][151] or join our [Slack ][4] community.

This content is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License][152].


(c) 2016, 21.co

[Get The 21 Bitcoin Computer][3]


[0]: /
[1]: /setup/
[2]: /learn/
[3]: /buy/
[4]: https://slack.21.co
[5]: /bitnodes/
[6]: /about/
[7]: #sell-or-license-any-file-for-bitcoin "Sell or License Any File for Bitcoin"
[8]: #overview "Overview"
[9]: #prerequisites "Prerequisites"
[10]: #step-1-set-up-client-and-server-accounts "Step 1: Set up client and server accounts."
[11]: #step-2-create-a-server-to-sell-digital-goods-for-bitcoin "Step 2: Create a server to sell digital goods for bitcoin"
[12]: #step-3-create-a-client-to-buy-digital-goods-for-bitcoin "Step 3: Create a client to buy digital goods for bitcoin"
[13]: #next-steps "Next Steps"
[14]: /learn/ "< Back To Index"
[15]: https://twitter.com/intent/tweet?text=Hmm. This looks like a good resource for learning how to build Bitcoin apps:&url=https%3A//21.co/learn/sell-or-license-any-file-for-bitcoin/
[16]: https://www.facebook.com/sharer/sharer.php?u=https%3A//21.co/learn/sell-or-license-any-file-for-bitcoin/
[17]: /cdn-cgi/l/email-protection#102f366365727a7573642d44787963307c7f7f7b63307c797b75307130777f7f74306275637f6562737530767f62307c7571627e797e7730787f6730647f30726579Xld Bitcoin apps&body=Here's the URL: https%3A//21.co/learn/sell-or-license-any-file-for-bitcoin/
[18]: ../introduction-to-the-21-bitcoin-computer/
[19]: /setup
[20]: ../21-multiple-users
[21]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-1
[22]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-2
[23]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-3
[24]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-4
[25]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-5
[26]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-6
[27]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-7
[28]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-8
[29]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-9
[30]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-10
[31]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-11
[32]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-12
[33]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-13
[34]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-14
[35]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-15
[36]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-16
[37]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-17
[38]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-18
[39]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-19
[40]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-20
[41]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-21
[42]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-22
[43]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-23
[44]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-24
[45]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-25
[46]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-26
[47]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-27
[48]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-28
[49]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-29
[50]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-30
[51]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-31
[52]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-32
[53]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-33
[54]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-34
[55]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-35
[56]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-36
[57]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-37
[58]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-38
[59]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-39
[60]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-40
[61]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-41
[62]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-42
[63]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-43
[64]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-44
[65]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-45
[66]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-46
[67]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-47
[68]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-48
[69]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-49
[70]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-50
[71]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-51
[72]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-52
[73]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-53
[74]: #code-ba9c5d616c5521249a50c536fddca96cdf6aff76-54
[75]: #code-1c4fe80353cd81a398bbb8039e67c57895f18021-1
[76]: #code-1c4fe80353cd81a398bbb8039e67c57895f18021-2
[77]: #code-1c4fe80353cd81a398bbb8039e67c57895f18021-3
[78]: #code-1c4fe80353cd81a398bbb8039e67c57895f18021-4
[79]: #code-1c4fe80353cd81a398bbb8039e67c57895f18021-5
[80]: #code-1c4fe80353cd81a398bbb8039e67c57895f18021-6
[81]: /cdn-cgi/l/email-protection
[82]: #code-d3b8a40c20692de73193312072e8d597700b58be-1
[83]: #code-d3b8a40c20692de73193312072e8d597700b58be-2
[84]: #code-d3b8a40c20692de73193312072e8d597700b58be-3
[85]: #code-d3b8a40c20692de73193312072e8d597700b58be-4
[86]: #code-d3b8a40c20692de73193312072e8d597700b58be-5
[87]: #code-d3b8a40c20692de73193312072e8d597700b58be-6
[88]: #code-d3b8a40c20692de73193312072e8d597700b58be-7
[89]: #code-d3b8a40c20692de73193312072e8d597700b58be-8
[90]: #code-d3b8a40c20692de73193312072e8d597700b58be-9
[91]: #code-d3b8a40c20692de73193312072e8d597700b58be-10
[92]: #code-d3b8a40c20692de73193312072e8d597700b58be-11
[93]: #code-d3b8a40c20692de73193312072e8d597700b58be-12
[94]: #code-d3b8a40c20692de73193312072e8d597700b58be-13
[95]: #code-d3b8a40c20692de73193312072e8d597700b58be-14
[96]: #code-d3b8a40c20692de73193312072e8d597700b58be-15
[97]: #code-d3b8a40c20692de73193312072e8d597700b58be-16
[98]: #code-d3b8a40c20692de73193312072e8d597700b58be-17
[99]: #code-d3b8a40c20692de73193312072e8d597700b58be-18
[100]: #code-d3b8a40c20692de73193312072e8d597700b58be-19
[101]: #code-d3b8a40c20692de73193312072e8d597700b58be-20
[102]: #code-d3b8a40c20692de73193312072e8d597700b58be-21
[103]: #code-d3b8a40c20692de73193312072e8d597700b58be-22
[104]: #code-d3b8a40c20692de73193312072e8d597700b58be-23
[105]: #code-d3b8a40c20692de73193312072e8d597700b58be-24
[106]: #code-d3b8a40c20692de73193312072e8d597700b58be-25
[107]: #code-d3b8a40c20692de73193312072e8d597700b58be-26
[108]: #code-d3b8a40c20692de73193312072e8d597700b58be-27
[109]: #code-d3b8a40c20692de73193312072e8d597700b58be-28
[110]: #code-d3b8a40c20692de73193312072e8d597700b58be-29
[111]: #code-d3b8a40c20692de73193312072e8d597700b58be-30
[112]: #code-d3b8a40c20692de73193312072e8d597700b58be-31
[113]: #code-d3b8a40c20692de73193312072e8d597700b58be-32
[114]: #code-d3b8a40c20692de73193312072e8d597700b58be-33
[115]: #code-d3b8a40c20692de73193312072e8d597700b58be-34
[116]: #code-d3b8a40c20692de73193312072e8d597700b58be-35
[117]: #code-d3b8a40c20692de73193312072e8d597700b58be-36
[118]: #code-d3b8a40c20692de73193312072e8d597700b58be-37
[119]: #code-d3b8a40c20692de73193312072e8d597700b58be-38
[120]: #code-d3b8a40c20692de73193312072e8d597700b58be-39
[121]: #code-d3b8a40c20692de73193312072e8d597700b58be-40
[122]: #code-d3b8a40c20692de73193312072e8d597700b58be-41
[123]: #code-d3b8a40c20692de73193312072e8d597700b58be-42
[124]: #code-d3b8a40c20692de73193312072e8d597700b58be-43
[125]: #code-d3b8a40c20692de73193312072e8d597700b58be-44
[126]: #code-d3b8a40c20692de73193312072e8d597700b58be-45
[127]: #code-d3b8a40c20692de73193312072e8d597700b58be-46
[128]: #code-d3b8a40c20692de73193312072e8d597700b58be-47
[129]: #code-d3b8a40c20692de73193312072e8d597700b58be-48
[130]: #code-d3b8a40c20692de73193312072e8d597700b58be-49
[131]: #code-d3b8a40c20692de73193312072e8d597700b58be-50
[132]: #code-d3b8a40c20692de73193312072e8d597700b58be-51
[133]: #code-d3b8a40c20692de73193312072e8d597700b58be-52
[134]: #code-d3b8a40c20692de73193312072e8d597700b58be-53
[135]: #code-d3b8a40c20692de73193312072e8d597700b58be-54
[136]: #code-d3b8a40c20692de73193312072e8d597700b58be-55
[137]: #code-d3b8a40c20692de73193312072e8d597700b58be-56
[138]: #code-d3b8a40c20692de73193312072e8d597700b58be-57
[139]: #code-d3b8a40c20692de73193312072e8d597700b58be-58
[140]: #code-d3b8a40c20692de73193312072e8d597700b58be-59
[141]: https://www.gutenberg.org/
[142]: http://freemusicarchive.org/curator/Creative_Commons/
[143]: https://soosck.wordpress.com/2010/11/04/20-open-source-movies-edit-redistribute-free/
[144]: https://www.iconfinder.com/free_icons
[145]: https://www.google.com/?gws_rd=ssl#q=site:github.com+%22BSD+license%22
[146]: http://www.fastcompany.com/3032732/most-creative-people/how-brands-are-using-your-best-instagram-shots-for-more-authentic-marketing
[147]: http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvii-deployment-on-linux-even-on-the-raspberry-pi
[148]: http://tutos.readthedocs.org/en/latest/source/ndg.html
[149]: https://slack.21.co/
[150]: /cdn-cgi/l/email-protection#6e51481d1b0c040b0d1a533a06071d4e020101051d4e0207050b4e0f4e0901010a4e1c0b1d011b1c0d0b4e08011c4e020b0f1c000700094e0601194e1a014e0c1b07Xld Bitcoin apps&body=Here's the URL: https%3A//21.co/learn/sell-or-license-any-file-for-bitcoin/
[151]: /cdn-cgi/l/email-protection#3b484e4b4b54494f7b090a155854
[152]: https://creativecommons.org/licenses/by-sa/4.0/
[153]: //twitter.com/21
[154]: //medium.com/@21
