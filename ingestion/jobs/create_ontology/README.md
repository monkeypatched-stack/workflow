# build
sudo docker build -t monkeypatched/ontology-job:latest . --no-cache

# run
sudo docker run --network host monkeypatched/ontology-job:latest

# login 
aws ecr get-login-password | docker login --username AWS --password-stdin 390200632117.dkr.ecr.us-east-1.amazonaws.com

# create repo 
aws ecr create-repository --repository-name ontology-job

# tag
docker tag monkeypatched/ontology-job:latest 390200632117.dkr.ecr.us-east-1.amazonaws.com/ontology-job:latest

# push
docker push 390200632117.dkr.ecr.us-east-1.amazonaws.com/ontology-job:latest