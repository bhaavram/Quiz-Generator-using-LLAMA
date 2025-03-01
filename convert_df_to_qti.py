import uuid
import xml.etree.ElementTree as ET

def convert_df_to_qti(df, attempts_allowed):
    """
    Convert the DataFrame (with columns: Type, Unused, Points, Question, CorrectAnswer,
    Option A, Option B, Option C, Option D, Option E) to a QTI XML file.
    The 'attempts_allowed' value is used to set the maximum attempts (cc_maxattempts).
    """
    # Register the QTI namespace
    ET.register_namespace("", "http://www.imsglobal.org/xsd/ims_qtiasiv1p2")

    # Create the root element
    root = ET.Element(
        'questestinterop',
        {
            "xmlns": "http://www.imsglobal.org/xsd/ims_qtiasiv1p2",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://www.imsglobal.org/xsd/ims_qtiasiv1p2 http://www.imsglobal.org/xsd/ims_qtiasiv1p2p1.xsd"
        }
    )

    # Create the Assessment element and include its metadata
    assessment_ident = "quiz_import_example"
    assessment = ET.SubElement(root, 'assessment', ident=assessment_ident, title="Quiz_Import_Example")

    # Add QTI metadata for maximum attempts using the user-provided value (default is 1)
    qtimetadata = ET.SubElement(assessment, 'qtimetadata')
    md_field = ET.SubElement(qtimetadata, 'qtimetadatafield')
    fieldlabel = ET.SubElement(md_field, 'fieldlabel')
    fieldlabel.text = "cc_maxattempts"
    fieldentry = ET.SubElement(md_field, 'fieldentry')
    fieldentry.text = str(attempts_allowed)

    # Create the root section
    section = ET.SubElement(assessment, 'section', ident="root_section")

    # Iterate over each row in the DataFrame to create items
    for index, row in df.iterrows():
        q_text = row["Question"]
        points = str(row["Points"])
        correct_answer = row["CorrectAnswer"]
        options = [row.get(col, "") for col in ["Option A", "Option B", "Option C", "Option D", "Option E"]]

        item_ident = "i" + uuid.uuid4().hex
        item = ET.SubElement(section, 'item', ident=item_ident, title=f"Question {index + 1}")

        # Item metadata
        itemmetadata = ET.SubElement(item, 'itemmetadata')
        qtimd = ET.SubElement(itemmetadata, 'qtimetadata')

        field1 = ET.SubElement(qtimd, 'qtimetadatafield')
        fl1 = ET.SubElement(field1, 'fieldlabel')
        fl1.text = "question_type"
        fe1 = ET.SubElement(field1, 'fieldentry')
        qtype = "multiple_choice_question" if row["Type"] == "MC" else "multiple_answers_question"
        fe1.text = qtype

        field2 = ET.SubElement(qtimd, 'qtimetadatafield')
        fl2 = ET.SubElement(field2, 'fieldlabel')
        fl2.text = "points_possible"
        fe2 = ET.SubElement(field2, 'fieldentry')
        fe2.text = points

        field3 = ET.SubElement(qtimd, 'qtimetadatafield')
        fl3 = ET.SubElement(field3, 'fieldlabel')
        fl3.text = "assessment_question_identifierref"
        fe3 = ET.SubElement(field3, 'fieldentry')
        fe3.text = "i" + uuid.uuid4().hex

        # Presentation: question text
        presentation = ET.SubElement(item, 'presentation')
        material = ET.SubElement(presentation, 'material')
        mattext = ET.SubElement(material, 'mattext', texttype="text/html")
        mattext.text = q_text

        rcardinality = "Single" if row["Type"] == "MC" else "Multiple"
        response_lid = ET.SubElement(presentation, 'response_lid', ident="response1")
        response_lid.set("rcardinality", rcardinality)
        render_choice = ET.SubElement(response_lid, 'render_choice')

        for j, opt_text in enumerate(options):
            option_id = f"{(index + 1) * 1000 + j}"
            resp_label = ET.SubElement(render_choice, 'response_label', ident=option_id)
            mat = ET.SubElement(resp_label, 'material')
            mattext_opt = ET.SubElement(mat, 'mattext', texttype="text/plain")
            mattext_opt.text = opt_text if opt_text is not None else ""

        resprocessing = ET.SubElement(item, 'resprocessing')
        outcomes = ET.SubElement(resprocessing, "outcomes")
        decvar = ET.SubElement(outcomes, "decvar", maxvalue="100", minvalue="0", varname="SCORE", vartype="Decimal")

        respcondition = ET.SubElement(resprocessing, 'respcondition', attrib={"continue": "No"})
        conditionvar = ET.SubElement(respcondition, 'conditionvar')
        try:
            correct_option_id = f"{(index + 1) * 1000 + int(correct_answer)}"
        except Exception:
            correct_option_id = f"{(index + 1) * 1000 + 1}"
        varequal = ET.SubElement(conditionvar, 'varequal', respident="response1")
        varequal.text = correct_option_id

        setvar = ET.SubElement(respcondition, "setvar", action="Set", varname="SCORE")
        setvar.text = "100"

    from io import BytesIO
    xml_buffer = BytesIO()
    tree = ET.ElementTree(root)
    tree.write(xml_buffer, encoding='ISO-8859-1', xml_declaration=True)
    xml_buffer.seek(0)
    return xml_buffer.getvalue()