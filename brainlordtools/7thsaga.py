__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import csv
import os
import pathlib
import shutil
import sqlite3
import struct
from pprint import pprint

from rhutils.db import insert_text, select_most_recent_translation
from rhutils.dump import extract_binary, get_csv_translated_texts, insert_binary
from rhutils.io import read_text, write_byte, write_text
from rhutils.snes import decode_snes_addr, encode_snes_addr
from rhutils.table import Table

TEXT_SEGMENT_1 = (0x60000, 0x6fddf)
TEXT_SEGMENT_X = (0x6fde0, 0x6ffff) # empty
TEXT_SEGMENT_2 = (0x70000, 0x733c0)
TEXT_SEGMENT_3 = (0x741f7, 0x75342)

MISC_SEGMENT_1 = (0x733c2, 0x741f6)
MISC_SEGMENT_2 = (0x75345, 0x7545f)

POINTER_BLOCKS = ((0x1a0ad, 0x1a0c1), (0x425db, 0x4269a))

FONT1_BLOCK = (0x13722d, 0x13B22d)
FONT2_BLOCK = (0x1d0800, 0x1d1800)

special_pointers = (0xc21e, 0xc22f, 0xc14d, 0xc1c1, 0xc26d, 0xc2c4, 0xc295, 0xc2a6, 0xc2fd, 0xc2ec, 0xc31b, 0xc343, 0xc354, 0xc37d, 0xc431, 0xc9a8, 0xca0b, 0xca19, 0xcaa3, 0xcab4, 0xcb54, 0xcb70, 0xcd12)

