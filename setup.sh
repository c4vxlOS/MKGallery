# !/bin/bash
sudo rm -R /usr/bin/mkgallery /usr/bin/mkgallery_src
sudo mkdir -p /usr/bin/mkgallery_src/

python build.py

sudo cp -R main.py /usr/bin/mkgallery_src/

sudo tee /usr/bin/mkgallery_src/mkgallery.sh <<EOF
# !/bin/bash
python /usr/bin/mkgallery_src/main.py "\$@"
EOF

sudo chmod -R 777 /usr/bin/mkgallery_src/
sudo ln -s /usr/bin/mkgallery_src/mkgallery.sh /usr/bin/mkgallery
sudo chmod 777 /usr/bin/mkgallery