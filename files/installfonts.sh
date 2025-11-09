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