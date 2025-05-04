
# docker build 
sudo docker build -t monkeypatched/index-documents-worker:latest . --no-cache

# docker run
docker run --network host -d -p 5672:5672 -p 9092:9092 monkeypatched/index-documents-worker:latest

# login 
aws ecr get-login-password | docker login --username AWS --password-stdin 390200632117.dkr.ecr.us-east-1.amazonaws.com

# create repo 
aws ecr create-repository --repository-name index-documents-worker

# tag
docker tag monkeypatched/index-documents-worker:latest 390200632117.dkr.ecr.us-east-1.amazonaws.com/index-documents-worker:latest

# push
docker push 390200632117.dkr.ecr.us-east-1.amazonaws.com/index-documents-worker:latest

