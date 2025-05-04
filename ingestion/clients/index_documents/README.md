
# Router
Data Ingestion pipeline create ontology client

# docker build 
sudo docker build -t monkeypatched/index-document-client:latest . --no-cache

# docker run
docker run --network host -d  monkeypatched/index-document-client:latest

# login 
aws ecr get-login-password | docker login --username AWS --password-stdin 390200632117.dkr.ecr.us-east-1.amazonaws.com

# create repo 
aws ecr create-repository --repository-name index-document-client

# tag
docker tag monkeypatched/index-document-client:latest 390200632117.dkr.ecr.us-east-1.amazonaws.com/index-document-client:latest

# push
docker push 390200632117.dkr.ecr.us-east-1.amazonaws.com/index-document-client:latest

