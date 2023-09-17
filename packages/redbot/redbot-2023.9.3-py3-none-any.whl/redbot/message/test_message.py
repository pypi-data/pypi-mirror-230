# coding=UTF-8

import unittest

from functools import partial
from typing import List, Type, Dict

from redbot.message import headers
from redbot.speak import Note
from redbot.syntax import rfc7230
from redbot.message import DummyMsg


class GeneralHeaderTesters(unittest.TestCase):
    def test_unquote_string(self) -> None:
        i = 0
        for instr, expected_str, _ in [
            ("foo", "foo", []),
            ('"foo"', "foo", []),
            (r'"fo\"o"', 'fo"o', []),
            (r'"f\"o\"o"', 'f"o"o', []),
            (r'"fo\\o"', r"fo\o", []),
            (r'"f\\o\\o"', r"f\o\o", []),
            (r'"fo\o"', "foo", []),
        ]:
            out_str = headers.unquote_string(str(instr))
            self.assertEqual(
                expected_str,
                out_str,
                f"[{i}] {str(expected_str)} != {str(out_str)}",
            )
            i += 1

    def test_split_string(self) -> None:
        i = 0
        for instr, expected_outlist, item, split in [
            ('"abc", "def"', ['"abc"', '"def"'], rfc7230.quoted_string, r"\s*,\s*"),
            (
                r'"\"ab", "c\d"',
                [r'"\"ab"', r'"c\d"'],
                rfc7230.quoted_string,
                r"\s*,\s*",
            ),
        ]:
            outlist = headers.split_string(str(instr), item, split)
            self.assertEqual(
                expected_outlist,
                outlist,
                f"[{i}] {str(expected_outlist)} != {str(outlist)}",
            )
            i += 1

    def test_parse_params(self) -> None:
        i = 0
        expected_pd: Dict[str, str]
        expected_notes: List[Type[Note]]
        for instr, expected_pd, expected_notes, delim in [  # type: ignore
            ("foo=bar", {"foo": "bar"}, [], ";"),
            ('foo="bar"', {"foo": "bar"}, [], ";"),
            ('foo="bar"; baz=bat', {"foo": "bar", "baz": "bat"}, [], ";"),
            (
                'foo="bar"; baz="b=t"; bam="boom"',
                {"foo": "bar", "baz": "b=t", "bam": "boom"},
                [],
                ";",
            ),
            (r'foo="b\"ar"', {"foo": 'b"ar'}, [], ";"),
            (r"foo=bar; foo=baz", {"foo": "baz"}, [headers.PARAM_REPEATS], ";"),
            ('foo=bar; baz="b;at"', {"foo": "bar", "baz": "b;at"}, [], ";"),
            ('foo=bar, baz="bat"', {"foo": "bar", "baz": "bat"}, [], ","),
            ('foo=bar, baz="b,at"', {"foo": "bar", "baz": "b,at"}, [], ","),
            (
                "foo=bar; baz='bat'",
                {"foo": "bar", "baz": "'bat'"},
                [headers.PARAM_SINGLE_QUOTED],
                ";",
            ),
            (
                "foo*=\"UTF-8''a%cc%88.txt\"",
                {"foo*": "a\u0308.txt"},
                [headers.PARAM_STAR_QUOTED],
                ";",
            ),
            ("foo*=''a%cc%88.txt", {}, [headers.PARAM_STAR_NOCHARSET], ";"),
            ("foo*=utf-16''a%cc%88.txt", {}, [headers.PARAM_STAR_CHARSET], ";"),
            ("nostar*=utf-8''a%cc%88.txt", {}, [headers.PARAM_STAR_BAD], ";"),
            ("NOstar*=utf-8''a%cc%88.txt", {}, [headers.PARAM_STAR_BAD], ";"),
        ]:
            msg = DummyMsg()
            param_dict = headers.parse_params(
                instr, partial(msg.add_note, "test"), ["nostar"], delim
            )
            diff = {n.__name__ for n in expected_notes}.symmetric_difference(
                set(msg.note_classes)
            )
            self.assertEqual(len(diff), 0, f"[{i}] Mismatched notes: {diff}")
            self.assertEqual(
                expected_pd,
                param_dict,
                f"[{i}] {str(expected_pd)} != {str(param_dict)}",
            )
            i += 1
