@Library('defra-docker-jenkins@v-2') _

import uk.gov.defra.ImageMap

ImageMap[] imageMaps = [
  [version: '12.18.3', tag: '12.18.3-alpine3.12', latest: false],
  [version: '14.15.3', tag: '14.15.3-alpine3.12', latest: true]
]

buildParentImage imageName: 'node',
  imageMaps: imageMaps,
  version: '1.2.3'
