# Router
Data Ingestion pipeline router

# docker build 
sudo docker build -t monkeypatched/router:latest . --no-cache

# docker run
docker run --network host -d  -p 6789:6789 monkeypatched/router:latest

# login 
aws ecr get-login-password | docker login --username AWS --password-stdin 390200632117.dkr.ecr.us-east-1.amazonaws.com

# create repo 
aws ecr create-repository --repository-name router

# tag
docker tag monkeypatched/router:latest 390200632117.dkr.ecr.us-east-1.amazonaws.com/router:latest

# push
docker push 390200632117.dkr.ecr.us-east-1.amazonaws.com/router:latest

