#!/bin/bash
# LinkOps Afterlife Deployment Script

set -e

echo "🚀 LinkOps Afterlife Deployment"
echo "==============================="

# Check if running in production or dev
ENV=${1:-dev}
echo "📍 Environment: $ENV"

# Docker build and push
echo "🔨 Building images..."
docker buildx build --platform linux/amd64 \
  -t ghcr.io/shadow-link-industries/linkops-afterlife-api:$ENV ./api --push

docker buildx build --platform linux/amd64 \
  -t ghcr.io/shadow-link-industries/linkops-afterlife-ui:$ENV ./ui --push

# K8s deployment
echo "☸️  Deploying to Kubernetes..."
kubectl apply -k k8s/overlays/$ENV

echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Check pods: kubectl get pods -n linkops-afterlife"
echo "2. Check services: kubectl get svc -n linkops-afterlife"
if [ "$ENV" = "prod" ]; then
    echo "3. Check ingress: kubectl get ingress -n linkops-afterlife"
    echo "4. Access at: https://demo.linkopsmlm.com"
else
    echo "3. Port forward: kubectl port-forward -n linkops-afterlife svc/dev-ui 5173:5173"
    echo "4. Access at: http://localhost:5173"
fi