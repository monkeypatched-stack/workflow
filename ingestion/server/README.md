# Server
Data Ingestion pipeline server

# docker build 
sudo docker build -t monkeypatched/server:latest . --no-cache

# docker run
docker run --network host -d  -p 6789:6789 monkeypatched/server:latest