sparse_pointers = (
    0x56f0a, 0x56f10, 0x56f16, 0x56f1c, 0x56f22, 0x56f28, 0x56f88, 0x56f8e, 0x56f94, 0x56f9a,
    0x56fa0, 0x56fa6, 0x56fac, 0x56fb2, 0x56fb8, 0x57012, 0x57018, 0x5701e, 0x57024, 0x5702a,
    0x57090, 0x57096, 0x5709c, 0x570a2, 0x570a8, 0x57114, 0x5711a, 0x57120, 0x57126, 0x5712c,
    0x57132, 0x57138, 0x5713e, 0x57144, 0x57192, 0x57198, 0x57204, 0x5720a, 0x57210, 0x57216,
    0x5721c, 0x57222, 0x57228, 0x57288, 0x5728e, 0x5729a, 0x572dc, 0x572e2, 0x572e8, 0x572ee,
    0x572f4, 0x5731e, 0x57324, 0x5732a, 0x57330, 0x57336, 0x5733c, 0x5737e, 0x57384, 0x5738a,
    0x57390, 0x57396, 0x5739c, 0x573e4, 0x573ea, 0x573f0, 0x573f6, 0x573fc, 0x57402, 0x5745c,
    0x57462, 0x57468, 0x5746e, 0x57474, 0x5747a, 0x57480, 0x57486, 0x5748c, 0x5750a, 0x57510,
    0x57516, 0x57b94, 0x57b9a, 0x57ba0, 0x57ba6, 0x57bfa, 0x159d37, 0x15a511, 0x15a541, 0x15a547,
    0x15a54d, 0x15a559, 0x15a55f, 0x15a60d, 0x15a61f, 0x15a625, 0x15a62b, 0x15aebf, 0x15aec5, 0x15aecb,
    0x15aef5, 0x15b123, 0x15b1b9, 0x158fd5, 0x158fe7, 0x158fff, 0x15901d, 0x159035, 0x15903b, 0x15905f,
    0x159065, 0x15906b, 0x1590bf, 0x1590c5, 0x1590d7, 0x1590f5, 0x159131, 0x15914f, 0x159185, 0x15918b,
    0x15919d, 0x1591af, 0x1591c1, 0x1591d3, 0x1591d9, 0x1591eb, 0x1591f1, 0x15920f, 0x159215, 0x15921b,
    0x15924b, 0x159251, 0x159281, 0x159287, 0x15928d, 0x15929f, 0x1592a5, 0x1592b7, 0x1592bd, 0x1592c3,
    0x1592c9, 0x1592cf, 0x1592e1, 0x1592e7, 0x1592ed, 0x1592f3, 0x1592f9, 0x1592ff, 0x159347, 0x15934d,
    0x15936b, 0x159371, 0x159395, 0x1593cb, 0x1593e9, 0x1593ef, 0x15940d, 0x159413, 0x159419, 0x15941f,
    0x15943d, 0x159455, 0x159485, 0x159497, 0x15949d, 0x1594b5, 0x1594d9, 0x1594eb, 0x1594fd, 0x159515,
    0x15954b, 0x15957b, 0x15958d, 0x15959f, 0x1595b1, 0x1595c3, 0x1595d5, 0x159629, 0x15964d, 0x159653,
    0x159665, 0x15966b, 0x159671, 0x159683, 0x159695, 0x1596a7, 0x1596bf, 0x1596dd, 0x1596fb, 0x159701,
    0x159737, 0x1597fd, 0x159a13, 0x159bbd, 0x159deb, 0x15a151, 0x15a2ad, 0x15a59b, 0x15a89b, 0x15a9e5,
    0x15aa15, 0x15aa51, 0x15aa6f, 0x15ab8f, 0x15ac0d, 0x15af1f, 0x15af61, 0x15b057, 0x15b11d, 0x15b25b,
    0x15b453, 0x15baa7, 0x15bafb, 0x15bc21, 0x15d0f1, 0x15c035, 0x15989f, 0x1598b7, 0x1598d5, 0x1598e7,
    0x159911, 0x159917, 0x15991d, 0x159935, 0x159995, 0x1599a7, 0x1599b9, 0x1599cb, 0x1599dd, 0x159a0d,
    0x159c05, 0x159c0b, 0x159c11, 0x159c17, 0x159c1d, 0x159c8f, 0x159c95, 0x159d07, 0x159ea5, 0x159eab,
    0x159eb1, 0x159eb7, 0x159ebd, 0x159ec3, 0x15b0ff, 0x15b105, 0x15b16b, 0x15b1cb, 0x15bd05, 0x15bd1d,
    0x15bd35, 0x15bf2d, 0x15bf3f, 0x15a7db, 0x15a81d, 0x15a8c5, 0x15abd7, 0x15aceb, 0x15acf1, 0x15ad09,
    0x15ad0f, 0x15ad15, 0x15ad1b, 0x15ad39, 0x15d57d, 0x15d697, 0x15d69d, 0x15d967, 0x15d96d, 0xf349a,
    0x5774a, 0x5783a, 0x57ad4, 0x57978, 0x15b0c3, 0x15a7ff, 0x15b0ed, 0x15b0bd, 0x15b0e7, 0x15b2cd,
    0x15b351, 0x15b3f3, 0x15b3f9, 0x15bcc3, 0x15c281, 0x15d061, 0x15e5a3, 0x15e681, 0x15e687, 0x159017,
    0x159233, 0x159329, 0x15946d, 0x159611, 0x15975b, 0x159965, 0x159a6d, 0x159ba5, 0x159e39, 0x15a187,
    0x15a21d, 0x15a87d, 0x15abc5, 0x15abef, 0x159149, 0x159269, 0x159389, 0x1593b3, 0x1595f3, 0x15973d,
    0x15976d, 0x15978b, 0x1597a9, 0x1597bb, 0x1597cd, 0x1597d3, 0x15987b, 0x159a4f, 0x159aa9, 0x159ac7,
    0x159adf, 0x159af7, 0x159e21, 0x15a19f, 0x159167, 0x15926f, 0x15938f, 0x15952d, 0x1595f9, 0x159791,
    0x159881, 0x1599f5, 0x5751c, 0x57522, 0x57528, 0x5757c, 0x57582, 0x577c2, 0x577c8, 0x575d6,
    0x575dc, 0x575e2, 0x575e8, 0x575ee, 0x57690, 0x57696, 0x5769c, 0x576a2, 0x576a8, 0x5772c,
    0x57732, 0x57738, 0x5773e, 0x57744, 0x57750, 0x5779e, 0x577a4, 0x577aa, 0x577b0, 0x577b6,
    0x577bc, 0x57840, 0x57846, 0x5784c, 0x57852, 0x57858, 0x5785e, 0x578ca, 0x578d0, 0x578d6,
    0x578dc, 0x578e2, 0x578e8, 0x57972, 0x5797e, 0x57984, 0x5798a, 0x57990, 0x57a20, 0x57a26,
    0x57a2c, 0x57a32, 0x57a38, 0x57a3e, 0x57a44, 0x57a4a, 0x57ada, 0x57ae0, 0x57ae6, 0x57b10,
    0x57b16, 0x57b1c, 0x57b22, 0x57c00, 0x57c06, 0x57c0c, 0x57c12, 0x57c18, 0x57c90, 0x57c96,
    0x57c9c, 0x57ca2, 0x57ca8, 0x57cae, 0x57cb4, 0x57d1a, 0x57d20, 0x57d26, 0x57d2c, 0x57d32,
    0x57d62, 0x57d68, 0x57d6e, 0x57dc8, 0x57dce, 0x57dd4, 0x57dda, 0x57de0, 0x57de6, 0x57dec,
    0x57df2, 0x57df8, 0x57e94, 0x57e9a, 0x57ea0, 0x57ea6, 0x5710e, 0x5718c, 0x573cc, 0x573d2,
    0x573de, 0x575f4, 0x575fa, 0x57600, 0x57606, 0x5760c, 0x57612, 0x57618, 0x57834, 0x57b88,
    0x57b8e, 0x57a14, 0x57bf4, 0x8740, 0x8743, 0x8746, 0x8749, 0x877c, 0x877f, 0x8782,
    0x8785, 0x8788, 0x878b, 0x87b8, 0x87bb, 0x87be, 0x87c1, 0x87c4, 0x87c7, 0x87f4,
    0x87f7, 0x87fa, 0x87fd, 0x8800, 0x8803, 0x8830, 0x8833, 0x8836, 0x8839, 0x883c,
    0x883f, 0x886c, 0x886f, 0x8872, 0x8875, 0x8878, 0x887b, 0x88a8, 0x88ab, 0x88ae,
    0x88b1, 0x88b4, 0x88b7, 0x1a0e5c, 0x1a6e1, 0x1a6e4, 0x1a6e7, 0x1a6ea, 0x1a6ed, 0x1a6f0,
    0x1a6f3, 0x1a6f6, 0x1a9645, 0x1348ce, 0x1404c, 0x143d4, 0x13f6a3, 0x134a07, 0x135a4e, 0x142f1b,
    0x14304a, 0x1546e4, 0x11af5a, 0x12afef, 0x8c22b, 0x87d83, 0x798e0, 0x345bd, 0xc6d10, 0xcc1b4,
    0xdc7fa, 0xdc9c6, 0x1883c3, 0x1c93ab, 0x1cea80, 0x1d0f66, 0x1d1026, 0x1d10e6, 0x1d1166, 0x1d0c0a,
    0x1d0c22, 0x1d0c28, 0x1d0ce8, 0x1d0de2, 0x1d0f86, 0x1d1106, 0x1d6623, 0x1dc2a4, 0x15ae35, 0x15af97,
    0x15b08d, 0x15b13b, 0x15b201, 0x15b4a1, 0x15bb7f, 0x15bbfd, 0x15d1e1, 0x15a235, 0x15a529, 0x15a871,
    0x15aba7, 0x15ac8b, 0x15ae4d, 0x15af79, 0x15b06f, 0x15b153, 0x15b243, 0x15b4bf, 0x15bb61, 0x15bc6f,
    0x15d151, 0x159b0f, 0x159d9d, 0x15a0bb, 0x15a24d, 0x15a4f3, 0x15a877, 0x15aab7, 0x15aca3, 0x15ae65,
    0x15af7f, 0x15b075, 0x15b159, 0x15b22b, 0x15b2f7, 0x15bb67, 0x15bc93, 0x15d14b, 0x1597f7, 0x159839,
    0x159a37, 0x159bdb, 0x159e09, 0x15a16f, 0x15a26b, 0x15a4c3, 0x15a84d, 0x15ab23, 0x15ac2b, 0x15ae05,
    0x15af49, 0x15b03f, 0x15b189, 0x15b1e9, 0x15b315, 0x15baad, 0x15bb19, 0x15bc4b, 0x15d1b1, 0x159a91,
    0x159b27, 0x159b75, 0x159b8d, 0x159b5d, 0x159b3f, 0x159b45, 0x159a7f, 0x159ccb, 0x159cd1, 0x159bf9,
    0x159bff, 0x159d3d, 0x159d85, 0x159dcd, 0x159dc7, 0x159db5, 0x159d73, 0x159f77, 0x159e5d, 0x159ec9,
    0x159e51, 0x159ff5, 0x159e57, 0x159e93, 0x159f71, 0x15a067, 0x159ffb, 0x15a001, 0x159fe3, 0x15a109,
    0x15a1bd, 0x15a1b7, 0x15a1b1, 0x15a0cd, 0x15a0df, 0x15a0f1, 0x15a1e1, 0x15a283, 0x15a289, 0x15a28f,
    0x15a1f3, 0x15a2c5, 0x159f7d, 0x15a439, 0x15a451, 0x159f83, 0x159fe9, 0x159fef, 0x15a43f, 0x15a445,
    0x15a44b, 0x15a457, 0x15a45d, 0x15a463, 0x15a469, 0x15a46f, 0x15a79f, 0x15a295, 0x15a2bf, 0x15a40f,
    0x15a2cb, 0x15a313, 0x15a3e5, 0x15a361, 0x15a319, 0x15a205, 0x15a31f, 0x15a391, 0x159e9f, 0x159e99,
    0x15a397, 0x15a7e7, 0x15a1cf, 0x15a853, 0x15a82f, 0x15a7f9, 0x15a811, 0x15a817, 0x15a7e1, 0x15dd57,
    0x15dbf5, 0x15dc5b, 0x15dd87, 0x15dd8d, 0x15dd9f, 0x15dd93, 0x15dd99, 0x15ddb1, 0x15ddab, 0x15dda5,
    0x15a481, 0x15a493, 0x15a4a5, 0x15a4db, 0x15a553, 0x15a637, 0x15a631, 0x15a7a5, 0x15a619, 0x15a613,
    0x15a8b9, 0x15a8bf, 0x15a98b, 0x15a919, 0x15aa9f, 0x15a92b, 0x15aa8d, 0x15a9f7, 0x15a91f, 0x15a925,
    0x15e4e3, 0x15e4dd, 0x15ab35, 0x15ab3b, 0x15aac9, 0x15ab5f, 0x15aaff, 0x15aaed, 0x15ab59, 0x15acb5,
    0x15acc7, 0x15adc3, 0x15ac43, 0x15ac5b, 0x15ac73, 0x15ad63, 0x15ad69, 0x15ad75, 0x15ae89, 0x15ae1d,
    0x15ae9b, 0x15ade1, 0x15ae77, 0x15addb, 0x15aeb9, 0x15aeb3, 0x15e96f, 0x15e9b7, 0x15afeb, 0x15afcd,
    0x15afbb, 0x15afa9, 0x15affd, 0x15b09f, 0x15b015, 0x15b00f, 0x15e891, 0x15e897, 0x15e9ff, 0x15ec6f,
    0x15b2a3, 0x15b27f, 0x15b2b5, 0x15b2bb, 0x15b2c1, 0x15b2c7, 0x15b291, 0x15b26d, 0x15b213, 0x15b327,
    0x15b471, 0x15b4b9, 0x15b2df, 0x15b3ed, 0x15b34b, 0x15b3c3, 0x15b483, 0x15b489, 0x15b4d1, 0x15b813,
    0x15b837, 0x15b8a3, 0x15b8cd, 0x15b8d3, 0x15b9a5, 0x15ba7d, 0x15ba83, 0x15ba89, 0x15c095, 0x15c0bf,
    0x15c0c5, 0x15c173, 0x15c227, 0x15c275, 0x15c27b, 0x15bed3, 0x15bf33, 0x15bcdb, 0x15bd4d, 0x15bd89,
    0x15bd8f, 0x15bd95, 0x15bd9b, 0x15bda1, 0x15bda7, 0x15bdad, 0x15becd, 0x15bf27, 0x15bf9f, 0x15bfb7,
    0x15bfbd, 0x15bfc3, 0x15bfa5, 0x15bfc9, 0x15bfb1, 0x15bfab, 0x15c03b, 0x15bf39, 0x15bf45, 0x15bb91,
    0x15bba3, 0x15bbb5, 0x15d26b, 0x15d277, 0x15d223, 0x15d271, 0x15d025, 0x15d17b, 0x15d091, 0x15d11b,
    0x15d265, 0x15babf, 0x15bad1, 0x15bad7, 0x15bae3, 0x15badd, 0x15bac5, 0x15bacb, 0x15ee67, 0x15ee6d,
    0x15ee73, 0x15ee79, 0x15ee55, 0x15eeb5, 0x15eec1, 0x15efc9, 0x15f119, 0x15f251, 0x15a0a3, 0x15a6df,
    0x15a6e5, 0x15a6eb, 0x15a6f1, 0x15d3d3, 0x15d40f, 0x15d457, 0x15d403, 0x15d44b, 0x15d61f, 0x15d757,
    0x15d793, 0x15d6f1, 0x15f72a, 0x158fc3, 0x15f73c, 0x15f730, 0x15f736, 0x15f50f, 0x159719, 0x15da7b,
    0x15debf, 0x15d763, 0x15ac31, 0x15a367, 0x159407, 0x15d883, 0x15dd63, 0x15e4d7, 0x15dca3, 0x15d5d7,
    0x15d625, 0x15e561, 0x15ab1d, 0x159323, 0x15947f, 0x1596b9, 0x159815, 0x159f6b, 0x15a7d5, 0x15ac6d,
    0x15b033, 0x15b039, 0x15bb49, 0x15d05b,
)

