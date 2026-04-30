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
                echo '📥 Checking out source code...'
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "🐳 Building ${FULL_IMAGE}:${BUILD_NUMBER}"
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
                echo '📦 Pushing image to GitHub Container Registry...'
                sh """
                    echo "${GITHUB_TOKEN}" | \
                        docker login ghcr.io -u ${GITHUB_USER} --password-stdin

                    docker push ${FULL_IMAGE}:${BUILD_NUMBER}
                    docker push ${FULL_IMAGE}:latest

                    echo "✅ Pushed ${FULL_IMAGE}:${BUILD_NUMBER} and :latest"
                """
            }
        }

        stage('Run on Docker') {
            steps {
                echo '🚀 Running the sales analyzer container...'
                sh """
                    # Remove old container if exists
                    docker rm -f ${CONTAINER_NAME} 2>/dev/null || true

                    # Run and save the HTML report to the host
                    docker run \
                        --name ${CONTAINER_NAME} \
                        -v \$(pwd)/output:/app/output \
                        ${FULL_IMAGE}:${BUILD_NUMBER} \
                        python app.py --out /app/output/report.html
                """
            }
        }

        stage('Show Results') {
            steps {
                echo '🔍 Verifying the container ran successfully...'
                sh """
                    echo "──────────── Container Exit Status ────────────"
                    EXIT_CODE=\$(docker inspect ${CONTAINER_NAME} --format='{{.State.ExitCode}}')
                    echo "Exit code: \$EXIT_CODE"

                    if [ "\$EXIT_CODE" != "0" ]; then
                        echo "❌ Script failed!"
                        docker logs ${CONTAINER_NAME}
                        exit 1
                    fi

                    echo "──────────── Container Logs ────────────────────"
                    docker logs ${CONTAINER_NAME}

                    echo "──────────── Output File ───────────────────────"
                    ls -lh output/report.html

                    echo "✅ Script ran successfully. Report saved to: \$(pwd)/output/report.html"
                """
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline #${BUILD_NUMBER} succeeded."
        }
        failure {
            echo '❌ Pipeline failed. Check logs above.'
        }
        always {
            sh 'docker logout ghcr.io || true'
            sh 'docker image prune -f || true'
            sh "docker rm -f ${CONTAINER_NAME} 2>/dev/null || true"
        }
    }
}
