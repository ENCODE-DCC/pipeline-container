class: ExpressionTool

cwlVersion: v1.0

requirements:
  - class: InlineJavascriptRequirement

inputs:

  unfiltered_bam:
    type: File
    inputBinding:
      position: 1
  filtered_bam:
    type: File
    inputBinding:
      position: 2
  unfiltered_flagstat:
    type: File
    inputBinding:
      position: 3
  filtered_flagstat:
    type: File
    inputBinding:
      position: 4
  dup_qc:
    type: File
    inputBinding:
      position: 5
  pbc_qc:
    type: File
    inputBinding:
      position: 6
  mapping_log:
    type: File
    inputBinding:
      position: 7
  post_mapping_log:
    type: File
    inputBinding:
      position: 8
  filter_qc_log:
    type: File
    inputBinding:
      position: 9
  xcor_log:
    type: File
    inputBinding:
      position: 10
  cc:
    type: File
    inputBinding:
      position: 11
  cc_pdf:
    type: File
    inputBinding:
      position: 12
  mapping_json:
    type: File
    inputBinding:
      position: 13
  post_mapping_json:
    type: File
    inputBinding:
      position: 14
  filter_json:
    type: File
    inputBinding:
      position: 15
  xcor_json:
    type: File
    inputBinding:
      position: 16
  tag_align:
    type: File[]
    inputBinding:
      position: 17



outputs:
  folder: Directory

expression: |
  ${
    var now = new Date();
    var date = [ now.getMonth() + 1, now.getDate(), now.getFullYear() ];
    var time = [ now.getHours(), now.getMinutes(), now.getSeconds() ];
    for ( var i = 1; i < 3; i++ ) {
        if ( time[i] < 10 ) {
          time[i] = "0" + time[i];
        }
    }
    time[0] = time[0]+"H"
    time[1] = time[1]+"M"
    time[2] = time[2]+"S"
    var folder = {
      "class": "Directory",
      "basename": date.join("-") + "T" + time.join(""),
      "listing": []
    }
    var files = [];
    if (!Array.isArray(inputs.tag_align)){
      files.push (inputs.tag_align)
    } else {
      files = inputs.tag_align
    }
    files.push(inputs.cc_pdf)
    files.push(inputs.cc)
    files.push(inputs.xcor_log)
    files.push(inputs.filter_qc_log)
    files.push(inputs.post_mapping_log)
    files.push(inputs.mapping_log)
    files.push(inputs.pbc_qc)
    files.push(inputs.dup_qc)
    files.push(inputs.filtered_flagstat)
    files.push(inputs.unfiltered_flagstat)
    files.push(inputs.filtered_bam)
    files.push(inputs.unfiltered_bam)
    files.push(inputs.mapping_json)
    files.push(inputs.post_mapping_json)
    files.push(inputs.filter_json)
    files.push(inputs.xcor_json)
    for (var i = 0; i < files.length; i++){
      folder.listing.push(files[i])
    }
    return { "folder": folder };
  }