def _get_misc_2byte_pointer_map(f, pointer_map):
    # Two-byte hardcoded pointers with bank byte \xc7 (file base 0x70000)
    two_byte_c7 = [
        0xcc2, 0xce0, 0xcfe, 0x245c, 0x2490, 0x24c5, 0x2fc5, 0x324c, 0x3351, 0x3456,
        0x34cf, 0x3547, 0x35bf, 0x9df3, 0x1e546, 0x1ead1, 0x1eaa5, 0x18b62, 0x18b7b, 0x18cab,
        0x18cc3, 0x18d01, 0x18d19, 0x18d57, 0x18d6f, 0x18dc5, 0x18e1b, 0x18e71, 0x18ec7, 0x18f45,
        0x190d3, 0x190ed, 0x19733, 0x1975b, 0x19783, 0x197ab, 0x197d3, 0x1e3ba, 0x1e3e6, 0x1e51a,
        0x1e99d, 0x1e9c9, 0x1e9f5, 0x1ea21, 0x1ea4d, 0x1ea79, 0x217c0, 0x217f1, 0x41788, 0x440ff,
        0x45b06, 0x45fc9, 0x4719b, 0x47950, 0x47b1e, 0x485ac, 0x48657, 0x48739, 0x48676, 0x48758,
        0x487e0, 0x487c1, 0x48971, 0x48982, 0x18dad, 0x19b36, 0x1e412, 0x18e03, 0x19b62, 0x1e43e,
        0x18e59, 0x19b8e, 0x1e46a, 0x18eaf, 0x19bba, 0x1e496, 0x19be6, 0x1e4c2, 0x19c12, 0x1e4ee,
        0x477c3, 0x49025, 0x47911, 0x49392, 0x4a848, 0x4c371, 0x489d1, 0x489f3, 0x48a64, 0x48ad5,
        0x48b46, 0x48bb2, 0x48c1e, 0x48a42, 0x48ab3, 0x48b24, 0x48b90, 0x48bfc, 0x49353, 0x49639,
        0x49e76, 0x49e95, 0x49ef2, 0x49f11, 0x49f7e, 0x4a01c, 0x4a02d, 0x4a07c, 0x4a09e, 0x4a0ed,
        0x4a10f, 0x4a15e, 0x4a180, 0x4a1cf, 0x4a1f1, 0x4a23b, 0x4a25d, 0x4a2a7, 0x4a2c9, 0x4a88d,
        0x4a8d2, 0x4a952, 0x4ae93, 0x4b4e8, 0x4b517, 0x485eb, 0x488fe, 0x49fb1, 0x4cadf, 0x48dc7,
        0x493d1, 0x5e0c8, 0x4b53c, 0x4b56c, 0x4b585, 0x4b5af, 0x4b613, 0x4b643, 0x4b65c, 0x4b686,
        0x4b6ab, 0x4b6da, 0x4b899, 0x4b8c4, 0x4b90a, 0x4b937, 0x4b950, 0x4b97a, 0x4b9ab, 0x4b9e9,
        0x4ba3c, 0x4ba6b, 0x4ba84, 0x4baae, 0x4bbfc, 0x4bc1a, 0x4bc8d, 0x4bfb2, 0x4c283, 0x4c3b6,
        0x4c3fb, 0x4c4b2, 0x4c874, 0x4c893, 0x4c925, 0x4c944, 0x4c9be, 0x4c9cf, 0x4ca3e, 0x4ca5c,
        0x4cac6, 0x4cb36, 0x4cbe4, 0x4d5bf, 0x4d654, 0x4d6d8, 0x4d707, 0x4d72c, 0x4d75c, 0x4d775,
        0x4d79f, 0x4d7f3, 0x4d823, 0x4d83c, 0x4d866, 0x4d88b, 0x4d8ba, 0x4da38, 0x4da60, 0x4da96,
        0x4dac3, 0x4dadc, 0x4db06, 0x4db3c, 0x4db6b, 0x4db84, 0x4dbae, 0x4dce6, 0x4dd0d, 0x4dd60,
        0x4de01, 0x4de28, 0x5e0a1, 0x5e0b6, 0x5e3a3,
    ]
    for p_offset in two_byte_c7:
        f.seek(p_offset)
        raw = f.read(2)
        if len(raw) == 2:
            p_value = struct.unpack('i', raw + b'\xc7' + b'\x00')[0] - 0xc00000
            pointer_map.setdefault(p_value, []).append(p_offset)
    return pointer_map

