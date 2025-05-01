# build
sudo docker build -t monkeypatched/index-job:latest . --no-cache

# run
sudo docker run --network host monkeypatched/index-job:latest