import palimpzest as pz

class ScientificPaper(pz.PDFFile):
   """Represents a scientific research paper, which in practice is usually from a PDF file"""
   paper_title = pz.Field(desc="The title of the paper. This is a natural language title, not a number or letter.", required=True)
   paper_year = pz.Field(desc="The year the paper was published. This is a number.", required=False)
   paper_author = pz.Field(desc="The name of the first author of the paper", required=True)
   paper_journal = pz.Field(desc="The name of the journal the paper was published in", required=True)
   paper_subject = pz.Field(desc="A summary of the paper contribution in one sentence", required=False)
   paper_doiURL = pz.Field(desc="The DOI URL for the paper", required=True)

class Reference(pz.Schema):
    """ Represents a reference to another paper, which is cited in a scientific paper"""
    reference_index = pz.Field(desc="The index of the reference in the paper", required=True)
    reference_title = pz.Field(desc="The title of the paper being cited", required=True)
    reference_first_author = pz.Field(desc="The author of the paper being cited", required=True)
    reference_year = pz.Field(desc="The year in which the cited paper was published", required=True)
    # snippet = pz.Field(desc="A snippet from the source paper that references the index", required=False)

class CaseData(pz.Schema):
    """An individual row extracted from a table containing medical study data."""
    case_submitter_id = pz.Field(desc="The ID of the case", required=True)
    age_at_diagnosis = pz.Field(desc="The age of the patient at the time of diagnosis", required=False)
    race = pz.Field(desc="An arbitrary classification of a taxonomic group that is a division of a species.", required=False)
    ethnicity = pz.Field(desc="Whether an individual describes themselves as Hispanic or Latino or not.", required=False)
    gender = pz.Field(desc="Text designations that identify gender.", required=False)
    vital_status = pz.Field(desc="The vital status of the patient", required=False)
    ajcc_pathologic_t = pz.Field(desc="Code of pathological T (primary tumor) to define the size or contiguous extension of the primary tumor (T), using staging criteria from the American Joint Committee on Cancer (AJCC).", required=False)
    ajcc_pathologic_n = pz.Field(desc="The codes that represent the stage of cancer based on the nodes present (N stage) according to criteria based on multiple editions of the AJCC's Cancer Staging Manual.", required=False)
    ajcc_pathologic_stage = pz.Field(desc="The extent of a cancer, especially whether the disease has spread from the original site to other parts of the body based on AJCC staging criteria.", required=False)
    tumor_grade = pz.Field(desc="Numeric value to express the degree of abnormality of cancer cells, a measure of differentiation and aggressiveness.", required=False)
    tumor_focality = pz.Field(desc="The text term used to describe whether the patient's disease originated in a single location or multiple locations.", required=False)
    tumor_largest_dimension_diameter = pz.Field(desc="The tumor largest dimension diameter.", required=False)
    primary_diagnosis = pz.Field(desc="Text term used to describe the patient's histologic diagnosis, as described by the World Health Organization's (WHO) International Classification of Diseases for Oncology (ICD-O).", required=False)
    morphology = pz.Field(desc="The Morphological code of the tumor, as described by the World Health Organization's (WHO) International Classification of Diseases for Oncology (ICD-O).", required=False)
    tissue_or_organ_of_origin = pz.Field(desc="The text term used to describe the anatomic site of origin, of the patient's malignant disease, as described by the World Health Organization's (WHO) International Classification of Diseases for Oncology (ICD-O).", required=False)
    # tumor_code = pz.Field(desc="The tumor code", required=False)
    study = pz.Field(desc="The last name of the author of the study, from the table name", required=False)
