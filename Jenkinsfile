// Versioning - edit these variables to set version information
def dockerfileVersion = '1.0.1'
def nodeVersion = '12.16.0'

// Constants
def registry = 'defradigital'
def imageNameDevelopment = 'node-development'
def imageNameProduction = 'node'
def regCredsId = DOCKERHUB_CREDENTIALS_ID
def gitHubCredsId = GITHUB_CREDENTIALS_ID

// Variables
def repoUrl = ''
def commitSha = ''
def versionTag = ''
def imageRepositoryDevelopment = ''
def imageRepositoryProduction = ''
def imageRepositoryDevelopmentLatest = ''
def imageRepositoryProductionLatest = ''

def abortIfNotMaster() {
  if(BRANCH_NAME == 'master') {
    echo 'Building master branch'
  } else {
    currentBuild.result = 'ABORTED'
    error('Build aborted - not a master branch')
  }
}

def setVariables() {
  repoUrl = getRepoUrl()
  commitSha = getCommitSha()
  versionTag = "${dockerfileVersion}-node${nodeVersion}"
  imageRepositoryDevelopment = "$registry/$imageNameDevelopment:$versionTag"
  imageRepositoryProduction = "$registry/$imageNameProduction:$versionTag"
  imageRepositoryDevelopmentLatest = "$registry/$imageNameDevelopment"
  imageRepositoryProductionLatest = "$registry/$imageNameProduction"
}

def getRepoUrl() {
  return sh(returnStdout: true, script: "git config --get remote.origin.url").trim()
}

def getCommitSha() {
  return sh(returnStdout: true, script: "git rev-parse HEAD").trim()
}

def updateGithubCommitStatus(message, state) {
  step([
    $class: 'GitHubCommitStatusSetter',
    reposSource: [$class: "ManuallyEnteredRepositorySource", url: repoUrl],
    commitShaSource: [$class: "ManuallyEnteredShaSource", sha: commitSha],
    errorHandlers: [[$class: 'ShallowAnyErrorHandler']],
    statusResultSource: [ $class: "ConditionalStatusResultSource", results: [[$class: "AnyBuildResult", message: message, state: state]] ]
  ])
}

def buildImage(image, target) {
  sh "docker build --no-cache \
    --tag $image \
    --build-arg NODE_VERSION=${nodeVersion} \
    --build-arg VERSION=$dockerfileVersion \
    --target $target \
    ."
}

def pushImage(image) {
  docker.withRegistry('', regCredsId) {
    sh "docker push $image"
  }
}

node {
  checkout scm
  try {
    stage('Check master branch') {
      abortIfNotMaster()
    }
    stage('Set GitHub status pending') {
      updateGithubCommitStatus('Build started', 'PENDING')
    }
    stage('Set variables') {
      setVariables()
    }
    stage('Build development image') {
      buildImage(imageRepositoryDevelopment, 'development')
      buildImage(imageRepositoryDevelopmentLatest, 'development')
    }
    stage('Build production image') {
      buildImage(imageRepositoryProduction, 'production')
      buildImage(imageRepositoryProductionLatest, 'production')
    }
    stage('Push development image') {
      pushImage(imageRepositoryDevelopment)
      pushImage(imageRepositoryDevelopmentLatest)
    }
    stage('Push production image') {
      pushImage(imageRepositoryProduction)
      pushImage(imageRepositoryProductionLatest)
    }
    stage('Set GitHub status success') {
      updateGithubCommitStatus('Build successful', 'SUCCESS')
    }
  } catch(e) {
    stage('Set GitHub status failure') {
      updateGithubCommitStatus(e.message, 'FAILURE')
    }
    throw e
  }
}
