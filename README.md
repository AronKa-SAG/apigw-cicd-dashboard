# apigw-cicd-dashboard
Dashboard showing deployed assets for wM API Gateway. Based on Python and run via Docker.

# run repo
```
docker build -t dashboard:0.9 .
docker run -d -p 8080:8080 dashboard:0.9
```