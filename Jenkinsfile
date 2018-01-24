pipeline {
        agent {label 'master-builder'}


        stages {
		stage('Unit-tests') {
			steps { 
                                script{
                                        TAG = sh([script: "echo quay.io/encode-dcc/atac-seq-pipeline:${env.BUILD_NUMBER}", returnStdout: true]).trim()
                                }
				echo "Running unit tests.."
			}
		}
                stage('Build-nonmaster') {
                        when { not { branch 'master' } }
                        steps { 
                                echo "The TAG is $TAG"
                                slackSend "started job: ${env.JOB_NAME}, build number ${env.BUILD_NUMBER} on branch: ${env.BRANCH_NAME}."
				slackSend "The images will be tagged as ${env.BRANCH_NAME}:${env.BUILD_NUMBER}"
                                sh "./envtest.sh $env.BRANCH_NAME $env.BUILD_NUMBER"
                                // sh "docker login -u=ottojolanki -p=${QUAY_PASS} quay.io"
                                // sh "docker build --no-cache -t filter images/filter/"
                                // sh "docker tag filter quay.io/ottojolanki/filter:${env.BRANCH_NAME}"
                                // sh "docker push quay.io/ottojolanki/filter:${env.BRANCH_NAME}"
                                // sh "docker logout"
                        }
                }
                stage('Build-master') {
                        when { branch 'master'}
                        steps {
				slackSend "started job: ${env.JOB_NAME}, build number ${env.BUILD_NUMBER} on branch: ${env.BRANCH_NAME}."
				slackSend "The images will be tagged as ${env.BRANCH_NAME}:${env.BUILD_NUMBER}"
                                echo env.BRANCH_NAME
                                echo "Running master build steps."
                                // sh "docker login -u=ottojolanki -p=${QUAY_PASS} quay.io"
                                // sh "docker build --no-cache -t filter images/filter/"
                                // sh "docker tag filter quay.io/ottojolanki/filter:latest"
                                // sh "docker push quay.io/ottojolanki/filter:latest"
                                // sh "docker logout"
                        }
                }
        }
	post {
                success {
                        echo 'Post build actions that run on success'
                        slackSend "Job ${env.JOB_NAME}, build number ${env.BUILD_NUMBER} on branch ${env.BRANCH_NAME} finished successfully."
                }
                failure {
                        echo 'Post build actions that run on failure'
                        slackSend "Job ${env.JOB_NAME}, build number ${env.BUILD_NUMBER} on branch ${env.BRANCH_NAME} failed."
                }
                always {
                        echo 'Post build actions that run always'
                }
	}
}
