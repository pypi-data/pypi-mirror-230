import pathlib
import unittest

import pivtestdata as ptd

__this_dir__ = pathlib.Path(__file__).parent


class TestPIVTec(unittest.TestCase):

    def setUp(self) -> None:
        if False:
            ptd.delete_all_downloaded_files()

    def test_pivchallenge_meta(self):
        assert ptd.piv_challenge.pc_1A.meta.pixel_size_mu == (6.7, 6.7)

    def test_pivchallenge(self):
        n_imgs = (2, 12, 4, 16)
        for pc, n_img in zip(
                (ptd.piv_challenge.pc_1A, ptd.piv_challenge.pc_1B, ptd.piv_challenge.pc_1C, ptd.piv_challenge.pc_1E),
                n_imgs):
            assert pc.url == f'https://www.pivchallenge.org/pub/{pc.case}/{pc.case}.zip'
            assert pc.challenge_number == 1
            pc.download()
            assert pc.image_dir == ptd.user_dir / pc.name
            assert len(pc.image_filenames) == n_img

    # take too long to download for a test...
    # def test_pivchallenge_2(self):
    #     n_imgs = (200, 200, 2)
    #     for pc, n_img in zip((ptd.piv_challenge.pc_2A,
    #                           ptd.piv_challenge.pc_2B,
    #                           ptd.piv_challenge.pc_2C), n_imgs):
    #         assert pc.url == f'https://www.pivchallenge.org/pub03/{pc.case}all.zip'
    #         assert pc.challenge_number == 2
    #         pc.download()
    #         assert pc.image_dir == ptd.user_dir / pc.name
    #         assert len(pc.image_filenames) == n_img