def _get_misc_3byte_pointer_map(f, pointer_map):
    # Misc pointer tables (step-based, first 3 bytes of each entry are the pointer)
    misc_pointer_tables = [
        (0x302a,   2,  3), # Yes, No
        (0x262d,   7,  3), # begin...
        (0x63a2,  51, 10), # [SWORD] Tranq...
        (0x65a7,  53, 17), # [ARMOR] Xtri...
        (0x6c9a,  99,  9), # Exigate, Watr Rn, Potn [1], MHerb [1]...
        (0x7015,  61, 12), # FIRE [1]
        (0x72f1,  99, 42), # Monsters... Guanta...
        (0x8320,  38, 27), # Lemele...
        (0x999b,   3,  3), # Cure
        (0xac6b,   3,  3), # buy...
        (0x45f1c,  7,  3), # Town menu
        (0x45f46,  7,  3), # Map menu
        (0x45f70,  7,  3), # Battle menu
        (0x48fbb,  2,  3), # Use...
        (0x4f329,  6,  3), # Use...
        (0x4fbe0,  5,  3), # Use...
        (0x4eeb9,  11, 3), # party
        (0x1e76d,  7,  3), # Human...
    ]
    for table_start, count, step in misc_pointer_tables:
        table_end = table_start + count * step
        f.seek(table_start)
        while f.tell() < table_end:
            p_offset = f.tell()
            raw = f.read(step)
            if len(raw) >= 3:
                p_value = struct.unpack('i', raw[:3] + b'\x00')[0] - 0xc00000
                pointer_map.setdefault(p_value, []).append(p_offset)
    return pointer_map

