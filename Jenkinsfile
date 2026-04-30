pipeline {

    agent any

    environment {
        GITHUB_USER    = 'samuel2ayman'
        GITHUB_TOKEN   = credentials('github-token')
        IMAGE_NAME     = 'sales-analyzer'
        FULL_IMAGE     = "ghcr.io/samuel2ayman/sales-analyzer"
        CONTAINER_NAME = 'sales-analyzer'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 20, unit: 'MINUTES')
        timestamps()
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh """
                    docker build \
                        -t ${FULL_IMAGE}:${BUILD_NUMBER} \
                        -t ${FULL_IMAGE}:latest \
                        .
                """
            }
        }

        stage('Push to GHCR') {
            steps {
                sh """
                    echo "${GITHUB_TOKEN}" | \
                        docker login ghcr.io -u ${GITHUB_USER} --password-stdin

                    docker push ${FULL_IMAGE}:${BUILD_NUMBER}
                    docker push ${FULL_IMAGE}:latest
                """
            }
        }

        stage('Run on Docker') {
            steps {
                sh """
                    # Remove the old container if it exists
                    docker rm -f ${CONTAINER_NAME} 2>/dev/null || true

                    # Map to port 8081 on the host to avoid Jenkins conflict
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p 8081:80 \
                        --restart unless-stopped \
                        ${FULL_IMAGE}:${BUILD_NUMBER}
                """
            }
        }

        stage('Show Results') {
            steps {
                sh """
                    sleep 8

                    echo "------------ Container Status ------------"
                    docker ps --filter name=${CONTAINER_NAME}

                    echo "------------ Container Logs ------------"
                    docker logs ${CONTAINER_NAME}
                """
            }
        }
    }

    post {
        success {
            echo "Pipeline ${BUILD_NUMBER} succeeded."
        }
        failure {
            echo "Pipeline ${BUILD_NUMBER} failed."
        }
        always {
            sh 'docker logout ghcr.io || true'
            sh 'docker image prune -f || true'
        }
    }
}
