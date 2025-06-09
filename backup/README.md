#

[Bot](https://www.linkedin.com/pulse/linkedin-apply-bot-amin-boulouma/?trk=pulse-article)

[Profile Manager](https://support.mozilla.org/en-US/kb/profile-manager-create-remove-switch-firefox-profiles#:~:text=open%2C%20as%20follows%3A-,Creating%20a%20profile,such%20as%20your%20personal%20name.)
```
firefox.exe -P
```

## Assets Needed

java

python 3.10+

- Optional

[geckodriver](https://github.com/mozilla/geckodriver/releases)

## Selenium

[Selenium Server](https://selenium-release.storage.googleapis.com/index.html?path=3.5/)

[Selenium - Easily Setup a Hub and Node](https://www.toolsqa.com/selenium-webdriver/selenium-grid-how-to-easily-setup-a-hub-and-node/)

- Optional

[Selenium](https://www.selenium.dev/documentation/grid/getting_started/)

```
java -jar selenium-server-4.8.3.jar hub

java -jar selenium-server-4.8.3.jar -role node -hub http://192.168.56.1:4444/grid/register -port 4000
```

## Windows

```
java -jar selenium-server-standalone-3.5.3.jar -role hub

java -jar selenium-server-standalone-3.5.3.jar -role node -hub http://198.18.1.109:4444/grid/register -port 4000
```

## Ubuntu

```
java -jar selenium-server-standalone-3.5.3.jar -role hub

java -jar selenium-server-standalone-3.5.3.jar -role node -hub http://10.116.0.2:4444/grid/register -port 4000
```

[ubuntu desktop](https://docs.digitalocean.com/tutorials/droplet-desktop/)

Optional - [ubuntu desktop](https://phoenixnap.com/kb/how-to-install-a-gui-on-ubuntu)

[java install](https://itsfoss.com/run-java-program-ubuntu/)

[python install](https://phoenixnap.com/kb/how-to-install-python-3-ubuntu)

[pip install](https://www.odoo.com/forum/help-1/how-to-install-pip-in-python-3-on-ubuntu-18-04-167715)

https://dev.to/mistryvatsal/microblog-create-a-new-non-root-user-with-sudo-privileges-on-ubuntu-based-digitalocean-droplet-configured-with-ssh-1l3#:~:text=Login%20to%20your%20droplet%20using,bash%20or%20PuTTY(Windows).&text=Create%20a%20new%20user%2C%20%3Cnew,%3E%20with%20your%20desired%20username).&text=Let%20us%20add%20the%20%3Cnew,to%20get%20the%20sudo%20privileges.&text=Create%20a%20file%20named%20authorized_keys%20and%20paste%20your%20SSH%20key%20in%20there.

https://code.visualstudio.com/docs/setup/linux