def _get_text_pointer_block_pointer_map(f, pointer_map):
    # POINTER_BLOCKS (sequential 3-byte pointer tables)
    for block_start, block_end in POINTER_BLOCKS:
        f.seek(block_start)
        while f.tell() < block_end:
            p_offset = f.tell()
            raw = f.read(3)
            if len(raw) == 3:
                p_value = struct.unpack('i', raw + b'\x00')[0] - 0xc00000
                pointer_map.setdefault(p_value, []).append(p_offset)
    return pointer_map

def _get_text_sparse_pointer_map(f, pointer_map):
    # sparse_pointers (3-byte)
    for p_offset in sparse_pointers:
        f.seek(p_offset)
        raw = f.read(3)
        if len(raw) == 3:
            p_value = struct.unpack('i', raw + b'\x00')[0] - 0xc00000
            pointer_map.setdefault(p_value, []).append(p_offset)
    return pointer_map

def _get_text_2byte_pointer_map(f, pointer_map):
    # Two-byte hardcoded pointers with bank byte \xc6 (file base 0x60000)
    two_byte_c6 = [
        0x668, 0x7d8, 0x8d3, 0xa39, 0xb34, 0x1d412, 0x2bd2d, 0x2be96, 0x2c1f5, 0x2d6fb,
        0x2d7b5, 0x2f3da, 0x8eb2, 0xa0b7, 0xaafb, 0x8f9b, 0xa1a0, 0xac1c, 0x900d, 0xa212,
        0x9134, 0xa339, 0xb1d1, 0x94bc, 0x953d, 0xa732, 0x95ef, 0xa7cf, 0x960f, 0xa7ef,
        0x971f, 0xa8d5, 0x9800, 0xa995, 0x9870, 0xaa05, 0xb4db, 0x98cf, 0xaa64, 0x9962,
        0x9a44, 0x9b99, 0x9e7d, 0x9e2b, 0xa069, 0xacee, 0xad25, 0xb097, 0xb42a, 0xb0c2,
        0xb4a5, 0xa9cf, 0xb5a5, 0xb604, 0xb6c6, 0x9c45, 0x9f60, 0x28b78, 0xa6fa, 0xa6b1,
        0x9505, 0xc97b, 0x1f081, 0x2e1f6, 0x2c272,
    ] + list(special_pointers)
    for p_offset in two_byte_c6:
        f.seek(p_offset)
        raw = f.read(2)
        if len(raw) == 2:
            p_value = struct.unpack('i', raw + b'\xc6' + b'\x00')[0] - 0xc00000
            if p_offset in special_pointers:
                p_value += 1
            pointer_map.setdefault(p_value, []).append(p_offset)
    two_byte_c7 = [
        0xd551,
    ]
    for p_offset in two_byte_c7:
        f.seek(p_offset)
        raw = f.read(2)
        if len(raw) == 2:
            p_value = struct.unpack('i', raw + b'\xc7' + b'\x00')[0] - 0xc00000
            pointer_map.setdefault(p_value, []).append(p_offset)
    return pointer_map

