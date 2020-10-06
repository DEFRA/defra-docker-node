@Library('defra-docker-jenkins@initial-setup') _

import uk.gov.defra.ImageMap

ImageMap[] imageMaps = [
  [version: '8.17.0', tag: '8.17.0-alpine', latest: false],
  [version: '12.18.3', tag: '12.18.3-alpine3.12', latest: true],
]

buildParentImage imageName: 'node',
  imageMaps: imageMaps,
  version: '1.2.0'
