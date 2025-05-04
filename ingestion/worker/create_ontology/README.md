
# docker build 
sudo docker build -t monkeypatched/create-ontology-worker:latest . --no-cache

# docker run
docker run --network host -d -p 5672:5672 -p 9092:9092 monkeypatched/create-ontology-worker:latest

# login 
aws ecr get-login-password | docker login --username AWS --password-stdin 390200632117.dkr.ecr.us-east-1.amazonaws.com

# create repo 
aws ecr create-repository --repository-name create-ontology-worker

# tag
docker tag monkeypatched/create-ontology-worker:latest 390200632117.dkr.ecr.us-east-1.amazonaws.com/create-ontology-worker:latest

# push
docker push 390200632117.dkr.ecr.us-east-1.amazonaws.com/create-ontology-worker:latest