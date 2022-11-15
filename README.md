# Ping
This telegram bot is written on python with the help of [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) . 
It checks whether there are links. For the databases used sqlite3. For check url [requests](https://github.com/psf/requests)
# Install 
## Linux
Check Python
```
python3 --version
```
If no download
```
sudo apt-get update
sudo apt-get install python3.10
```
Install the libraries
```
pip install python-dotenv
pip install pyTelegramBotAPI
pip install requests
```
Download app
```
git clone https://github.com/Archermysteri/ping.git
cd ping
```
Write down the token of the Bot's telegram
```
echo "TOKEN=YOUR_TOKEN" > .env
```
Start app
```
python main.py
```