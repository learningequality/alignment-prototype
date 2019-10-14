Data exports
============
This directory contains the raw data for curriculum structures and human judgments
you can use for training your models.

See http://alignmentapp.learningequality.org/files/exports/data/ for all exports
and http://alignmentapp.learningequality.org/files/exports/data/latest/ for the
most recent export folder.


Each data export folder contains the following files:

    .
    ├── metadata.json             # general info about when the export was done
    ├── curriculumdocuments.csv   # info about the curriculum documents included
    ├── standardnodes.csv         # detailed curriculum standard tree data (MAIN)
    ├── humanjudgments.csv        # human similarity judgments collected
    └── userprofiles.csv          # user profiles of the human reviewers


### curriculumdocuments.csv
Stores the metadata for a curriculum document, e.g. KICD standards for math.

  - `document_id` (int): a numeric identifier for the document (used for foreign keys)
  - `country`: the country
  - `title`: the official title
  - `digitization_method`: how the document was imported. Possible values are:
    - `manual_entry`: someone manually typed in the standard nodes
    - `scan_manual`: same as the above but starting with OCR
    - `automated_scan`: automated structure extraction via OCR+position data (Activity 1b)
    - `website_scrape`: curriculum scraped from website
    - `data_import`: structured curriculum data imported another database
  - `source_id` (str): a unique identifier for this document
  - `source_url`: and optional URL where the document was imported from
  - `created`: when the curriculum document was uploaded/created in the system



### standardnodes.csv
The individual elements of a curriculum structure.

  - `id` (int): a numeric identifier for the document (used for foreign keys)
  - `document_id` (FK): foreign key to `curriculumdocuments.document_id`
  - `depth` (int): distance from the root node 
  - `dist_from_leaf` (int): maximum distance from the a leaf node
  - `parent_id` (FK): the id of the parent node in the tree structure; empty for root nodes
  - `sort_order`: used to specify ordering of the nodes within the parent node
  - `identifier` (str): a short identifier or standard node, e.g. CCSS.Math.Content.K.OA.A.4.
    Not guaranteed to be present or unique for all standard nodes.
  - `kind` (str): indicates the type of node (e.g. level, subject area, topic, learning objective, etc.)
  - `title` (str): the main text description for this standard node
  - `time_units` (float): a numeric value ~= to the # hours of instruction for this unit or topic
  - `notes`: additional notes, description, and secondary text about this node
  - `extra_fields` (JSON): can contain arbitrary extra information available for this node


### humanjudgments.csv
Stores human feedback about relevance between two standard nodes `node1` and `node2`.
Similarity judgments are undirected.

  - `id`: a numeric identifier for this human judgment
  - `node1_id` (FK): foreign key to `standardnodes.id`  
  - `node2_id` (FK): foreign key to `standardnodes.id`
  - `rating` (float): relevance rating: min = 0.0 (not relevant at all), max = 1.0 (highly relevant)
  - `confidence` (float): an optional confidence level: 1.0= 100% sure, 50% depends, 0% just guessing
  - `mode` (str): indicates the how the human judgment was collected "rapid_feedback" vs. "manual_review" etc.
  - `user_id`: FK to the `userprofiles.id`
  - `extra_fields` (JSON): any additional data stored by the human judgement API (e.g. comments)


### userprofiles.csv
Info about the background and content knowledge of the users that provided human judgments.

  - `id`: the user id
  - `background`: what is the professional background of the user
  - `subject_areas`: semicolon-separated list of areas of expertise (e.g. Chemistry, Biology, etc.)

