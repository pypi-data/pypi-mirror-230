from redbot.message import headers
from redbot.syntax import rfc7234
from redbot.type import AddNoteMethodType


class expires(headers.HttpHeader):
    canonical_name = "Expires"
    description = """\
The `Expires` header gives a time after which the response is considered stale."""
    reference = f"{rfc7234.SPEC_URL}#header.expires"
    syntax = False  # rfc7234.Expires
    list_header = False
    deprecated = False
    valid_in_requests = False
    valid_in_responses = True

    def parse(self, field_value: str, add_note: AddNoteMethodType) -> int:
        return headers.parse_date(field_value, add_note)


class BasicExpiresTest(headers.HeaderTest):
    name = "Expires"
    inputs = [b"Mon, 04 Jul 2011 09:08:06 GMT"]
    expected_out = 1309770486


class BadExpiresTest(headers.HeaderTest):
    name = "Expires"
    inputs = [b"0"]
    expected_out = None
    expected_err = [headers.BAD_DATE_SYNTAX]


class BlankExpiresTest(headers.HeaderTest):
    name = "Expires"
    inputs = [b""]
    expected_out = None
    expected_err = [headers.BAD_DATE_SYNTAX]
