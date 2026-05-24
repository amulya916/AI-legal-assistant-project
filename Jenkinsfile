pipeline {
    agent any

    environment {
        // Define your Docker Hub Registry or ECR
        DOCKER_REGISTRY = "docker.io"
        IMAGE_NAME      = "your-dockerhub-username/ailegalproject"
        IMAGE_TAG       = "${BUILD_NUMBER}"
        KUBECONFIG_CREDENTIAL_ID = "kubernetes-config-id"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Lint & Unit Tests') {
            steps {
                echo 'Running unit tests...'
                // Spin up a temporary container to run tests
                sh 'docker build -t app-test-image:latest .'
                sh 'docker run --rm app-test-image:latest python -m unittest discover -s tests'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building production Docker image...'
                sh "docker build -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ."
                sh "docker tag ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest"
            }
        }

        stage('Push Docker Image') {
            steps {
                // Ensure Docker credentials are set up in Jenkins
                withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh "echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin ${DOCKER_REGISTRY}"
                    sh "docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                    sh "docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest"
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo 'Deploying to Kubernetes...'
                // Use Jenkins Kubernetes Credentials or kubeconfig tool to apply manifests
                withKubeConfig([credentialsId: "${KUBECONFIG_CREDENTIAL_ID}"]) {
                    // Replace image tag in deployment manifest dynamically
                    sh "sed -i 's|image: .*/ailegalproject:.*|image: ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}|g' k8s/deployment.yaml"
                    
                    // Apply manifests
                    sh "kubectl apply -f k8s/pvc.yaml"
                    sh "kubectl apply -f k8s/secret.yaml"
                    sh "kubectl apply -f k8s/deployment.yaml"
                    sh "kubectl apply -f k8s/service.yaml"
                    
                    // Verify rollout
                    sh "kubectl rollout status deployment/ailegalproject-deployment"
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution complete.'
            sh 'docker logout'
        }
        success {
            echo 'Application successfully built, tested, and deployed!'
        }
        failure {
            echo 'Deployment failed. Please check build logs.'
        }
    }
}
