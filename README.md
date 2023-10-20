# apigw-cicd-dashboard
Dashboard showing deployed assets for wM API Gateway. Based on Python and run via Docker.

# run repo
```
docker build -t dashboard:0.9 .
docker run -d -p 8080:8080 dashboard:0.9
```

# upload image to repo
```
docker image tag dashboard:0.9 sagtestclient/aron-docker:dashboard-1.0
docker image push sagtestclient/aron-docker:dashboard-1.0
```

# start and stop aks cluster
```
Start-AzAksCluster -Name dashboard -ResourceGroupName $resourcegroupname -SubscriptionId $subscriptionid
Stop-AzAksCluster  -Name dashboard -ResourceGroupName $resourcegroupname -SubscriptionId $subscriptionid
```

# use ADO to build and deploy image
The ADO pipeline is triggered by the creation of tags.
When you create a new tag, the pipeline builds (and publishes) the new version of the image.
Next the image will be deployed to the AKS cluster, using the the k8s deployment manifest in this repo.

create a new tag
> git tag 1.0

push tag to repo
> git push origin 1.0

delete tag locally
> git tag --delete 1.0