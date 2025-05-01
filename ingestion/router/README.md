# Router
Data Ingestion pipeline router

# docker build 
sudo docker build -t monkeypatched/router:latest . --no-cache

# docker run
docker run --network host -d  -p 6789:6789 monkeypatched/router:latest
