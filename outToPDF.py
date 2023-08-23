import pdfrw
import boto3
import tempfile
s3 = boto3.client('s3')

# Takes in an input path to a PDF file, an output path for the resulting PDF, and a dictionary of field names and values. Its main purpose is to fill the given PDF with the provided data and save the resulting file to the specified output path.
def write_fillable_pdf(input_pdf_path, output_pdf_path, data):
    """Writes a fillable PDF file with the given data."""
    
    # Reads the PDF file from the provided input path
    template_pdf = pdfrw.PdfReader(input_pdf_path)

    # Check if the 'AcroForm' key exists in the root of the PDF
    # AcroForm represents a collection of fields for gathering information interactively from the user
    if "/AcroForm" in template_pdf.Root.keys():
        # If so, update the 'NeedAppearances' flag to 'true' which indicates that the viewer needs to generate appearances for form fields
        template_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))

    # Iterate over each page in the PDF
    for page in template_pdf.pages:
        # Get the annotations for the page. Annotations can be things like text boxes, checkboxes, etc.
        annotations = page['/Annots']

        if annotations is not None:
            # If annotations exist on the page, iterate over each one
            for annotation in annotations:
                # Check if the annotation subtype is 'Widget' which represents form fields
                if annotation['/Subtype'] == '/Widget':
                    if annotation['/T']:
                        # Extract the field name from the annotation
                        field_name = annotation['/T'][1:-1]  # Remove leading and trailing parentheses

                        # If the field name exists in the provided data
                        if field_name in data:
                            # Set the value of the field with the corresponding value from the data
                            annotation.update(pdfrw.PdfDict(V=data[field_name]))

                            # Check if the field has a flag ("/Ff") and ensure it's not hidden
                            if "/Ff" in annotation:
                                try:
                                    # Get the value of the "/Ff" flag and unset the hidden bit (0x200000)
                                    ff_value = int(str(annotation["/Ff"]))
                                    annotation.update(pdfrw.PdfDict(Ff=ff_value & ~0x200000))
                                except ValueError:
                                    continue

    # Write the modified PDF to the specified output path
    pdfrw.PdfWriter().write(output_pdf_path, template_pdf)

# Handles the user's uploaded PDF files from an S3 bucket (a cloud storage service by AWS)
# It downloads the file from S3, stores it temporarily, and then processes it to extract field names and their values
def inputSEP(input_pdf_s3_key):
    # create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_pdf:
        # download the file from S3 to the temporary file
        s3.download_file('ccc-sep-pdf', input_pdf_s3_key, temp_pdf.name)
        # then process the local file as before
        return process_pdf(temp_pdf.name)

def process_pdf(input_pdf_path):
    # List of expected field names in the PDF
    field_names = ['1', '1_2', '2', '2_2', '3', '3_2', '4', '4_2', '5', '5_2', '6', '6_2', '7', '7_2', '1_3', '1_4', '2_3', '2_4', '3_3', '3_4', '4_3', '4_4', '5_3', '5_4', '6_3', '6_4', '7_3', '7_4', '1_5', '1_6', '2_5', '2_6', '3_5', '3_6', '4_5', '4_6', '5_5', '5_6', '6_5', '6_6', '7_5', '7_6','1_7', '1_8', '2_7', '2_8', '3_7', '3_8', '4_7', '4_8', '5_7', '5_8', '6_7', '6_8', '7_7', '7_8',  '1_9', '1_10', '2_9', '2_10', '3_9', '3_10', '4_9', '4_10', '5_9', '5_10', '6_9', '6_10', '7_9', '7_10', '1_11', '1_12', '2_11', '2_12', '3_11', '3_12', '4_11', '4_12', '5_11', '5_12', '6_11', '6_12', '7_11', '7_12', '1_13', '1_14', '2_13', '2_14', '3_13', '3_14', '4_13', '4_14', '5_13', '5_14', '6_13', '6_14', '7_13', '7_14', '1_15', '1_16', '2_15', '2_16', '3_15', '3_16', '4_15', '4_16', '5_15', '5_16', '6_15', '6_16', '7_15', '7_16', '1_17', '1_18', '2_17', '2_18', '3_17', '3_18', '4_17', '4_18', '5_17', '5_18', '6_17', '6_18', '7_17', '7_18']

    # List to store the extracted key-value pairs
    key_and_val = []
    
    # Read the PDF from the provided path
    pdf = pdfrw.PdfReader(input_pdf_path)
    
    # Iterate over each page in the PDF
    for page in pdf.pages:
        # Get the annotations for the page
        annotations = page['/Annots']
        
        if annotations is not None:
            # If annotations exist on the page, iterate over each one
            for annotation in annotations:
                # Check if the annotation subtype is 'Widget'
                if annotation['/Subtype'] == '/Widget':
                    if annotation['/T']:
                        # Extract the field name from the annotation
                        field_name = annotation['/T'][1:-1]  # Remove leading and trailing parentheses
                        
                        # If the field name exists in the predefined list of field names
                        if field_name in field_names:
                            # Extract the value of the field
                            value = annotation['/V']
                            if value is not None:  # Check if value is not None before performing subscript operation
                                key = field_name
                                val = value[1:-1]  # Remove leading and trailing parentheses
                                key_and_val.append((key,val))
    
    # Return the extracted key-value pairs
    return key_and_val 

# FUNCTION I used to find the field names: 
# def output_pdf_fields(pdf_path):
#     pdf = PdfReader(pdf_path)

#     fields = {}

#     for page in pdf.pages:
#         annotations = page['/Annots']
#         if annotations is None:
#             continue
#         for annotation in annotations:
#             if annotation['/Subtype'] == '/Widget':
#                 if '/T' in annotation:
#                     field_key = annotation['/T'][1:-1]
#                     fields[field_key] = annotation['/V']
#     return fields

# pdf_path = "SEP.pdf"

# print(output_pdf_fields(pdf_path))

# # make_fields_viewable(pdf_path, "SEP_new.pdf")


