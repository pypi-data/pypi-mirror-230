import re

import pytest

from amazon_short_url.cli import clean


class Test_clean:
    @pytest.mark.parametrize(
        "url",
        [
            'https://www.amazon.com/Kindle-Paperwhite-16-adjustable-Lockscreen/dp/B0B9YZSXB7/ref=sr_1_6?_encoding=UTF8&content-id=amzn1.sym.b9deb6fa-f7f0-4f9b-bfa0-824f28f79589&keywords=Kindle+E-readers&pd_rd_r=f3c5d8cc-fc3f-4500-9550-3cd8b7a9496a&pd_rd_w=Y8Gew&pd_rd_wg=f1HJI&pf_rd_p=b9deb6fa-f7f0-4f9b-bfa0-824f28f79589&pf_rd_r=VKBJ77MN9NTC3ZSBHXQK&qid=1694490408&sr=8-6',
            'https://www.amazon.co.uk/echo-dot-2022/dp/B09B96TG33/?_encoding=UTF8&_ref=dlx_gate_dd_dcl_tlt_6dc83538_dt&pd_rd_w=zfse8&content-id=amzn1.sym.6cd4a383-cdf4-48e7-b879-6a3b5b5d99da&pf_rd_p=6cd4a383-cdf4-48e7-b879-6a3b5b5d99da&pf_rd_r=D3PM20TDWP122F7HZSW6&pd_rd_wg=xNxko&pd_rd_r=723a40e7-3541-4324-940b-f0ad29d2b96f&ref_=pd_gw_unk',
            'https://www.amazon.com.au/dp/B09ZXF8YM4/ref=gw_dt_qc_ch_lav/?_encoding=UTF8&pd_rd_w=T8NPd&content-id=amzn1.sym.7a23e1e0-95d5-45d8-99d3-0a1c1af69ed3&pf_rd_p=7a23e1e0-95d5-45d8-99d3-0a1c1af69ed3&pf_rd_r=TS34TTTMYWP3M9Z4TEPN&pd_rd_wg=9lw2L&pd_rd_r=6bd21133-0c94-421e-b789-a4cdd9e6fb9e&ref_=pd_gw_unk',
            'https://www.amazon.co.jp/%E3%82%BF%E3%82%AB%E3%83%A9%E3%83%88%E3%83%9F%E3%83%BC-TAKARA-TOMY-%E3%83%9D%E3%82%B1%E3%83%83%E3%83%88%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%83%BC-%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%83%BC%E3%83%9C%E3%83%BC%E3%83%AB/dp/B0854VQ912/?_encoding=UTF8&pd_rd_w=VenWw&content-id=amzn1.sym.188d4668-4672-4f36-9ad0-64c3725855d9%3Aamzn1.symc.573c83ff-b207-408b-b0c7-3d92bb6b7d04&pf_rd_p=188d4668-4672-4f36-9ad0-64c3725855d9&pf_rd_r=SPNTT7MGN9265NT8NY3D&pd_rd_wg=RmkNk&pd_rd_r=81bad9c9-3ec4-4817-8674-1e0e9027ce7b&ref_=pd_gw_ci_mcx_mr_hp_atf_m',
        ],
    )
    def test_success(self, url):
        result = clean(url)
        assert isinstance(result, str)
        assert re.match(r'https://www.amazon.co(m|m?\.[a-z]+)/dp/[A-Z0-9]+', result)

    def test_url_none(self):
        with pytest.raises(ValueError):
            clean(None)

    def test_invalid_scheme(self):
        url = 'http://www.amazon.com/Kindle-Paperwhite-16-adjustable-Lockscreen/dp/B0B9YZSXB7/ref=sr_1_6?_encoding=UTF8&content-id=amzn1.sym.b9deb6fa-f7f0-4f9b-bfa0-824f28f79589&keywords=Kindle+E-readers&pd_rd_r=f3c5d8cc-fc3f-4500-9550-3cd8b7a9496a&pd_rd_w=Y8Gew&pd_rd_wg=f1HJI&pf_rd_p=b9deb6fa-f7f0-4f9b-bfa0-824f28f79589&pf_rd_r=VKBJ77MN9NTC3ZSBHXQK&qid=1694490408&sr=8-6'
        with pytest.raises(ValueError) as excinfo:
            clean(url)
        assert excinfo.value.args[0].startswith('Invalid scheme: ')

    def test_invalid_netloc(self):
        url = 'https://www.amazon.xyz/Kindle-Paperwhite-16-adjustable-Lockscreen/dp/B0B9YZSXB7/ref=sr_1_6?_encoding=UTF8&content-id=amzn1.sym.b9deb6fa-f7f0-4f9b-bfa0-824f28f79589&keywords=Kindle+E-readers&pd_rd_r=f3c5d8cc-fc3f-4500-9550-3cd8b7a9496a&pd_rd_w=Y8Gew&pd_rd_wg=f1HJI&pf_rd_p=b9deb6fa-f7f0-4f9b-bfa0-824f28f79589&pf_rd_r=VKBJ77MN9NTC3ZSBHXQK&qid=1694490408&sr=8-6'
        with pytest.raises(ValueError) as excinfo:
            clean(url)
        assert excinfo.value.args[0].startswith('Invalid netloc: ')

    def test_path_unsupported(self):
        url = 'https://www.amazon.com/gp/goldbox?ref_=nav_cs_gb'
        with pytest.raises(ValueError) as excinfo:
            clean(url)
        assert excinfo.value.args[0].startswith('Unsupported path: ')
