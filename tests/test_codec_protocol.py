import unittest

from core.encode import (
    binaryToText,
    binaryToTrits,
    decode_message,
    encodeMessage,
    textToBinary,
    tritsToBinary,
)
from core.serial_protocol import format_trits_payload, parse_trits_line


class CodecProtocolTests(unittest.TestCase):
    def assert_roundtrip(self, message: str, key: str) -> None:
        encrypted = encodeMessage(message, key)
        binary = textToBinary(encrypted)
        trits = binaryToTrits(binary)
        recovered_binary = tritsToBinary(trits)
        recovered_encrypted = binaryToText(recovered_binary)
        recovered_message = decode_message(recovered_encrypted, key)

        self.assertEqual(recovered_binary, binary)
        self.assertEqual(recovered_message, message)

    def test_roundtrip_ascii(self):
        self.assert_roundtrip("TESTE", "ABC")

    def test_roundtrip_accented_text(self):
        self.assert_roundtrip("OLÁ ÇÃO", "SENHA")

    def test_binary_to_text_rejects_invalid_binary(self):
        with self.assertRaisesRegex(ValueError, "only 0 and 1"):
            binaryToText("01012")

    def test_binary_to_text_rejects_non_byte_length(self):
        with self.assertRaisesRegex(ValueError, "multiple of 8"):
            binaryToText("010")

    def test_trits_to_binary_rejects_invalid_values(self):
        with self.assertRaisesRegex(ValueError, "only -1, 0 and 1"):
            tritsToBinary([-1, 0, 1, 2, 0, -1])

    def test_trits_to_binary_rejects_non_block_length(self):
        with self.assertRaisesRegex(ValueError, "multiple of 6"):
            tritsToBinary([-1, 0, 1])

    def test_format_and_parse_trits_payload(self):
        trits = [-1, 0, 1, 1, 0, -1]

        payload = format_trits_payload(trits)

        self.assertEqual(payload, "-0++0-\n")
        self.assertEqual(parse_trits_line(payload), trits)

    def test_parse_rejects_invalid_trit_value(self):
        with self.assertRaisesRegex(ValueError, "invalid trit value"):
            parse_trits_line("-0+x0-")

    def test_parse_rejects_non_block_length(self):
        with self.assertRaisesRegex(ValueError, "multiple of 6"):
            parse_trits_line("-0+")


if __name__ == "__main__":
    unittest.main()
