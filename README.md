# cookidump

Easily dump cookidoo recipes from the official website

### Description ###

This repo shows example how to modify [auino/cookidump](https://github.com/auino/cookidump) to dump collections and 
recipes, also re-login if logged out by the website. This repo is a teaching example, cloning and running this repo
is not recommended and who ever do that are responsible for any consequence. 

### Features ###

Beyonds [auino/cookidump](https://github.com/auino/cookidump), this adds 

* auto login and re-login if logged out
* dump collections and recipes

### Installation ###

1. Clone [auino/cookidump](https://github.com/auino/cookidump)'s repository:

    ```
    git clone https://github.com/auino/cookidump.git
    ```

2. Applies changes to implement features exampled in this repo. 

3. `cd` into the download folder

4. Install [Python](https://www.python.org) requirements:
    
    ```
    pip install -r requirements.txt
    ```

5. Install the [Google Chrome](https://chrome.google.com) browser, if not already installed

6. Download the [Chrome WebDriver](https://sites.google.com/a/chromium.org/chromedriver/) and save it on the `cookidump` folder

7. You are ready to dump your recipes

### Usage ###

Simply run the following command to start the program. The program is interactive to simplify it's usage.

```
python cookidump.py <webdriverfile> <outputdir> <email> <password>
```

where:
* `webdriverfile` identifies the path to the downloaded [Chrome WebDriver](https://sites.google.com/a/chromium.org/chromedriver/) (for instance, `chromedriver.exe` for Windows hosts, `./chromedriver` for Linux and macOS hosts)
* `outputdir` identifies the path of the output directory (will be created, if not already existent)

The program will open a [Google Chrome](https://chrome.google.com) window and wait until you are logged in into your [Cookidoo](https://cookidoo.co.uk) account (different countries are supported).

After that, follow instructions provided by the script itself to proceed with the dump.

### Disclaimer ###

I only modified a little bit on [auino/cookidump](https://github.com/auino/cookidump)'s project as an example to how 
to make certain changes that project to make process easier. Any user should not use this project directly, but clone
[auino/cookidump](https://github.com/auino/cookidump) and applies change hinted by this project.

The authors of this program are not responsible of the usage of it.
This program is released only for research and dissemination purposes.
Also, the program provides users the ability to locally and temporarily store recipes accessible through a legit subscription.
Before using this program, check Cookidoo subscription terms of service, according to the country related to the exploited subscription. 
Sharing of the obtained recipes is not a legit activity and the authors of this program are not responsible of any illecit and sharing activity accomplished by the users.

### Contacts ###

Please contact original author: [@auino](https://twitter.com/auino).