def _get_text_internal_pointer_map(f, pointer_map):
    #
    for text_segment_start, text_segment_end in (TEXT_SEGMENT_1, TEXT_SEGMENT_2, TEXT_SEGMENT_3):
        f.seek(text_segment_start)
        while f.tell() < text_segment_end:
            byte = f.read(1)
            if byte in (b'\xfb', b'\xfc'):
                f.read(2)
                p_offset = f.tell()
                raw = f.read(3)
                p_value = struct.unpack('i', raw + b'\x00')[0] - 0xc00000
                pointer_map.setdefault(p_value, []).append(p_offset)
            elif byte == b'\xff':
                p_offset = f.tell()
                raw = f.read(3)
                p_value = struct.unpack('i', raw + b'\x00')[0] - 0xc00000
                pointer_map.setdefault(p_value, []).append(p_offset)
    return pointer_map

def seventhsaga_text_segment_dumper(f, dump_path, table, id, block, cur, text_pointer_map, start=0x0, end=0x0):
    f.seek(start)
    while f.tell() < end:
        text_offset = f.tell()
        text = read_text(f, text_offset, end_byte=b'\xf7', cmd_list={b'\xf6': 1, b'\xfb': 5, b'\xfc': 5, b'\xfd': 2, b'\xfe': 2, b'\xff': 3})
        text_decoded = table.decode(text)
        pointers_offsets = text_pointer_map.get(text_offset, [])
        pointers_offsets_str = ';'.join(hex(x) for x in pointers_offsets)
        ref = f'[ID={id} START={hex(text_offset)} END={hex(f.tell() - 1)} POINTERS={pointers_offsets_str}]'
        # dump - db
        insert_text(cur, id, text, text_decoded, text_offset, '', block, ref)
        # dump - txt
        filename = filename = dump_path / 'dump_eng.txt'
        with open(filename, 'a+', encoding='utf-8') as out:
            out.write(f'{ref}\n{text_decoded}\n\n')
        id += 1
    return id

def item_pointers_finder(f):
    pointers = []
    f.seek(0)
    while True:
        byte = f.read(1)
        if not byte:
            break
        current_pos = f.tell()
        if byte in (b'\xc6', b'\xc7'):
            f.seek(-2, os.SEEK_CUR)
            byte_a9 = f.read(1)
            if byte_a9 == b'\xa9':
                f.seek(-5, os.SEEK_CUR)
                byte_85 = f.read(1)
                if byte_85 == b'\x85':
                    f.seek(-3, os.SEEK_CUR)
                    pointers.append([byte, f.tell(), hex(f.tell())])
        f.seek(current_pos)
    for pointer in pointers:
        text_offset = decode_snes_addr(f, pointer[1], base_addr=0xc00000, size=2, bank_byte=pointer[0])
        pointer.append(text_offset)
        pointer.append(hex(text_offset))
    pprint(pointers, indent=4, width=40)
    return pointers

def seventhsaga_text_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = pathlib.Path(args.dump_path)
    db = args.database_file
    table = Table(table1_file)
    conn = sqlite3.connect(db)
    conn.text_factory = str
    cur = conn.cursor()
    shutil.rmtree(dump_path, ignore_errors=True)
    pathlib.Path.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        # item_pointers_finder(f)
        text_pointer_map = {}
        _get_text_pointer_block_pointer_map(f, text_pointer_map)
        _get_text_sparse_pointer_map(f, text_pointer_map)
        _get_text_2byte_pointer_map(f, text_pointer_map)
        _get_text_internal_pointer_map(f, text_pointer_map)
        id = 1
        id = seventhsaga_text_segment_dumper(f, dump_path, table, id, 1, cur, text_pointer_map, TEXT_SEGMENT_1[0], TEXT_SEGMENT_1[1])
        id = seventhsaga_text_segment_dumper(f, dump_path, table, id, 2, cur, text_pointer_map, TEXT_SEGMENT_2[0], TEXT_SEGMENT_2[1])
        id = seventhsaga_text_segment_dumper(f, dump_path, table, id, 3, cur, text_pointer_map, TEXT_SEGMENT_3[0], TEXT_SEGMENT_3[1])
    cur.close()
    conn.commit()
    conn.close()

