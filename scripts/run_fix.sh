#!/bin/bash
aliyun ecs RunCommand --RegionId me-east-1 --InstanceId i-eb3ce85peqozeocmrwtd --Type RunShellScript --CommandContent "
export KUBECONFIG=/etc/kubernetes/admin.conf
# Check port 80
netstat -tulpn | grep :80 || true

# Apply fix
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kosmos-frontend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kosmos-frontend
  template:
    metadata:
      labels:
        app: kosmos-frontend
    spec:
      containers:
        - name: kosmos-frontend
          image: kosmos-frontend:v1.0.0
          imagePullPolicy: Never
          ports:
            - containerPort: 3000
              hostPort: 80
          env:
            - name: NEXT_PUBLIC_API_URL
              value: \"http://kosmos-backend:8000\"
            - name: API_INTERNAL_URL
              value: \"http://kosmos-backend:8000\"
EOF

kubectl rollout restart deployment kosmos-frontend
"
