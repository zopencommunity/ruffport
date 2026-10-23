node('linux') {
    stage ('Poll') {
      checkout([
        $class: 'GitSCM', branches: [[name: '*/main']], extensions: [],
        userRemoteConfigs: [[url: 'https://github.com/zopencommunity/ruffport.git']]])
    }
    stage('Build') {
      build job: 'Port-Pipeline', parameters: [
        string(name: 'PORT_GITHUB_REPO', value: 'https://github.com/zopencommunity/ruffport.git'),
        string(name: 'PORT_DESCRIPTION', value: 'An extremely fast Python linter and code formatter'),
        string(name: 'BUILD_LINE', value: 'DEV')
      ]
    }
}