def seventhsaga_text_inserter(args):
    source_file = args.source_file
    dest_file = args.dest_file
    table2_file = args.table2
    translation_path = args.translation_path
    db = args.database_file
    user_name = args.user
    table = Table(table2_file)
    conn = sqlite3.connect(db)
    conn.text_factory = str
    cur = conn.cursor()
    # insert text into the new location and collect old and new text offsets
    NEW_TEXT_SEGMENT_1_START = NEW_TEXT_SEGMENT_1_END = 0x300000
    text_offset_map = {}
    with open(dest_file, 'r+b') as f:
        f.seek(NEW_TEXT_SEGMENT_1_START)
        rows = select_most_recent_translation(cur, ['1', '2', '3'])
        for row in rows:
            _, _, text_decoded, address, _, translation, _, _, _ = row
            text = translation if translation else text_decoded
            encoded_text = table.encode(text)
            if f.tell() < 0x310000 and f.tell() + len(encoded_text) > 0x30ffff:
                f.seek(0x310000)
            text_offset_map[int(address)] = (f.tell(), False)
            f.write(encoded_text)
            f.write(b'\xf7')
        NEW_TEXT_SEGMENT_1_END = f.tell()
        # repoint pointers in pointer blocks
        text_pointerblock_pointer_map = _get_text_pointer_block_pointer_map(f, {})
        for _, p_addresses in text_pointerblock_pointer_map.items():
            for p_address in p_addresses:
                repoint_3byte_pointer(f, p_address, text_offset_map, 'TEXT - Pointer Block (3 bytes)')
        # repoint sparse pointers
        text_sparse_pointer_map = _get_text_sparse_pointer_map(f, {})
        for _, p_addresses in text_sparse_pointer_map.items():
            for p_address in p_addresses:
                repoint_3byte_pointer(f, p_address, text_offset_map, 'TEXT - Sparse pointer (3 bytes)')
        # repoint two byte pointers
        text_2byte_pointer_map = _get_text_2byte_pointer_map(f, {})
        for _, p_addresses in text_2byte_pointer_map.items():
            for p_address in p_addresses:
                repoint_2byte_pointer(f, p_address, text_offset_map, b'\xc6', 'TEXT (2 bytes)')
        # repoint pointers in text block
        f.seek(NEW_TEXT_SEGMENT_1_START)
        while f.tell() < NEW_TEXT_SEGMENT_1_END:
            byte = f.read(1)
            if byte in (b'\xfb', b'\xfc'):
                f.read(2)
                repoint_3byte_pointer(f, f.tell(), text_offset_map, 'Text Block A')
            elif byte == b'\xff':
                repoint_3byte_pointer(f, f.tell(), text_offset_map, 'Text Block B')
        # repoint other pointers
        write_byte(f, 0x1a2dc, b'\xf0')
        write_byte(f, 0x1a31b, b'\xf0')
        write_byte(f, 0x21898, b'\xf0')
        write_byte(f, 0x21723, b'\xf0')
        # hardcoded internal pointers (not at the beginning of text)
        # repoint_2byte_pointer(f, 0x2b9a5, text_offset_map, b'\xc6') # 0x6e3bf
        # repoint_2byte_pointer(f, 0x2bb64, text_offset_map, b'\xc6') # 0x6e447
    cur.close()
    conn.commit()
    conn.close()

def seventhsaga_gfx_dumper(args):
    source_file = args.source_file
    dump_path = pathlib.Path(args.dump_path)
    with open(source_file, 'rb') as f:
        extract_binary(f, FONT1_BLOCK[0], FONT1_BLOCK[1] - FONT1_BLOCK[0], dump_path / 'gfx_font1.bin')
        extract_binary(f, FONT2_BLOCK[0], FONT2_BLOCK[1] - FONT2_BLOCK[0], dump_path / 'gfx_font2.bin')

def seventhsaga_gfx_inserter(args):
    dest_file = args.dest_file
    translation_path = pathlib.Path(args.translation_path)
    with open(dest_file, 'r+b') as f:
        insert_binary(f, FONT1_BLOCK[0], translation_path / 'gfx_font1.bin', max_length=FONT1_BLOCK[1] - FONT1_BLOCK[0])
        insert_binary(f, FONT2_BLOCK[0], translation_path / 'gfx_font2.bin', max_length=FONT2_BLOCK[1] - FONT2_BLOCK[0])

