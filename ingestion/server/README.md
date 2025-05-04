# Server
Data Ingestion pipeline server

# docker build 
sudo docker build -t monkeypatched/server:latest . --no-cache

# docker run
docker run --network host -d  -p 6789:6789 monkeypatched/server:latest

# login 
aws ecr get-login-password | docker login --username AWS --password-stdin 390200632117.dkr.ecr.us-east-1.amazonaws.com

# create repo 
aws ecr create-repository --repository-name server

# tag
docker tag monkeypatched/server:latest 390200632117.dkr.ecr.us-east-1.amazonaws.com/server:latest

# push
docker push 390200632117.dkr.ecr.us-east-1.amazonaws.com/server:latest