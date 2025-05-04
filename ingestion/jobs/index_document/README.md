# build
sudo docker build -t monkeypatched/index-job:latest . --no-cache

# run
sudo docker run --network host monkeypatched/index-job:latest

# login 
aws ecr get-login-password | docker login --username AWS --password-stdin 390200632117.dkr.ecr.us-east-1.amazonaws.com

# create repo 
aws ecr create-repository --repository-name index-job

# tag
docker tag monkeypatched/index-job:latest 390200632117.dkr.ecr.us-east-1.amazonaws.com/index-job:latest

# push
docker push 390200632117.dkr.ecr.us-east-1.amazonaws.com/index-job:latest