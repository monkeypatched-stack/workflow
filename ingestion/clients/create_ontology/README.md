
# Router
Data Ingestion pipeline create ontology client

# docker build 
sudo docker build -t monkeypatched/create-ontology-client:latest . --no-cache


docker run --network host -d -p 5672:5672 -p 9092:9092 monkeypatched/ontology-worker:latest

