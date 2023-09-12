from .webzip import WebZip

vortex_pair = WebZip(name='pivtec/vortex_pair',
                     url='https://www.pivtec.com/download/samples/VortexPairSeq.zip',
                     img_file_pattern=r'vp_\d+[ab].tif', mask_file_pattern='vp__mask*.bmp')
turbulent_boundary_layer = WebZip(name='pivtec/turbulent_boundary_layer',
                                  url='https://www.pivtec.com/download/samples/turbbl_seq.zip')

