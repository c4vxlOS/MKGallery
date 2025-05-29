# !/bin/bash
sudo rm -R /usr/bin/mkgallery /usr/bin/mkgallery-server /usr/bin/mkgallery_src
sudo mkdir -p /usr/bin/mkgallery_src/

python3 build.py

python3 -m pip install requests flask --break-system-packages

sudo cp -R main.py /usr/bin/mkgallery_src/
sudo cp -R server.py /usr/bin/mkgallery_src/

sudo tee /usr/bin/mkgallery_src/mkgallery.sh <<EOF
# !/bin/bash
python3 /usr/bin/mkgallery_src/main.py "\$@"
EOF

sudo tee /usr/bin/mkgallery_src/mkgallery-server.sh <<EOF
# !/bin/bash
python3 /usr/bin/mkgallery_src/server.py "\$@"
EOF

sudo chmod -R 777 /usr/bin/mkgallery_src/
sudo ln -s /usr/bin/mkgallery_src/mkgallery.sh /usr/bin/mkgallery
sudo ln -s /usr/bin/mkgallery_src/mkgallery-server.sh /usr/bin/mkgallery-server
sudo chmod 777 /usr/bin/mkgallery
sudo chmod 777 /usr/bin/mkgallery-server