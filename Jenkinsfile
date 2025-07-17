pipeline {
    agent { label 'node-label' }
    stages {
        stage('Setup and Test') {
            agent {
                docker {
                    image 'python:3.10'
                    args '-v $WORKSPACE:/workspace'
                }
            }
            steps {
                // Install dependencies
                sh 'pip install -r requirements.txt'
                // Run the main test script
                sh 'python tacho_test.py'
            }
        }
        stage('Archive Logs') {
            steps {
                // Archive CSV logs as Jenkins artifacts
                archiveArtifacts artifacts: 'csv_logs/*.csv', allowEmptyArchive: true
            }
        }
    }
}