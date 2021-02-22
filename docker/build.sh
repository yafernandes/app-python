cd ..
docker build -t yaalexf/app-python -f docker/Dockerfile .
docker push yaalexf/app-python
cd -