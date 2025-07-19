pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.11'
        DOCKER_IMAGE = 'fastapi-project'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Python') {
            steps {
                sh '''
                    python3 -m pip install --upgrade pip
                    python3 -m pip install virtualenv
                    python3 -m virtualenv venv
                    source venv/bin/activate
                    pip install -r requirements.txt
                    pip install pytest-cov pytest-asyncio httpx flake8 black isort bandit safety
                '''
            }
        }
        
        stage('Lint') {
            steps {
                sh '''
                    source venv/bin/activate
                    flake8 app/ tests/ --max-line-length=88 --extend-ignore=E203,W503
                    black --check app/ tests/
                    isort --check-only app/ tests/
                '''
            }
        }
        
        stage('Test') {
            environment {
                DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/test_db'
                SECRET_KEY = 'test-secret-key-for-jenkins'
                DEBUG = 'true'
            }
            steps {
                sh '''
                    source venv/bin/activate
                    pytest tests/ -v --cov=app --cov-report=xml --cov-report=term-missing
                '''
            }
            post {
                always {
                    publishCoverage adapters: [coberturaAdapter('coverage.xml')], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                sh '''
                    source venv/bin/activate
                    bandit -r app/ -f json -o bandit-report.json || true
                    safety check --json --output safety-report.json || true
                '''
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'bandit-report.json',
                        reportName: 'Bandit Security Report'
                    ])
                }
            }
        }
        
        stage('Build Docker Image') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                    tag 'v*'
                }
            }
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                    docker.build("${DOCKER_IMAGE}:latest")
                }
            }
        }
        
        stage('Push Docker Image') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                    tag 'v*'
                }
            }
            steps {
                script {
                    docker.withRegistry('https://your-registry.com', 'docker-registry-credentials') {
                        docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push()
                        docker.image("${DOCKER_IMAGE}:latest").push()
                    }
                }
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                sh '''
                    ssh user@staging-server "cd /opt/fastapi-project && \
                    docker-compose pull && \
                    docker-compose up -d && \
                    sleep 10 && \
                    curl -f http://localhost:8000/health"
                '''
            }
        }
        
        stage('Deploy to Production') {
            when {
                tag 'v*'
            }
            input {
                message "Deploy to production?"
                ok "Deploy"
            }
            steps {
                sh '''
                    ssh user@production-server "cd /opt/fastapi-project && \
                    docker-compose pull && \
                    docker-compose up -d && \
                    sleep 10 && \
                    curl -f http://localhost:8000/health"
                '''
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
} 