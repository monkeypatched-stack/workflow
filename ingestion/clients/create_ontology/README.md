
# Router
Data Ingestion pipeline create ontology client

# docker build 
sudo docker build -t monkeypatched/create-ontology-client:latest . --no-cache

# run
docker run --network host -d -p 5672:5672 -p 9092:9092 monkeypatched/create-ontology-client:latest


# login 
aws ecr get-login-password | docker login --username AWS --password-stdin 390200632117.dkr.ecr.us-east-1.amazonaws.com

# create repo 
aws ecr create-repository --repository-name create-ontology-client

# tag
docker tag monkeypatched/create-ontology-client:latest 390200632117.dkr.ecr.us-east-1.amazonaws.com/create-ontology-client:latest

# push
docker push 390200632117.dkr.ecr.us-east-1.amazonaws.com/create-ontology-client:latest


