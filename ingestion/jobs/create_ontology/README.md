# build
sudo docker build -t monkeypatched/ontology-job:latest . --no-cache

# run
sudo docker run --network host monkeypatched/ontology-job:latest