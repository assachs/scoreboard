
sudo mkdir -p /etc/scoreboard
if [ ! -f /etc/scoreboard/match.json ]
then
  sudo cp scoreboard/files/match-sample.json /etc/scoreboard/match.json
fi


chmod 755 scoreboard/rgb/scoreboard.py
chmod 755 scoreboard/sb

sudo cp /home/pi/scoreboard/files/scoreboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable scoreboard.service

sudo rm -fr /home/pi/stomp_ws_py
git clone https://github.com/assachs/stomp_ws_py.git
sudo apt install fonts-freefont-otf python3-websocket otf2bdf

. ~/scoreboard/files/installfonts.sh

cd ~

