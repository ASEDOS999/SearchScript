#!/bin/bash 
sudo docker run --shm-size=1024m -d --rm -p 3334:3333 inemo/isanlp_udpipe
sudo docker run --rm -d -p 3333:3333 inemo/isanlp
