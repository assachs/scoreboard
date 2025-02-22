
sudo mkdir -p /etc/scoreboard
sudo cp scoreboard/files/match-sample.json /etc/scoreboard/match.json

chmod 755 scoreboard/rgb/scoreboard.py
chmod 755 scoreboard/sb

sudo cp /home/pi/scoreboard/files/scoreboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable scoreboard.service

rm -fr /home/pi/stomp_ws_py
git clone https://github.com/assachs/stomp_ws_py.git
sudo apt install fonts-freefont-otf python3-websocket otf2bdf

cd ~/rpi-rgb-led-matrix/fonts/

otf2bdf -v -o FreeSans-36-20.bdf -r 36 -p 20 /usr/share/fonts/opentype/freefont/FreeSans.otf
otf2bdf -v -o FreeSans-72-30.bdf -r 72 -p 30 /usr/share/fonts/opentype/freefont/FreeSans.otf
otf2bdf -v -o FreeSans-72-66.bdf -r 72 -p 66 /usr/share/fonts/opentype/freefont/FreeSans.otf
otf2bdf -v -o FreeSans-72-66.bold.bdf -r 72 -p 66 /usr/share/fonts/opentype/freefont/FreeSansBold.otf

ln -s FreeSans-72-30.bdf saetze.bdf
ln -s FreeSans-72-66.bold.bdf punkte.bdf
ln -s FreeSans-72-66.bdf doppelpunkt.bdf
ln -s FreeSans-36-20.bdf teamnamen.bdf
ln -s FreeSans-36-20.bdf auszeit.bdf

cd ~

