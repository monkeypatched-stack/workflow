
# docker build 
sudo docker build -t monkeypatched/index-documents-worker:latest . --no-cache

# docker run
docker run --network host -d -p 5672:5672 -p 9092:9092 monkeypatched/index-documents-worker:latest

