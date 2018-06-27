pipeline {
    agent { node { label 'jenkins-gcp-agent' } }

    stages {
        stage('Build & Test') {
            steps {
                sshagent (credentials: ['jenkins-github-private-key']) {
                    sh 'make docker_test'
                }
            }
        }
        stage('Release') {
            steps {
                withCredentials([string(credentialsId: 'pypi', variable: 'TWINE_PASSWORD')]) {
                    sh 'make docker_release'
                }
            }
        }
    }

    post {
        always {
            junit 'tests/*.xml'
        }
        success {
            notifyBuild 'success'
        }
        unstable {
            notifyBuild 'unstable'
        }
        failure {
            notifyBuild 'failure'
        }
    }
}

def notifyBuild(String status) {
    def colors = [ success: 'good', unstable: 'warning', failure: 'danger' ]
    def version = readFile 'VERSION'
    def message = "Build ${status} for ${env.JOB_NAME}:${version}\n${env.BUILD_URL}"
    slackSend color: colors[status], message: message
}
