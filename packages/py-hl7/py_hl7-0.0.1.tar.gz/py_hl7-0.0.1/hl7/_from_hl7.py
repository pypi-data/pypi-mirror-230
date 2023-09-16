from ._constants import ENCODING_CHARACTERS, FIELD_SEPARATOR

_FIELD_SEPARATOR_FIELD = "<FIELD_SEPARATOR_FIELD>"
_ENCODING_CHARS_FIELD = "<ENCODING_CHARS_FIELD>"


def _prepare_hl7_message(hl7_content: str) -> str:
    encoding_chars = "".join(ENCODING_CHARACTERS)
    return hl7_content.replace(
        f"MSH|{encoding_chars}", f"MSH|{_FIELD_SEPARATOR_FIELD}|{_ENCODING_CHARS_FIELD}"
    )


def hl7_to_csv(hl7_content: str) -> str:
    csv_data = []
    encoding_chars = "".join(ENCODING_CHARACTERS)
    if f"MSH|{encoding_chars}" not in hl7_content:
        raise ValueError("Not a valid HL7 message")

    hl7_content = _prepare_hl7_message(hl7_content=hl7_content)

    for segment in hl7_content.split("\n"):
        fields = segment.split("|")
        segment_name = fields[0]
        for index, field in enumerate(fields[1:], start=1):
            if field:
                subfields = field.split("^")
                for sub_index, subfield in enumerate(subfields, start=1):
                    if subfield:
                        if "&" in subfield:
                            subsubfields = subfield.split("&")
                            for subsub_index, subsubfield in enumerate(
                                subsubfields, start=1
                            ):
                                csv_data.append(
                                    f"{segment_name};{index}.{sub_index}.{subsub_index};{subsubfield}"
                                )
                        else:
                            csv_data.append(
                                f"{segment_name};{index}.{sub_index};{subfield}"
                            )

    return (
        "\n".join(csv_data)
        .replace(_ENCODING_CHARS_FIELD, encoding_chars)
        .replace(_FIELD_SEPARATOR_FIELD, FIELD_SEPARATOR)
    )
