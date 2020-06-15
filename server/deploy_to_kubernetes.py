import os

deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: make{}
  labels:
    app: make{}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: make{}
  template:
    metadata:
      labels:
        app: make{}
    spec:
      containers:
        - name: make{}
          image: ddatsko/concurrent_make:latest
          ports:
            - containerPort: 3000
          imagePullPolicy: Always
"""

service = """
apiVersion: v1
kind: Service
metadata:
  name: make-service{}
spec:
  type: LoadBalancer
  selector:
    app: make{}
  ports:
    - name: main
      protocol: TCP
      port: 443
      targetPort: 3000
"""

for i in range(5):
    open('deployment.yaml', 'w').write(deployment.format(*([i] * 5)))
    open('service.yaml', 'w').write(service.format(i, i))
    os.system('kubectl apply -f deployment.yaml')
    os.system('kubectl apply -f service.yaml')

