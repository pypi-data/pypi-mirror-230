from .webzip import WebZip


class PivChallenge(WebZip):
    """Web resource as zip file for PIV Challenge datasets"""

    def __init__(self, challenge_number: int, case_name: str, url: str):
        if 'pivchallenge.org' not in url:
            raise ValueError('url must be from pivchallenge.org')
        name = f'piv_challenge/{challenge_number}/{case_name}'
        super().__init__(url=url, name=name)
        self.challenge_number = challenge_number
        self.case = case_name


pc_1A = PivChallenge(challenge_number=1, case_name='A',
                     url='https://www.pivchallenge.org/pub/A/A.zip')
pc_1A.meta.pixel_size_mu = (6.7, 6.7)
pc_1A.meta.dynamic_range_bits = 12
pc_1A.meta.quantum_efficiency = 0.4
pc_1A.meta.full_well_capacity = 25000
pc_1A.meta.readout_noise = 8  # 7 ... 8 @ 12.5 MHz
pc_1A.meta.field_of_view_m = (0.17, 0.14)

pc_1B = PivChallenge(challenge_number=1, case_name='B',
                     url='https://www.pivchallenge.org/pub/B/B.zip')

pc_1C = PivChallenge(challenge_number=1, case_name='C',
                     url='https://www.pivchallenge.org/pub/C/C.zip')
pc_1C.meta.frame_rate = 30  # frames per second
pc_1C.meta.pixel_size_mu = (9.0, 9.0)  # micrometer
pc_1C.meta.sensor_size = (9.072, 9.072)  # mm
pc_1C.meta.dynamic_range_bits = 8

# 35 mm f/2
pc_1C.meta.lens_focal_length = 35  # mm
pc_1C.meta.lens_f_number = 2.0


# There is no case D!

pc_1E = PivChallenge(challenge_number=1, case_name='E',
                     url='https://www.pivchallenge.org/pub/E/E.zip')

pc_2A = PivChallenge(challenge_number=2, case_name='A',
                     url='https://www.pivchallenge.org/pub03/Aall.zip')
pc_2B = PivChallenge(challenge_number=2, case_name='B',
                     url='https://www.pivchallenge.org/pub03/Ball.zip')
pc_2C = PivChallenge(challenge_number=2, case_name='C',
                     url='https://www.pivchallenge.org/pub03/Call.zip')

pc_3A1 = PivChallenge(challenge_number=3, case_name='A1',
                      url='https://www.pivchallenge.org/pub05/A/A1.zip')
pc_3A2 = PivChallenge(challenge_number=3, case_name='A2',
                      url='https://www.pivchallenge.org/pub05/A/A2.zip')
pc_3A3 = PivChallenge(challenge_number=3, case_name='A3',
                      url='https://www.pivchallenge.org/pub05/A/A3.zip')
pc_3A4 = PivChallenge(challenge_number=3, case_name='A4',
                      url='https://www.pivchallenge.org/pub05/A/A4.zip')

pc_3B = PivChallenge(challenge_number=3, case_name='B',
                     url='https://www.pivchallenge.org/pub05/B/B.zip')
pc_3C = PivChallenge(challenge_number=3, case_name='C',
                     url='https://www.pivchallenge.org/pub05/C/C.zip')

pc_4A = PivChallenge(challenge_number=4, case_name='A',
                     url='https://www.pivchallenge.org/pub14/4th_PIV-Challenge_Images_Case_A.zip')
pc_4B = PivChallenge(challenge_number=4, case_name='B',
                     url='https://www.pivchallenge.org/pub14/4th_PIV-Challenge_Images_Case_B.zip')
pc_4C = PivChallenge(challenge_number=4, case_name='C',
                     url='https://www.pivchallenge.org/pub14/4th_PIV-Challenge_Images_Case_C.zip')
pc_4D = PivChallenge(challenge_number=4, case_name='D',
                     url='https://www.pivchallenge.org/pub14/4th_PIV-Challenge_Images_Case_D.zip')
pc_4E = PivChallenge(challenge_number=4, case_name='E',
                     url='https://www.pivchallenge.org/pub14/4th_PIV-Challenge_Images_Case_E.zip')
pc_4F = PivChallenge(challenge_number=4, case_name='F',
                     url='https://www.pivchallenge.org/pub14/4th_PIV-Challenge_Images_Case_F.zip')

all_cases = [pc_1A, pc_1B, pc_1C, pc_1E, pc_2A, pc_2B, pc_2C, pc_3A1, pc_3A2, pc_3A3, pc_3A4, pc_3B, pc_3C,
             pc_4A, pc_4B, pc_4C, pc_4D, pc_4E, pc_4F]
