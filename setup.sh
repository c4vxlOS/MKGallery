# !/bin/bash
sudo mkdir -p /usr/bin/makegallery/sh

python build.py

sudo cp -R index.py /usr/bin/makegallery/

cd /usr/bin/makegallery/sh/

sudo tee mkgallery.sh <<EOF
# !/bin/bash
python /usr/bin/makegallery/index.py "\$@"
EOF

sudo tee uninstall.sh <<EOF
# !/bin/bash
sudo rm /usr/bin/mkgallery
sudo rm -R /usr/bin/makegallery/
EOF

sudo chmod 777 -R ../sh/

sudo ln -s /usr/bin/makegallery/sh/mkgallery.sh /usr/bin/mkgallery
sudo chmod 777 -R /usr/bin/mkgallery