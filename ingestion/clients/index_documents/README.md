
# Router
Data Ingestion pipeline create ontology client

# docker build 
sudo docker build -t monkeypatched/index-document-client:latest . --no-cache


docker run --network host -d  monkeypatched/index-document-client:latest