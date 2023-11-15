pipeline {
  agent any
    stages {
      stage('Lint') {
        agent {
          docker {
            image 'python:3.11.3-buster'
            args '-u 0'
          }
        }
        when {
          anyOf {
            branch pattern: "feature-*"
            branch pattern: "fix-*"
          }
        }
        steps {
          sh "pip install poetry"
          sh "poetry install --with dev"
          sh "poetry run -- black --check *.py"
        }
      }
      stage('Build') {
      when {
        anyOf {
          branch pattern: "master"  
        }
      }
      steps {
        script {
          def image = docker.build "gosuooops/dos14-authz:${env.GIT_COMMIT}"
          docker.withRegistry('','dockerhub-ev') {
            image.push()
          build = "${env.GIT_COMMIT}"  
          }
        }
      }
    }
    stage('Update Helm Chart') {
      when {
        expression {
          build == "${env.GIT_COMMIT}" &&  "${env.BRANCH_NAME}" == "master"
        }
       }
      steps {
        sh "git checkout feature-helm-CD"
        sh "git config --global pull.rebase true"
        sh "git pull origin"
        script {
        def filename = 'charts/authz/values-aws-prd.yaml'
        def data = readYaml file: filename

        // Change something in the file
        data.image.tag = "${env.GIT_COMMIT}"

        sh "rm $filename"
        writeYaml file: filename, data: data

          withCredentials([string(credentialsId: 'ken_github_token', variable: 'SECRET')]) {
                sh('git config --global user.email "evgenii_neo@mail.ru" && git config --global user.name "Jenkins"')
                sh('git add .')
                sh('git commit -m "JENKINS: add image tag in helm chart tag for CD"')
                sh('git remote set-url origin https://${SECRET}@github.com/GosuOoops/dos14--Kuchko_Evgenii-git-flow.git')
                sh('git push origin feature-helm-CD')
          }
        }
      }
    }
  }
}
