import pathlib
import unittest

import pivtestdata as ptd

__this_dir__ = pathlib.Path(__file__).parent


class TestPIVTec(unittest.TestCase):

    def setUp(self) -> None:
        if False:
            ptd.delete_all_downloaded_files()

    def test_vortex_pair(self):
        vortex_pair = ptd.pivtec.vortex_pair
        self.assertEqual(vortex_pair.name, 'pivtec/vortex_pair')
        self.assertEqual(vortex_pair.url, 'https://www.pivtec.com/download/samples/VortexPairSeq.zip')
        vortex_pair.download()

        self.assertEqual(vortex_pair.image_dir, ptd.user_dir / vortex_pair.name)
        self.assertEqual(80, len(vortex_pair.image_filenames))
        self.assertEqual(1, len(vortex_pair.mask_filenames))
        self.assertEqual(vortex_pair.mask_filename[0].name, 'vp__mask.bmp')
        self.assertEqual(vortex_pair.mask_filenames[0].name, 'vp__mask.bmp')
        self.assertIsInstance(vortex_pair.A[0], pathlib.Path)
        self.assertIsInstance(vortex_pair.B[0], pathlib.Path)

    def test_turbulent_bdry_layer(self):
        turbulent_boundary_layer = ptd.pivtec.turbulent_boundary_layer
        self.assertEqual(turbulent_boundary_layer.name, 'pivtec/turbulent_boundary_layer')
        self.assertEqual(turbulent_boundary_layer.url,
                         'https://www.pivtec.com/download/samples/turbbl_seq.zip')
        turbulent_boundary_layer.download()

        self.assertEqual(turbulent_boundary_layer.image_dir, ptd.user_dir / turbulent_boundary_layer.name)
        self.assertEqual(20, len(turbulent_boundary_layer.image_filenames))
        self.assertEqual(1, len(turbulent_boundary_layer.mask_filenames))

        self.assertIsInstance(turbulent_boundary_layer.A[0], pathlib.Path)
        self.assertIsInstance(turbulent_boundary_layer.B[0], pathlib.Path)
        self.assertEqual(turbulent_boundary_layer.mask_filename[0].name, 'tbl_run3__mask.tif')
        self.assertEqual(turbulent_boundary_layer.mask_filenames[0].name, 'tbl_run3__mask.tif')