def seventhsaga_misc_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    table = Table(table1_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        # get pointers
        misc_pointer_map = {}
        _get_misc_2byte_pointer_map(f, misc_pointer_map)
        _get_misc_3byte_pointer_map(f, misc_pointer_map)
        # reading texts
        for i, current_misc_segment in enumerate((MISC_SEGMENT_1, MISC_SEGMENT_2)):
            filename = os.path.join(dump_path, f'misc{i + 1}.csv')
            with open(filename, 'w+', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(['pointer_address', 'text_address', 'text', 'trans'])
                f.seek(current_misc_segment[0])
                while f.tell() <= current_misc_segment[1]:
                    text_address = f.tell()
                    pointer_addresses = misc_pointer_map.get(text_address, [])
                    text = read_text(f, text_address, end_byte=b'\xf7')
                    text_decoded = table.decode(text)
                    fields = [';'.join(hex(x) for x in pointer_addresses), hex(text_address), text_decoded]
                    csv_writer.writerow(fields)

def seventhsaga_misc_inserter(args):
    dest_file = args.dest_file
    table1_file = args.table1
    translation_path = args.translation_path
    table = Table(table1_file)
    # repoint text
    with open(dest_file, 'r+b') as f:
        # reading misc1.csv texts
        translation_file = os.path.join(translation_path, 'misc1.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        # writing misc1.csv texts
        text_offset_map = {}
        t_new_address = 0x350000
        for _, (_, t_address, t_value) in enumerate(translated_texts):
            text_offset_map[t_address] = (t_new_address, False)
            text = table.encode(t_value)
            t_new_address = write_text(f, t_new_address, text, end_byte=b'\xf7')
        # repointing misc1
        misc_2byte_pointer_map = _get_misc_2byte_pointer_map(f, {})
        for _, p_addresses in misc_2byte_pointer_map.items():
            for p_address in p_addresses:
                repoint_2byte_pointer(f, p_address, text_offset_map, b'\xc7', 'MISC (2 bytes)')
        misc_3byte_pointer_map = _get_misc_3byte_pointer_map(f, {})
        for _, p_addresses in misc_3byte_pointer_map.items():
            for p_address in p_addresses:
                repoint_3byte_pointer(f, p_address, text_offset_map, 'MISC (3 bytes)')

def repoint_2byte_pointer(f, pointer_offset, text_offset_map, bank_byte, type=None):
    original_text_offset = decode_snes_addr(f, pointer_offset, base_addr=0xc00000, size=2, bank_byte=bank_byte)
    if pointer_offset in special_pointers:
        original_text_offset += 1
    new_text_offset, _ = text_offset_map.get(original_text_offset, (None, None))
    if new_text_offset:
        new_pointer_value = encode_snes_addr(new_text_offset, base_addr=0xc00000, size=3)
        f.seek(-2, os.SEEK_CUR)
        f.write(new_pointer_value[:-1])
        f.seek(5, os.SEEK_CUR)
        f.write(new_pointer_value[2:3])
    else:
        print(f'Pointer not found - Type: {type} - Text offset: {hex(original_text_offset)} - Pointer offset: {hex(pointer_offset)}')

def repoint_3byte_pointer(f, pointer_offset, text_offset_map, type=None):
    original_text_offset = decode_snes_addr(f, pointer_offset, base_addr=0xc00000, size=3)
    new_text_offset, _ = text_offset_map.get(original_text_offset, (None, None))
    if new_text_offset:
        new_pointer_value = encode_snes_addr(new_text_offset, base_addr=0xc00000, size=3)
        if original_text_offset == 0x65081:
            seek_cur = f.tell()
            f.seek(0x2d8af)
            f.write(b'\xc9' + new_pointer_value[:-1]) # 0xc9 = CMP
            f.seek(seek_cur)
        f.seek(-3, os.SEEK_CUR)
        f.write(new_pointer_value)
    else:
        print(f'Pointer not found - Type: {type} - Text offset: {hex(original_text_offset)} - Pointer offset: {hex(pointer_offset)}')

import argparse
parser = argparse.ArgumentParser()
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
dump_text_parser = subparsers.add_parser('dump_text', help='Execute TEXT DUMP')
dump_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_text_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_text_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
dump_text_parser.set_defaults(func=seventhsaga_text_dumper)
insert_text_parser = subparsers.add_parser('insert_text', help='Execute TEXT INSERTER')
insert_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
insert_text_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_text_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
insert_text_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
insert_text_parser.add_argument('-u', '--user', action='store', dest='user', help='')
insert_text_parser.set_defaults(func=seventhsaga_text_inserter)
dump_gfx_parser = subparsers.add_parser('dump_gfx', help='Execute GFX DUMP')
dump_gfx_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_gfx_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_gfx_parser.set_defaults(func=seventhsaga_gfx_dumper)
insert_gfx_parser = subparsers.add_parser('insert_gfx', help='Execute GFX INSERTER')
insert_gfx_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_gfx_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_gfx_parser.set_defaults(func=seventhsaga_gfx_inserter)
dump_misc_parser = subparsers.add_parser('dump_misc', help='Execute MISC DUMP')
dump_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_misc_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_misc_parser.set_defaults(func=seventhsaga_misc_dumper)
insert_misc_parser = subparsers.add_parser('insert_misc', help='Execute MISC INSERTER')
insert_misc_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Modified table filename')
insert_misc_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_misc_parser.set_defaults(func=seventhsaga_misc_inserter)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
