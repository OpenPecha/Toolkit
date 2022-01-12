from openpecha.formatters.adarsha import parse_pecha
from openpecha.utils import load_yaml
from pathlib import Path


class TestAdarshaParser:

    def test_base_text(self):
        work = ['bonpokangyur', 2426116]
        parse_pecha("./data", work, True)
        with open("./data/expected_base.txt","r") as f:
            base_text = f.read()

        with open(f"./data/{work[0]}/{work[0]}.opf/base/001.txt") as f:
            test_base_text = f.read()

        assert base_text == test_base_text

    def test_layer(self):
        work = ['bonpokangyur', 2426116]
        test_annotation = load_yaml(Path(f"./data/{work[0]}/{work[0]}.opf/layers/001/Pagination.yml"))
        expected_annotation = {
            "fb133094beac4930bdb48168b8bf9a62": {
                "span": {"start": 0, "end": 52},
                "metadata": {"pbId": 2426118, "Img_name": "1-1-1a"},
                "page_info": None,
                "imgnum": 1,
                "reference": "https://files.dharma-treasure.org/degekangyur/degekangyur1-1/1-1-1a.jpg",
            },
            "334216beee434b03bc4b81996a3556a7": {
                "span": {"start": 55, "end": 542},
                "metadata": {"pbId": 2426119, "Img_name": "1-1-1b"},
                "page_info": None,
                "imgnum": 2,
                "reference": "https://files.dharma-treasure.org/degekangyur/degekangyur1-1/1-1-1b.jpg",
            },
            "5eb7bb8070674a7aa4727e808c1ec8a0": {
                "span": {"start": 545, "end": 1055},
                "metadata": {"pbId": 2426120, "Img_name": "1-1-2a"},
                "page_info": None,
                "imgnum": 3,
                "reference": "https://files.dharma-treasure.org/degekangyur/degekangyur1-1/1-1-2a.jpg",
            },
            "c2fe42819f4a45d8b42598d70067acee": {
                "span": {"start": 1058, "end": 1698},
                "metadata": {"pbId": 2426121, "Img_name": "1-1-2b"},
                "page_info": None,
                "imgnum": 4,
                "reference": "https://files.dharma-treasure.org/degekangyur/degekangyur1-1/1-1-2b.jpg",
            },
            "6f44882d8eb4489db283476c0e26c13d": {
                "span": {"start": 1701, "end": 2330},
                "metadata": {"pbId": 2426122, "Img_name": "1-1-3a"},
                "page_info": None,
                "imgnum": 5,
                "reference": "https://files.dharma-treasure.org/degekangyur/degekangyur1-1/1-1-3a.jpg",
            },
            "88f9c623853849088454e82caa551aef": {
                "span": {"start": 2333, "end": 3167},
                "metadata": {"pbId": 2426123, "Img_name": "1-1-3b"},
                "page_info": None,
                "imgnum": 6,
                "reference": "https://files.dharma-treasure.org/degekangyur/degekangyur1-1/1-1-3b.jpg",
            },
            "fa2f4900e0c8430abef9003508774490": {
                "span": {"start": 3170, "end": 4030},
                "metadata": {"pbId": 2426124, "Img_name": "1-1-4a"},
                "page_info": None,
                "imgnum": 7,
                "reference": "https://files.dharma-treasure.org/degekangyur/degekangyur1-1/1-1-4a.jpg",
            },
            "0fbc9696691143ba861e72dbf2d25bfc": {
                "span": {"start": 4033, "end": 4853},
                "metadata": {"pbId": 2426125, "Img_name": "1-1-4b"},
                "page_info": None,
                "imgnum": 8,
                "reference": "https://files.dharma-treasure.org/degekangyur/degekangyur1-1/1-1-4b.jpg",
            },
            "19f61b59585443c08b0bd7592e85a2a9": {
                "span": {"start": 4856, "end": 5695},
                "metadata": {"pbId": 2426126, "Img_name": "1-1-5a"},
                "page_info": None,
                "imgnum": 9,
                "reference": "https://files.dharma-treasure.org/degekangyur/degekangyur1-1/1-1-5a.jpg",
            },
            "236caff851474b1290ac37bfb3307367": {
                "span": {"start": 5698, "end": 6571},
                "metadata": {"pbId": 2426127, "Img_name": "1-1-5b"},
                "page_info": None,
                "imgnum": 10,
                "reference": "https://files.dharma-treasure.org/degekangyur/degekangyur1-1/1-1-5b.jpg",
            },
        }
        for first, second in zip(expected_annotation, test_annotation["annotations"]):
            assert expected_annotation[first] == test_annotation["annotations"][second]





    

