FROM ubuntu:14.04

SPP_VERSION_MAP = {
    "1.10.1": "/phantompeakqualtools/spp_1.10.1.tar.gz",
    "1.14":   "/phantompeakqualtools/spp-1.14.tar.gz"
}

bedtools

samtools

  "runSpec": {
    "interpreter": "python2.7",
    "file": "src/xcor.py",
    "execDepends": [
    {"name": "samtools",
      "package_manager": "git",
      "url": "https://github.com/samtools/samtools.git",
      "destdir": "/samtools-build",
      "tag": "0.1.19",
      "build_commands": "make samtools && cp samtools /usr/local/bin"},
    {"name": "bedtools",
      "package_manager": "git",
      "url": "https://github.com/arq5x/bedtools2.git",
      "destdir": "/bedtools-build",
      "tag": "v2.19.1",
      "build_commands": "make && cp bin/* /usr/local/bin"},
    {"name": "libboost1.46-dev"},
    {"name": "libboost-dev"},
    {"name": "caTools", "package_manager": "cran"},
    {"name": "snow", "package_manager": "cran"}
    ]
  },

  Rscript

